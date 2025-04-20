import json
import pytest
from write import Writer

@pytest.mark.parametrize(
    "output_destiny, result, expected_output, is_cli",
    [
        # CLI branch: should print JSON+newline
        (
            "cli",
            {"foo": 1, "bar": 2},
            json.dumps({"foo": 1, "bar": 2}) + "\n\n",  # print adds an extra newline
            True
        ),
        # File branch: write single result, then read back
        (
            "events_out.json",
            {"a": 10, "b": 20},
            json.dumps({"a": 10, "b": 20}) + "\n",
            False
        ),
    ]
)
def test_writer_write(tmp_path, capsys, output_destiny, result, expected_output, is_cli):
    """
    Parametrized tests for Writer.write:
    - When output_destiny == 'cli', ensure the JSON is printed to stdout.
    - Otherwise, ensure the JSON is appended (with newline) to the specified file.
    """
    # If file mode, adjust path
    if not is_cli:
        file_path = tmp_path / output_destiny
        output_destiny = str(file_path)

    writer = Writer(output_destiny)
    writer.write(result)

    if is_cli:
        # Capture and verify stdout
        captured = capsys.readouterr()
        assert captured.out == expected_output
    else:
        # Read the file and verify its contents
        text = (tmp_path / output_destiny).read_text()
        assert text == expected_output

@pytest.mark.parametrize(
    "initial_content, new_result, expected_lines",
    [
        # Start with empty file, write one event
        (
            "",
            {"x": 123},
            [json.dumps({"x": 123})]
        ),
        # Start with existing line, append another
        (
            json.dumps({"x": 1}) + "\n",
            {"y": 2},
            [json.dumps({"x": 1}), json.dumps({"y": 2})]
        ),
    ]
)
def test_writer_append_behavior(tmp_path, initial_content, new_result, expected_lines):
    """
    Verify that write() appends to an existing file rather than overwriting.
    """
    file_path = tmp_path / "append_test.json"
    file_path.write_text(initial_content)

    writer = Writer(str(file_path))
    writer.write(new_result)

    # Read all non-empty lines and compare
    lines = [line for line in file_path.read_text().splitlines() if line]
    assert lines == expected_lines
