import pytest
from process import Processor, round_up_minute
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch
from metrics_ import MovingAverage, Maximum
from values import Event
from collections import deque

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
    """Test the function roun up"""
    assert round_up_minute(timestamp) == expected


def test_initial_process_returns_zero(mock_event):
    """Test that the initial process returns zero"""
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 1)
    event = mock_event(ts, 10)
    result = p.process(event, metric="moving_average")
    assert result == {"date": "2025-04-20 12:00:00", "average_delivery_time": 0}
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 1)
    event = mock_event(ts, 10)
    result = p.process(event, metric="maximum")
    assert result == {"date": "2025-04-20 12:00:00", "max_delivery_time": 0}

def test_same_minute_returns_none(mock_event):
    """Test that the process returns None when the event is in the same minute"""
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 1)
    p.process(mock_event(ts, 10), metric="moving_average")
    result = p.process(mock_event(ts + timedelta(seconds=30), 20), metric="moving_average")
    p.process(mock_event(ts, 10), metric="maximum")
    result1 = p.process(mock_event(ts + timedelta(seconds=30), 20), metric="maximum")
    assert result is None
    assert result1 is None


def test_cross_minute_triggers_output(mock_event):
    """Test that crossing a minute boundary triggers output generation"""
    p = Processor(window_size=10)
    base_ts = datetime(2025, 4, 20, 12, 0, 30)
    p.process(mock_event(base_ts, 10), metric="moving_average")
    result = p.process(mock_event(base_ts + timedelta(minutes=1, seconds=5), 20), metric="moving_average")
    assert isinstance(result, dict)
    assert "date" in result and "average_delivery_time" in result
    p = Processor(window_size=10)
    base_ts = datetime(2025, 4, 20, 12, 0, 30)
    p.process(mock_event(base_ts, 10), metric="maximum")
    result = p.process(mock_event(base_ts + timedelta(minutes=1, seconds=5), 20), metric="maximum")
    assert isinstance(result, dict)
    assert "date" in result and "max_delivery_time" in result


def test_multiple_minute_gap(mock_event):
    """Test that multiple minute gaps generate multiple outputs"""
    p = Processor(window_size=10)
    base_ts = datetime(2025, 4, 20, 12, 0, 30)
    p.process(mock_event(base_ts, 10), metric="moving_average")
    result = p.process(mock_event(base_ts + timedelta(minutes=3), 20), metric="moving_average")
    assert isinstance(result, list)
    assert len(result) == 3
    for r in result:
        assert "date" in r and "average_delivery_time" in r
        
    p = Processor(window_size=10)
    base_ts = datetime(2025, 4, 20, 12, 0, 30)
    p.process(mock_event(base_ts, 10), metric="maximum")
    result1 = p.process(mock_event(base_ts + timedelta(minutes=3), 20), metric="maximum")
    assert isinstance(result1, list)
    assert len(result1) == 3
    for r in result1:
        assert "date" in r and "max_delivery_time" in r



def test_finalize_returns_last_minute_output(mock_event):
    """Test that finalize returns last minute output"""
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 0)
    p.process(mock_event(ts, 10), metric="moving_average")
    result = p.finalize(metric="moving_average")
    assert result["date"] == "2025-04-20 12:01:00"
    assert "average_delivery_time" in result
    
    p = Processor(window_size=10)
    ts = datetime(2025, 4, 20, 12, 0, 0)
    p.process(mock_event(ts, 10), metric="maximum")
    result1 = p.finalize(metric="maximum")
    assert result1["date"] == "2025-04-20 12:01:00"
    assert "max_delivery_time" in result1


def test_unsupported_metric_raises(mock_event):
    """Test that unsuported metric raise ValueError"""
    p = Processor(window_size=5)
    ts = datetime(2025, 4, 20, 12, 0, 0)
    p.process(mock_event(ts, 10), metric="moving_average")
    with pytest.raises(ValueError, match="Unsuported metric"):
        p.generate_output_for_minute(ts, metric="unknown")


def test_get_metrics():
    """Test that get_metrics returns the correct metric class instances"""
    processor = Processor(window_size=5)
    metric = processor.get_metrics("moving_average")
    assert isinstance(metric, MovingAverage)
    
    metric = processor.get_metrics("maximum")
    assert isinstance(metric, Maximum)
    
    metric = processor.get_metrics("unknown_metric")
    assert metric is None

def test_process_same_minute_returns_none():
    """Test that process returns None when an event is in the same minute as current_minute"""
    processor = Processor(window_size=5)
    
    initial_time = datetime(2025, 4, 21, 12, 0, 0)
    processor.event_current_minute = initial_time
    event = Event(timestamp=initial_time - timedelta(seconds=30), translation_id="X", source_language="X", target_language="X", client_name="X", event_name="X", nr_words=10, duration=5)
    result = processor.process(event, "moving_average")
    assert result is None
    assert event in processor.moving_window
    
    processor = Processor(window_size=5)
    initial_time = datetime(2025, 4, 21, 12, 0, 0)
    processor.event_current_minute = initial_time  
    event1 = Event(timestamp=initial_time - timedelta(seconds=30), translation_id="X", source_language="X", target_language="X", client_name="X", event_name="X", nr_words=10, duration=5)
    result1 = processor.process(event1, "maximum")
    assert result1 is None
    assert event1 in processor.moving_window

def test_process_return_logic():
    """Test the return logic for outputs in the process method"""
    processor = Processor(window_size=5)
    
    # Set up the initial state with a specific current minute
    initial_time = datetime(2025, 4, 21, 12, 0, 0)
    
    # Test case 1: First event initializes current_minute and returns output
    # Before the first event, event_current_minute should be None
    processor.event_current_minute = None
    processor.moving_window = deque()
    
    first_event = Event(
        timestamp=initial_time - timedelta(seconds=30),  # Just before initial_time
        translation_id="X", 
        source_language="X", 
        target_language="X", 
        client_name="X", 
        event_name="X", 
        nr_words=10, 
        duration=5
    )
    
    # Mock generate_output to return predictable output
    processor.generate_output_for_minute = Mock()
    
    # First event should return an output, not None
    result1 = processor.process(first_event, "moving_average")
    assert result1 is not None
    
    # Test case 2: Event in same minute returns None
    # Now set event_current_minute to initial_time
    processor.generate_output_for_minute.reset_mock()
    processor.event_current_minute = initial_time
    
    same_minute_event = Event(
        timestamp=initial_time - timedelta(seconds=15),
        translation_id="X", 
        source_language="X", 
        target_language="X", 
        client_name="X", 
        event_name="X", 
        nr_words=10, 
        duration=7
    )
    
    # When event is in same minute, should return None and not call generate_output
    result2 = processor.process(same_minute_event, "moving_average")
    assert result2 is None
    processor.generate_output_for_minute.assert_not_called()
    
    # Test case 3: Single minute gap
    processor.generate_output_for_minute.reset_mock()
    processor.generate_output_for_minute.return_value = {"minute": "output"}
    
    next_minute_event = Event(
        timestamp=initial_time + timedelta(minutes=1, seconds=-15),
        translation_id="X", 
        source_language="X", 
        target_language="X", 
        client_name="X", 
        event_name="X", 
        nr_words=10, 
        duration=8
    )
    
    result3 = processor.process(next_minute_event, "moving_average")
    assert result3 == {"minute": "output"}  # Single output directly returned
    processor.generate_output_for_minute.assert_called_once()
    
    # Test case 4: Multiple minute gap
    processor.generate_output_for_minute.reset_mock()
    processor.generate_output_for_minute.return_value = {"minute": "output"}
    
    # Create an event three minutes later (2 minute gap)
    future_event = Event(
        timestamp=initial_time + timedelta(minutes=3, seconds=-15),
        translation_id="X", 
        source_language="X", 
        target_language="X", 
        client_name="X", 
        event_name="X", 
        nr_words=10, 
        duration=9
    )
    
    result4 = processor.process(future_event, "moving_average")
    assert isinstance(result4, list)
    assert len(result4) == 2  # Two outputs for the 2-minute gap
    assert processor.generate_output_for_minute.call_count == 2

def test_generate_output_calls_popleft():
    """Test that generate_output_for_minute calls popleft_moving_window"""
    processor = Processor(window_size=5)
    
    # Mock the popleft_moving_window method
    processor.popleft_moving_window = Mock()
    
    # Call generate_output_for_minute
    minute = datetime(2025, 4, 21, 12, 0, 0)
    processor.generate_output_for_minute(minute, "moving_average")
    
    # Assert that popleft_moving_window was called with the minute
    processor.popleft_moving_window.assert_called_once_with(minute)


def test_process_increments_current_minute():
    """Test that process increments event_current_minute correctly"""
    processor = Processor(window_size=5)
    
    # Set initial current minute
    initial_time = datetime(2025, 4, 21, 12, 0, 0)
    processor.event_current_minute = initial_time
    
    # Mock generate_output_for_minute to avoid side effects
    processor.generate_output_for_minute = Mock(return_value={"minute": "output"})
    
    # Create an event that is 2 minutes in the future
    future_time = initial_time + timedelta(minutes=2)
    future_event = Event(
        timestamp=future_time,
        translation_id="X", 
        source_language="X", 
        target_language="X", 
        client_name="X", 
        event_name="X", 
        nr_words=10, 
        duration=5
    )
    
    # Process the event
    processor.process(future_event, "moving_average")
    
    # Assert that current_minute was incremented to match the event's minute
    # The current_minute will be incremented to round_up_minute(future_time)
    expected_new_minute = round_up_minute(future_time)
    assert processor.event_current_minute == expected_new_minute
