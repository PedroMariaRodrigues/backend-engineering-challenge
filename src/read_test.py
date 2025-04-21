import os
import time
import json
import pytest
import inspect
from read import Reader
from datetime import datetime
from values import Event

@pytest.mark.parametrize(
    "line, expected_exception, expected_attrs",
    [
        # 1. Valid event line
        (
            json.dumps({
                "timestamp": "2018-12-26 18:23:19.903159",
                "translation_id": "abc123",
                "source_language": "en",
                "target_language": "pt",
                "client_name": "taxi-eats",
                "event_name": "translation_delivered",
                "nr_words": 100,
                "duration": 5
            }),
            None,
            {
                "timestamp": datetime(2018, 12, 26, 18, 23, 19, 903159),
                "translation_id": "abc123",
                "source_language": "en",
                "target_language": "pt",
                "client_name": "taxi-eats",
                "event_name": "translation_delivered",
                "nr_words": 100,
                "duration": 5
            }
        ),
        # 2. Invalid JSON
        ("{not valid json}", ValueError, None),
        # 3. Missing required key
        (
            json.dumps({
                # omit "translation_id"
                "timestamp": "2018-12-26 18:23:19.903159",
                "source_language": "en",
                "target_language": "pt",
                "client_name": "taxi-eats",
                "event_name": "translation_delivered",
                "nr_words": 100,
                "duration": 5
            }),
            ValueError,
            None
        ),
    ], 
    ids=[
        "valid_event",
        "invalid_json",
        "missing_key"
    ]
)
def test_parse_event(line, expected_exception, expected_attrs):
    """Parametrized tests for parse_event: success and failure modes."""
    reader = Reader(filename="irrelevant.json", keep_reading_live=False)
    if expected_exception:
        with pytest.raises(expected_exception):
            reader.parse_event(line)
    else:
        event = reader.parse_event(line)
        # verify each attribute on the Event
        for attr, val in expected_attrs.items():
            assert getattr(event, attr) == val

@pytest.mark.parametrize(
    "lines, expected_count",
    [
        # 1. Three valid lines: expect 3 yields
        (
            [
                json.dumps({
                    "timestamp": "2018-12-26 18:23:19.903159",
                    "translation_id": "id1",
                    "source_language": "en",
                    "target_language": "pt",
                    "client_name": "c1",
                    "event_name": "delivered",
                    "nr_words": 10,
                    "duration": 1
                }),
                json.dumps({
                    "timestamp": "2018-12-26 18:23:19.903159",
                    "translation_id": "id2",
                    "source_language": "en",
                    "target_language": "pt",
                    "client_name": "c2",
                    "event_name": "delivered",
                    "nr_words": 20,
                    "duration": 2
                }),
                json.dumps({
                    "timestamp": "2018-12-26 18:23:19.903159",
                    "translation_id": "id3",
                    "source_language": "en",
                    "target_language": "pt",
                    "client_name": "c3",
                    "event_name": "delivered",
                    "nr_words": 30,
                    "duration": 3
                }),
            ],
            3
        ),
        # 2. Empty file: expect 0 yields
        ([], 0),
    ],
    ids=["valid_3_events",
         "empty_file_no_events"
         ]
)
def test_read_existing_events(tmp_path, lines, expected_count):
    """
    Parametrized tests for read_existing_events:
    - write `lines` to a temp file
    - instantiate Reader with keep_reading_live=False
    - collect events and verify count matches expected_count
    """
    # prepare temp file
    file_path = tmp_path / "events.json"
    file_path.write_text("\n".join(lines) + ("\n" if lines else ""))

    reader = Reader(str(file_path), keep_reading_live=False)
    collected = list(reader.read_existing_events())
    
    assert len(collected) == expected_count

def make_event_dict():
    return {
        "timestamp": "2025-04-21 10:00:00",
        "translation_id": "123",
        "source_language": "en",
        "target_language": "fr",
        "client_name": "TestClient",
        "event_name": "TranslateFinished",
        "nr_words": 100,
        "duration": 1.23
    }

def test_parse_event_missing_key():
    """
    Test parse_event with missing key in JSON string.
    """
    reader = Reader("dummy", False)
    data = make_event_dict()
    del data["timestamp"]
    line = json.dumps(data)
    with pytest.raises(ValueError) as exc:
        reader.parse_event(line)
    assert "Missing key" in str(exc.value)

def test_read_existing_events_valid(tmp_path):
    """
    Test for read existing events with invalid json
    """
    file = tmp_path / "events.log"
    # Prepare lines: valid, empty, invalid JSON, missing key, valid
    data1 = make_event_dict()
    data2 = make_event_dict()
    del data2["client_name"]
    lines = [json.dumps(data1), "", "{bad json}", json.dumps(data2), json.dumps(make_event_dict())]
    file.write_text("\n".join(lines) + "\n")

    reader = Reader(str(file), keep_reading_live=True)
    events = list(reader.read_existing_events())
    # Should yield only valid events (first and last)
    assert len(events) == 2
    assert events[0].translation_id == data1["translation_id"]
    assert events[1].translation_id == make_event_dict()["translation_id"]
    # last_position set to file size
    assert reader.last_position == os.path.getsize(str(file))

def test_read_existing_events_file_not_found():
    """
    Test file not found
    """
    reader = Reader("nonexistent.log", False)
    with pytest.raises(SystemExit) as exc:
        list(reader.read_existing_events())
    assert exc.value.code == 1

def test_monitor_live_events_not_live():
    """
    When keep_reading_live is False, monitor_live_events
    returns a generator that immediately stops.
    """
    reader = Reader("dummy.log", False)
    gen = reader.monitor_live_events()

    # 1) It must be a generator
    assert inspect.isgenerator(gen), "Expected a generator, got %r" % (gen,)

    # 2) And it must be empty—next() raises StopIteration immediately
    with pytest.raises(StopIteration):
        next(gen)

def test_monitor_live_events_live(tmp_path, monkeypatch):
    """
    Test monitor live event working
    """
    # Create file and initial content
    file = tmp_path / "live.log"
    file.write_text("")

    reader = Reader(str(file), keep_reading_live=True)
    # Pre-write a new event before starting monitoring
    ev = make_event_dict()
    line = json.dumps(ev) + "\n"
    with open(file, "a") as f:
        f.write(line)

    # Monkeypatch sleep to stop after one loop: raise SystemExit
    monkeypatch.setattr(time, "sleep", lambda _: (_ for _ in ()).throw(SystemExit()))

    gen = reader.monitor_live_events()
    # Collect first yielded event
    event = next(gen)
    assert isinstance(event, Event)
    assert event.translation_id == ev["translation_id"]
    # Next iteration should cause SystemExit
    with pytest.raises(SystemExit):
        next(gen)

def test_monitor_handles_bad_json(tmp_path, monkeypatch, capsys):
    """
    Test monitor_live_events with bad JSON
    """
    file = tmp_path / "bad.log"
    file.write_text("{bad json}\n")

    reader = Reader(str(file), keep_reading_live=True)

    monkeypatch.setattr(time, "sleep", lambda _: (_ for _ in ()).throw(SystemExit()))

    with pytest.raises(SystemExit):
        next(reader.monitor_live_events())

    captured = capsys.readouterr()
    assert "Error decoding JSON" in captured.out


def test_monitor_handles_missing_file(monkeypatch, capsys):
    """
    Test monitor_live_events with missing file
    """
    reader = Reader("does_not_exist.log", keep_reading_live=True)

    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)
        raise SystemExit()

    monkeypatch.setattr(time, "sleep", fake_sleep)

    with pytest.raises(SystemExit):
        next(reader.monitor_live_events())

    captured = capsys.readouterr()
    assert "File not found" in captured.out
    assert 1 in slept

def test_monitor_catches_generic_exception(monkeypatch, capsys):
    """
    Test monitor_live_events handles generic exceptions
    """
    reader = Reader("dummy.log", True)

    def boom_open(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("builtins.open", boom_open)

    with pytest.raises(SystemExit) as exc:
        next(reader.monitor_live_events())

    captured = capsys.readouterr()
    assert "Error monitoring file" in captured.out
    assert exc.value.code == 1