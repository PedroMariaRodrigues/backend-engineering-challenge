import json
import pytest
from read import Reader
import pandas as pd

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
                "timestamp": pd.to_datetime("2018-12-26 18:23:19.903159"),
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
    file_path = tmp_path / "events.jsonl"
    file_path.write_text("\n".join(lines) + ("\n" if lines else ""))

    reader = Reader(str(file_path), keep_reading_live=False)
    collected = list(reader.read_existing_events())
    
    assert len(collected) == expected_count
