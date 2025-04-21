import pytest
from types import SimpleNamespace
from metrics_ import Metrics

@pytest.mark.parametrize(
    "events, expected_ma",
    [
        # Empty list -> average 0
        ([], 0),
        # Single event
        ([SimpleNamespace(duration=10)], 10),
        # Multiple events with integer durations
        ([SimpleNamespace(duration=d) for d in [1, 2, 3]], 2),
        # Multiple events with mixed durations
        ([SimpleNamespace(duration=d) for d in [0, 5, 10]], pytest.approx(5.0)),
        # Durations with floats
        ([SimpleNamespace(duration=d) for d in [1.5, 2.5, 3.0]], pytest.approx((1.5 + 2.5 + 3.0) / 3)),
    ]
)
def test_moving_average(events, expected_ma):
    """
    Test metrics.moving_average with various lists of events.
    """
    result = Metrics.moving_average(events)
    assert result == expected_ma
