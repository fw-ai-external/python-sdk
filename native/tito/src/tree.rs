// SPDX-License-Identifier: Apache-2.0

use pyo3::{
    prelude::*,
    types::{PyDict, PyTuple},
};

type Parent<'py> = (Option<Bound<'py, PyAny>>, Option<Bound<'py, PyAny>>, String);

#[pyfunction]
#[pyo3(signature = (latest, checkpoints, messages, contract))]
pub(crate) fn select_parent<'py>(
    latest: Option<Bound<'py, PyAny>>,
    checkpoints: &Bound<'py, PyDict>,
    messages: &Bound<'py, PyTuple>,
    contract: &str,
) -> PyResult<Parent<'py>> {
    for depth in (1..=messages.len()).rev() {
        let Some(candidates) = checkpoints.get_item(depth)? else {
            continue;
        };
        let response = messages.get_item(depth - 1)?;
        if !response.call_method1("get", ("role",))?.eq("assistant")? {
            continue;
        }
        let mut matched = None;
        for row in candidates.try_iter()? {
            let (segment, turn): (Bound<'_, PyAny>, Bound<'_, PyAny>) = row?.extract()?;
            if !response.eq(turn.getattr("assistant")?.getattr("message")?)? {
                continue;
            }
            let history = turn
                .getattr("request")?
                .getattr("messages")?
                .cast_into::<PyTuple>()?;
            if history.len() != depth - 1
                || common_prefix_tokens(&history, messages)? != history.len()
            {
                continue;
            }
            if matched.is_some() {
                return Ok((None, None, "ambiguous_parent".into()));
            }
            matched = Some((segment, turn));
        }
        if let Some((segment, turn)) = matched {
            if turn.getattr("finish_reason")?.eq("length")? {
                return Ok((None, Some(turn), "length_truncation".into()));
            }
            if !segment.getattr("render_contract_id")?.eq(contract)? {
                return Ok((None, Some(turn), "contract_change".into()));
            }
            return Ok((Some(segment), Some(turn), String::new()));
        }
    }
    let Some(latest) = latest else {
        return Ok((None, None, "initial".into()));
    };
    let reason = if latest.getattr("render_contract_id")?.eq(contract)? {
        "history_rewrite"
    } else {
        "contract_change"
    };
    Ok((None, None, reason.into()))
}

#[pyfunction]
pub(crate) fn history_rewrite(
    stored: &Bound<'_, PyTuple>,
    incoming: &Bound<'_, PyTuple>,
) -> PyResult<Option<&'static str>> {
    let matched = common_prefix_tokens(stored, incoming)?;
    Ok(if matched == stored.len() {
        None
    } else if matched == incoming.len() {
        Some("truncated")
    } else if matched + 1 == stored.len() {
        Some("assistant_roundtrip")
    } else {
        Some("prior_context")
    })
}

#[pyfunction]
pub(crate) fn common_prefix_tokens(
    left: &Bound<'_, PyTuple>,
    right: &Bound<'_, PyTuple>,
) -> PyResult<usize> {
    for (index, (a, b)) in left.iter().zip(right.iter()).enumerate() {
        if !(a.is(&b) || a.eq(&b)?) {
            return Ok(index);
        }
    }
    Ok(left.len().min(right.len()))
}

#[pyfunction]
pub(crate) fn fork_reason(
    is_tip: bool,
    is_latest: bool,
    prefix_match_tokens: Option<usize>,
    checkpoint_length: usize,
) -> Option<&'static str> {
    if !is_latest && prefix_match_tokens != Some(checkpoint_length) {
        Some("branch_token_drift")
    } else if !is_tip {
        Some("fork")
    } else {
        None
    }
}

#[pyfunction]
pub(crate) fn full_history_alignment(
    matches: usize,
    checkpoint_len: usize,
    response_start: usize,
    prompt_len: usize,
    max_masked_tokens: &Bound<'_, PyAny>,
) -> PyResult<(&'static str, usize)> {
    if matches == checkpoint_len {
        return Ok(("append", 0));
    }
    let masked = prompt_len.saturating_sub(response_start);
    if matches >= response_start
        && masked
            .into_pyobject(max_masked_tokens.py())?
            .lt(max_masked_tokens)?
    {
        Ok(("realign", masked))
    } else {
        Ok(("new_segment", 0))
    }
}
