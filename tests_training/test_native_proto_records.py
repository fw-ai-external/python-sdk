"""Binary results preserve each record's own tensor metadata."""

import numpy as np
import pytest

from fireworks.training.sdk._core.proto import tinker_public_pb2 as proto
from fireworks.training.sdk._core.proto.response_conv import deserialize_forward_backward_output


@pytest.mark.parametrize("reverse", [False, True])
def test_binary_result_records_can_have_different_shapes_and_dtypes(reverse):
    arrays = [
        np.arange(8, dtype=np.float32).reshape(2, 2, 2),
        (2**40 + np.arange(12, dtype=np.int64)).reshape(2, 2, 3),
    ]
    if reverse:
        arrays.reverse()
    response = proto.ForwardBackwardOutput(loss_fn_output_type="ArrayRecord", metrics={"loss:sum": 3})
    for values in arrays:
        record = response.loss_fn_outputs.add(num_datums=len(values))
        record.fields["values"].CopyFrom(
            proto.BatchedTensor(
                data=values.tobytes(),
                offsets=(np.arange(len(values) + 1, dtype=np.int64) * values[0].nbytes).tobytes(),
                dtype=proto.DTYPE_FLOAT32 if values.dtype == np.float32 else proto.DTYPE_INT64,
                trailing_shape=list(values.shape[2:]),
            )
        )

    result = deserialize_forward_backward_output(response.SerializeToString())
    assert result.metrics == {"loss:sum": 3}
    assert len(result.loss_fn_outputs) == 4
    for output, expected in zip(result.loss_fn_outputs, [value for batch in arrays for value in batch], strict=True):
        actual = output["values"]
        assert actual.shape == list(expected.shape)
        assert actual.to_numpy().dtype == expected.dtype
        np.testing.assert_array_equal(actual.to_numpy(), expected)
