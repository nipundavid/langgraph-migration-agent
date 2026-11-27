
from pathlib import Path
from textwrap import dedent

import pytest

from langgraph_migration_agent.migration.output_manager import OutputManager


def test_prepare_creates_default_output_directory(tmp_path: Path):
    """Verify that the default output directory is created beside the input."""

    input_path = tmp_path / "my-project"
    input_path.mkdir()

    output_manager = OutputManager()
    output_path = output_manager.prepare(input_path)

    assert output_path == tmp_path / "my-project_migration_output"
    assert output_path.is_dir()


def test_prepare_creates_custom_output_directory(tmp_path: Path):
    """Verify that a user-provided output directory is created."""

    input_path = tmp_path / "my-project"
    input_path.mkdir()

    custom_output = tmp_path / "custom-output"

    output_manager = OutputManager()
    output_path = output_manager.prepare(input_path, custom_output)

    assert output_path == custom_output
    assert output_path.is_dir()


def test_prepare_overwrites_existing_output_when_confirmed(
    tmp_path: Path, monkeypatch
):
    """Verify that existing output contents are deleted after confirmation."""

    input_path = tmp_path / "my-project"
    input_path.mkdir()

    output_path = tmp_path / "migration-output"
    output_path.mkdir()
    (output_path / "old_file.py").write_text("old content")

    # Simulate the user confirming the overwrite.
    monkeypatch.setattr("builtins.input", lambda _: "yes")

    output_manager = OutputManager()
    result = output_manager.prepare(input_path, output_path)

    assert result.is_dir()
    assert not (result / "old_file.py").exists()


def test_prepare_aborts_when_overwrite_is_rejected(tmp_path: Path, monkeypatch):
    """Verify that existing output contents remain untouched when rejected."""

    input_path = tmp_path / "my-project"
    input_path.mkdir()

    output_path = tmp_path / "migration-output"
    output_path.mkdir()
    old_file = output_path / "old_file.py"
    old_file.write_text("old content")

    # Simulate the user declining the overwrite.
    monkeypatch.setattr("builtins.input", lambda _: "no")

    output_manager = OutputManager()

    with pytest.raises(RuntimeError):
        output_manager.prepare(input_path, output_path)

    assert old_file.read_text() == "old content"


def test_prepare_rejects_output_path_that_is_a_file(tmp_path: Path):
    """Verify that an existing file cannot be used as the output directory."""

    input_path = tmp_path / "my-project"
    input_path.mkdir()

    output_path = tmp_path / "output.txt"
    output_path.write_text("existing content")

    output_manager = OutputManager()

    with pytest.raises(ValueError):
        output_manager.prepare(input_path, output_path)


def test_prepare_does_not_modify_input_directory(tmp_path: Path, monkeypatch):
    """Verify that preparing the output directory never deletes source files."""

    input_path = tmp_path / "my-project"
    input_path.mkdir()

    source_file = input_path / "agent.py"
    source_file.write_text(
        dedent("""\
            from langgraph.prebuilt import create_react_agent
        """)
    )

    output_path = tmp_path / "migration-output"
    output_path.mkdir()
    (output_path / "old_file.py").write_text("old content")

    monkeypatch.setattr("builtins.input", lambda _: "yes")

    output_manager = OutputManager()
    output_manager.prepare(input_path, output_path)

    assert source_file.exists()
    assert "create_react_agent" in source_file.read_text()
