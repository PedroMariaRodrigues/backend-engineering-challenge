import pytest
from types import SimpleNamespace
from metrics_ import MovingAverage, Maximum

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
    ],
    ids=[
        "empty_list",
        "single_event",
        "multiple_integer_durations",
        "multiple_mixed_durations",
        "multiple_float_durations",
    ]
)
def test_moving_average(events, expected_ma):
    """
    Test moving_average with various lists of events.
    """
    ma = MovingAverage()
    result = ma.compute(events)
    assert result == expected_ma
    
    
@pytest.mark.parametrize(
    "events, expected_max",
    [
        # Empty list -> maximum 0
        ([], 0),
        # Single event
        ([SimpleNamespace(duration=10)], 10),
        # Multiple events with integer durations
        ([SimpleNamespace(duration=d) for d in [1, 2, 3]], 3),
        # Multiple events with mixed durations
        ([SimpleNamespace(duration=d) for d in [0, 5, 10]], 10),
        # Durations with floats
        ([SimpleNamespace(duration=d) for d in [1.5, 2.5, 3.0]], 3.0),
    ], 
    ids=[
        "empty_list",
        "single_event",
        "multiple_integer_durations",
        "multiple_mixed_durations",
        "multiple_float_durations",
    ]
)
def test_maximum(events, expected_max):
    """
    Test maximum with various lists of events.
    """
    max_metric = Maximum() 
    result = max_metric.compute(events)
    assert result == expected_max
