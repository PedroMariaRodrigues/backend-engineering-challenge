import pytest
from datetime import datetime
from types import SimpleNamespace
from unittest import mock
from unbabel_cli import main

def test_main_integration(monkeypatch):
    """
    Test the main function to ensure it integrates all components correctly.
    """
    mock_args = [
        "main.py",
        "--input_file=example.json",
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
    """
    Test the main function to ensure it writes the output to a file correctly.
    """
    output_file = tmp_path / "output.json"
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
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
    """
    Test when an invalid metric is provided.
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
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

def test_main_missing_input_file(monkeypatch):
    """
    Test when the input file is missing.
    """
    mock_args = [
        "unbabel_cli.py",
        "--window_size=5",
        "--metric=moving_average",
        "--output=cli"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 2  # argparse exits with code 2 for argument errors

def test_main_missing_window_size(monkeypatch):
    """
    Test when the window size is missing.
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
        "--metric=moving_average",
        "--output=cli"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 2

def test_main_invalid_window_size_zero(monkeypatch):
    """
    Test when the window size is zero.
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
        "--window_size=0",
        "--metric=moving_average",
        "--output=cli"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with pytest.raises(ValueError, match="The window size must be a positive integer."):
        main()

def test_main_nonexistent_input_file(monkeypatch):
    """
    Test when the input file does not exist.
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=nonexistent_file.json",
        "--window_size=5",
        "--metric=moving_average",
        "--output=cli"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with pytest.raises(FileNotFoundError, match="The file 'nonexistent_file.json' does not exist."):
        main()
        
def test_main_keep_live(monkeypatch):
    """
    Test the main function with the --keep_live option
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
        "--window_size=5",
        "--metric=moving_average",
        "--output=cli",
        "--keep_live"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with mock.patch("unbabel_cli.Reader") as MockReader, \
         mock.patch("unbabel_cli.Processor") as MockProcessor, \
         mock.patch("unbabel_cli.Writer") as MockWriter:

        mock_reader = MockReader.return_value
        mock_processor = MockProcessor.return_value
        mock_writer = MockWriter.return_value

        # Simulate existing events
        mock_reader.read_existing_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 0), duration=10)
        ]

        # Simulate live events
        mock_reader.monitor_live_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 1), duration=20)
        ]

        mock_processor.process.side_effect = [
            {"date": "2025-04-20 12:00:00", "average_delivery_time": 10},
            {"date": "2025-04-20 12:01:00", "average_delivery_time": 20}
        ]
        mock_processor.finalize.return_value = {"date": "2025-04-20 12:02:00", "average_delivery_time": 25}

        main()

        # Verify that write was called for both existing and live events
        assert mock_writer.write.call_count == 2


def test_main_keep_live_with_gap_filling(monkeypatch):
    """
    Test the main function with the --keep_live option and gap filling.
    Simulates existing events, live events with a gap, and handles KeyboardInterrupt.
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
        "--window_size=5",
        "--metric=moving_average",
        "--output=cli",
        "--keep_live"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with mock.patch("unbabel_cli.Reader") as MockReader, \
         mock.patch("unbabel_cli.Processor") as MockProcessor, \
         mock.patch("unbabel_cli.Writer") as MockWriter:

        mock_reader = MockReader.return_value
        mock_processor = MockProcessor.return_value
        mock_writer = MockWriter.return_value

        # Simulate existing events
        mock_reader.read_existing_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 0), duration=10)
        ]

        # Simulate live events with a gap (e.g., missing 12:01 and 12:02)
        def live_events():
            yield SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 3), duration=20)
            raise KeyboardInterrupt  # Simulate user interrupt

        mock_reader.monitor_live_events.side_effect = live_events

        # Simulate processor.process returning multiple results for gap filling
        def process_side_effect(event):
            if event.timestamp == datetime(2025, 4, 20, 12, 0):
                return {"date": "2025-04-20 12:00:00", "average_delivery_time": 10}
            elif event.timestamp == datetime(2025, 4, 20, 12, 3):
                return [
                    {"date": "2025-04-20 12:01:00", "average_delivery_time": 15},
                    {"date": "2025-04-20 12:02:00", "average_delivery_time": 20},
                    {"date": "2025-04-20 12:03:00", "average_delivery_time": 25}
                ]

        mock_processor.process.side_effect = process_side_effect

        # Simulate finalize returning a final result
        mock_processor.finalize.return_value = {"date": "2025-04-20 12:04:00", "average_delivery_time": 30}

        # Run the main function and catch SystemExit
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0  # Ensure the exit code is 0

        # Verify that write was called for existing event
        mock_writer.write.assert_any_call({"date": "2025-04-20 12:00:00", "average_delivery_time": 10})

        # Verify that write was called for each gap-filled result
        mock_writer.write.assert_any_call({"date": "2025-04-20 12:01:00", "average_delivery_time": 15})
        mock_writer.write.assert_any_call({"date": "2025-04-20 12:02:00", "average_delivery_time": 20})
        mock_writer.write.assert_any_call({"date": "2025-04-20 12:03:00", "average_delivery_time": 25})

        # Verify that finalize result was written after KeyboardInterrupt
        mock_writer.write.assert_any_call({"date": "2025-04-20 12:04:00", "average_delivery_time": 30})

        # Total write calls should be 5
        assert mock_writer.write.call_count == 5

def test_main_keyboard_interrupt(monkeypatch):
    """
    Test the main function to ensure it handles KeyboardInterrupt gracefully.
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
        "--window_size=5",
        "--metric=moving_average",
        "--output=cli",
        "--keep_live"
    ]
    monkeypatch.setattr("sys.argv", mock_args)

    with mock.patch("unbabel_cli.Reader") as MockReader, \
         mock.patch("unbabel_cli.Processor") as MockProcessor, \
         mock.patch("unbabel_cli.Writer") as MockWriter:

        mock_reader = MockReader.return_value
        mock_processor = MockProcessor.return_value
        mock_writer = MockWriter.return_value

        # Simulate existing events
        mock_reader.read_existing_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 0), duration=10)
        ]

        # Simulate live events that raise KeyboardInterrupt
        def live_events():
            yield SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 1), duration=20)
            raise KeyboardInterrupt()

        mock_reader.monitor_live_events.side_effect = live_events

        mock_processor.process.side_effect = [
            {"date": "2025-04-20 12:00:00", "average_delivery_time": 10},
            {"date": "2025-04-20 12:01:00", "average_delivery_time": 20}
        ]
        mock_processor.finalize.return_value = {"date": "2025-04-20 12:02:00", "average_delivery_time": 25}

        with pytest.raises(SystemExit) as excinfo:
            main()

        # Verify that the application exits gracefully
        assert excinfo.value.code == 0
        assert mock_writer.write.call_count == 3  # Two events + finalize

def test_main_gap_filling(monkeypatch):
    """
    Test the main function to ensure it handles gap filling correctly
    """
    mock_args = [
        "unbabel_cli.py",
        "--input_file=example.json",
        "--window_size=5",
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

        # Simulate existing events
        mock_reader.read_existing_events.return_value = [
            SimpleNamespace(timestamp=datetime(2025, 4, 20, 12, 0), duration=10)
        ]

        # Simulate processor returning multiple results
        mock_processor.process.return_value = [
            {"date": "2025-04-20 12:00:00", "average_delivery_time": 10},
            {"date": "2025-04-20 12:01:00", "average_delivery_time": 15}
        ]
        mock_processor.finalize.return_value = {"date": "2025-04-20 12:02:00", "average_delivery_time": 20}

        main()

        # Verify that write was called for each result
        assert mock_writer.write.call_count == 3
