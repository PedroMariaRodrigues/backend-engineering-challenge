import pytest
from datetime import datetime
from types import SimpleNamespace
from unittest import mock
from unbabel_cli import main

def test_main_integration(monkeypatch):
    mock_args = [
        "main.py",
        "--input_file=test.jsonl",
        "--window_size=10",
        "--metric=moving_average",
        "--output=cli"
    ]

    monkeypatch.setattr("sys.argv", mock_args)

    with mock.patch("unbabel_cli.Reader") as MockReader, \
         mock.patch("unbabel_cli.Processor") as MockProcessor, \
         mock.patch("unbabel_cli.Writer") as MockWriter:

        mock_reader = MockReader.return_value
        mock_processor = MockProcessor.return_value
        mock_writer = MockWriter.return_value

        mock_reader.read_existing_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 0), duration=10),
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 1), duration=20)
        ]

        mock_processor.process.side_effect = [
            {"date": "2025-04-20 12:00:00", "average_delivery_time": 0},
            {"date": "2025-04-20 12:01:00", "average_delivery_time": 15},
        ]
        mock_processor.finalize.return_value = {"date": "2025-04-20 12:02:00", "average_delivery_time": 20}

        main()

        assert mock_writer.write.call_count == 3


def test_main_writes_to_file(monkeypatch, tmp_path):
    output_file = tmp_path / "output.json"
    mock_args = [
        "unbabel_cli.py",
        "--input_file=test.jsonl",
        "--window_size=5",
        "--metric=moving_average",
        f"--output={output_file}"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with mock.patch("unbabel_cli.Reader") as MockReader, \
         mock.patch("unbabel_cli.Processor") as MockProcessor:

        mock_reader = MockReader.return_value
        mock_processor = MockProcessor.return_value

        mock_reader.read_existing_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 0), duration=10),
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 1), duration=20)
        ]

        mock_processor.process.side_effect = [
            {"date": "2025-04-20 12:00:00", "average_delivery_time": 0},
            {"date": "2025-04-20 12:01:00", "average_delivery_time": 15},
        ]
        mock_processor.finalize.return_value = {"date": "2025-04-20 12:02:00", "average_delivery_time": 20}

        main()

        # Read the output file and verify its contents
        with open(output_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
            assert '"average_delivery_time": 0' in lines[0]
            assert '"average_delivery_time": 15' in lines[1]
            assert '"average_delivery_time": 20' in lines[2]

def test_main_invalid_metric(monkeypatch): 
    mock_args = [
        "unbabel_cli.py",
        "--input_file=test.jsonl",
        "--window_size=5",
        "--metric=invalid_metric",  # Invalid metric
        "--output=cli"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    # Now we expect a SystemExit error, because argparse will catch the invalid metric
    with pytest.raises(SystemExit) as excinfo:
        main()

    # Ensure the error code is 2, which signifies an invalid argument
    assert excinfo.value.code == 2

