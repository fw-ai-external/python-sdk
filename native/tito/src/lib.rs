// SPDX-License-Identifier: Apache-2.0

use flate2::{write::ZlibEncoder, Compression};
use pyo3::{
    exceptions::PyValueError,
    prelude::*,
    types::{PyBool, PyBytes, PyDict, PyFloat, PyInt, PyList, PyString, PyTuple},
};
use std::{collections::HashSet, io::Write};

mod lineage;

const BUFFER_SIZE: usize = 64 * 1024;

struct Writer<'py, F> {
    encoder: Bound<'py, PyAny>,
    sink: F,
    pending: Vec<u8>,
    active: HashSet<usize>,
}

impl<'py, F: FnMut(&[u8]) -> PyResult<()>> Writer<'py, F> {
    fn flush(&mut self) -> PyResult<()> {
        if !self.pending.is_empty() {
            (self.sink)(&self.pending)?;
            self.pending.clear();
        }
        Ok(())
    }

    fn write(&mut self, data: &[u8]) -> PyResult<()> {
        if self.pending.len() + data.len() >= BUFFER_SIZE {
            self.flush()?;
        }
        if data.len() >= BUFFER_SIZE {
            (self.sink)(data)
        } else {
            self.pending.extend_from_slice(data);
            Ok(())
        }
    }

    fn python_json(&mut self, value: &Bound<'py, PyAny>) -> PyResult<()> {
        let json = self.encoder.call1((value,))?.cast_into::<PyString>()?;
        self.write(json.to_cow()?.as_bytes())
    }

    fn dictionary(&mut self, dict: &Bound<'py, PyDict>, depth: usize) -> PyResult<()> {
        let mut fields = Vec::with_capacity(dict.len());
        for (key, value) in dict.iter() {
            let Ok(key) = key.cast_exact::<PyString>() else {
                return self.python_json(dict.as_any());
            };
            // UTF-8 preserves Python's Unicode code-point sort order.
            fields.push((key.to_cow()?.into_owned(), key.to_owned(), value));
        }
        fields.sort_unstable_by(|a, b| a.0.cmp(&b.0));
        self.write(b"{")?;
        for (index, (_, key, value)) in fields.into_iter().enumerate() {
            if index != 0 {
                self.write(b",")?;
            }
            self.python_json(key.as_any())?;
            self.write(b":")?;
            self.value(&value, depth + 1)?;
        }
        self.write(b"}")
    }

    fn sequence(
        &mut self,
        items: impl Iterator<Item = Bound<'py, PyAny>>,
        depth: usize,
    ) -> PyResult<()> {
        self.write(b"[")?;
        for (index, item) in items.enumerate() {
            if index != 0 {
                self.write(b",")?;
            }
            self.value(&item, depth + 1)?;
        }
        self.write(b"]")
    }

    fn value(&mut self, value: &Bound<'py, PyAny>, depth: usize) -> PyResult<()> {
        if let Ok(integer) = value.cast_exact::<PyInt>() {
            if let Ok(integer) = integer.extract::<i64>() {
                return self.write(itoa::Buffer::new().format(integer).as_bytes());
            }
            return self.python_json(value);
        }
        if value.is_none() {
            return self.write(b"null");
        }
        if value.is_exact_instance_of::<PyBool>() {
            return self.write(if value.is_truthy()? {
                b"true"
            } else {
                b"false"
            });
        }
        if value.is_exact_instance_of::<PyFloat>() && value.extract::<f64>()?.is_finite() {
            // CPython's JSON encoder uses repr for finite built-in floats.
            return self.write(value.repr()?.to_cow()?.as_bytes());
        }
        if depth >= 128 {
            return self.python_json(value);
        }
        let dict = value.cast_exact::<PyDict>().ok();
        let tuple = value.cast_exact::<PyTuple>().ok();
        let list = value.cast_exact::<PyList>().ok();
        if dict.is_none() && tuple.is_none() && list.is_none() {
            return self.python_json(value);
        }

        let identity = value.as_ptr() as usize;
        if !self.active.insert(identity) {
            return Err(PyValueError::new_err("Circular reference detected"));
        }
        let result = if let Some(dict) = dict {
            self.dictionary(dict, depth)
        } else if let Some(tuple) = tuple {
            self.sequence(tuple.iter(), depth)
        } else {
            self.sequence(list.expect("checked container kind").iter(), depth)
        };
        self.active.remove(&identity);
        result
    }
}

fn write_json<'py>(
    value: &Bound<'py, PyAny>,
    encoder: Bound<'py, PyAny>,
    sink: impl FnMut(&[u8]) -> PyResult<()>,
) -> PyResult<()> {
    let mut writer = Writer {
        encoder,
        sink,
        pending: Vec::with_capacity(BUFFER_SIZE),
        active: HashSet::new(),
    };
    writer.value(value, 0)?;
    writer.flush()
}

#[pyfunction]
fn encode_json<'py>(
    value: &Bound<'py, PyAny>,
    encoder: Bound<'py, PyAny>,
    write: Bound<'py, PyAny>,
) -> PyResult<()> {
    write_json(value, encoder, |data| {
        write.call1((PyBytes::new(value.py(), data),))?;
        Ok(())
    })
}

#[pyfunction]
fn compress_json<'py>(
    value: &Bound<'py, PyAny>,
    encoder: Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyBytes>> {
    let py = value.py();
    let mut compressor = ZlibEncoder::new(Vec::new(), Compression::new(6));
    write_json(value, encoder, |data| {
        py.detach(|| compressor.write_all(data))?;
        Ok(())
    })?;
    let output = py.detach(move || compressor.finish())?;
    Ok(PyBytes::new(py, &output))
}

// The offset counts Unicode code points, as in Python's JSON decoder.
fn scan_json_chars(
    mut characters: impl Iterator<Item = char>,
    mut at: usize,
    mut depth: i64,
    mut quoted: bool,
) -> (usize, i64, bool, bool) {
    while let Some(character) = characters.next() {
        at += 1;
        if quoted {
            match character {
                '\\' => {
                    characters.next();
                    // A trailing backslash also skips the first character of the next block.
                    at += 1;
                }
                '"' => quoted = false,
                _ => (),
            }
        } else {
            match character {
                '[' | '{' => depth += 1,
                ']' | '}' => {
                    depth -= 1;
                    if depth == 0 {
                        return (at, depth, quoted, true);
                    }
                }
                '"' => quoted = true,
                _ => (),
            }
        }
    }
    (at, depth, quoted, false)
}

#[pyfunction]
fn scan_json_composite(
    text: &Bound<'_, PyString>,
    at: usize,
    depth: i64,
    quoted: bool,
    ascii: bool,
) -> PyResult<(usize, i64, bool, bool)> {
    let text = text.to_cow()?;
    if ascii {
        let suffix = text.as_bytes().get(at..).unwrap_or_default();
        Ok(scan_json_chars(
            suffix.iter().copied().map(char::from),
            at,
            depth,
            quoted,
        ))
    } else {
        Ok(scan_json_chars(text.chars().skip(at), at, depth, quoted))
    }
}

#[pymodule(gil_used = true)]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(encode_json, module)?)?;
    module.add_function(wrap_pyfunction!(compress_json, module)?)?;
    module.add_function(wrap_pyfunction!(scan_json_composite, module)?)?;
    module.add_function(wrap_pyfunction!(lineage::select_parent, module)?)?;
    module.add_function(wrap_pyfunction!(lineage::history_rewrite, module)?)?;
    module.add_function(wrap_pyfunction!(lineage::common_prefix_tokens, module)?)?;
    module.add_function(wrap_pyfunction!(lineage::fork_reason, module)?)?;
    module.add_function(wrap_pyfunction!(lineage::full_history_alignment, module)?)
}
