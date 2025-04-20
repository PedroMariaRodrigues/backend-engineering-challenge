import pytest
from process import Processor, round_up_minute
from datetime import datetime, timedelta
from types import SimpleNamespace

@pytest.fixture
def mock_event():
    return lambda ts, duration: SimpleNamespace(timestamp=ts, duration=duration)

@pytest.mark.parametrize(
    "timestamp, expected",
    [
        (datetime(2025, 4, 20, 12, 34, 21), datetime(2025, 4, 20, 12, 35)),
        (datetime(2025, 4, 20, 23, 59, 59), datetime(2025, 4, 21, 0, 0)),
    ]
)
def test_round_up_minute(timestamp, expected):
    assert round_up_minute(timestamp) == expected


def test_initial_process_returns_zero_ma(mock_event):
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 1)
    event = mock_event(ts, 10)
    result = p.process(event, metric="moving_average")
    assert result == {"date": "2025-04-20 12:00:00", "average_delivery_time": 0}


def test_same_minute_returns_none(mock_event):
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 1)
    p.process(mock_event(ts, 10), metric="moving_average")
    result = p.process(mock_event(ts + timedelta(seconds=30), 20), metric="moving_average")
    assert result is None


def test_cross_minute_triggers_output(mock_event):
    p = Processor(window_size=10)
    base_ts = datetime(2025, 4, 20, 12, 0, 30)
    p.process(mock_event(base_ts, 10), metric="moving_average")
    result = p.process(mock_event(base_ts + timedelta(minutes=1, seconds=5), 20), metric="moving_average")
    assert isinstance(result, dict)
    assert "date" in result and "average_delivery_time" in result


def test_multiple_minute_gap(mock_event):
    p = Processor(window_size=10)
    base_ts = datetime(2025, 4, 20, 12, 0, 30)
    p.process(mock_event(base_ts, 10), metric="moving_average")
    result = p.process(mock_event(base_ts + timedelta(minutes=3), 20), metric="moving_average")
    assert isinstance(result, list)
    assert len(result) == 3
    for r in result:
        assert "date" in r and "average_delivery_time" in r


def test_finalize_returns_last_minute_output(mock_event):
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 0)
    p.process(mock_event(ts, 10), metric="moving_average")
    result = p.finalize(metric="moving_average")
    assert result["date"] == "2025-04-20 12:01:00"
    assert "average_delivery_time" in result


def test_unsupported_metric_raises(mock_event):
    p = Processor(window_size=5)
    ts = datetime(2025, 4, 20, 12, 0, 0)
    p.process(mock_event(ts, 10), metric="moving_average")
    with pytest.raises(ValueError, match="Unsuported metric"):
        p.generate_output_for_minute(ts, metric="unknown")
