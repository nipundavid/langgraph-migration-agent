
from pathlib import Path

import pytest

from langgraph_migration_agent.migration.directory_scanner import (
    DirectoryScanner,
)


def test_scan_discovers_python_files(tmp_path: Path):
    """
    Verify that the scanner recursively discovers Python files
    and returns paths relative to the input directory.

    Also verify that non-Python files are ignored.
    """

    # Arrange: Create a sample project structure.
    (tmp_path / "main.py").write_text("print('hello')")

    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    (agents_dir / "agent.py").write_text("def create_agent(): pass")

    (tmp_path / "README.md").write_text("# Sample project")

    # Act: Scan the project directory.
    scanner = DirectoryScanner()
    files = scanner.scan(tmp_path)

    # Assert: Only Python files are returned with relative paths.
    assert set(files) == {
        Path("main.py"),
        Path("agents/agent.py"),
    }


def test_scan_rejects_invalid_directory(tmp_path: Path):
    """
    Verify that the scanner raises ValueError when the supplied
    input path does not exist or is not a directory.
    """

    # Arrange: Define a path that does not exist.
    invalid_path = tmp_path / "does-not-exist"

    # Act and Assert: Scanning an invalid path must raise ValueError.
    scanner = DirectoryScanner()

    with pytest.raises(ValueError):
        scanner.scan(invalid_path)


def test_scan_returns_empty_list_for_empty_directory(tmp_path: Path):
    """
    Verify that scanning a valid directory containing no Python
    files returns an empty list rather than raising an exception.
    """

    # Arrange: tmp_path is an existing empty directory.

    # Act: Scan the empty directory.
    scanner = DirectoryScanner()
    files = scanner.scan(tmp_path)

    # Assert: No Python files should be discovered.
    assert files == []

def test_scan_rejects_file_path(tmp_path: Path):
    """
    Verify that the scanner rejects an existing file
    when a directory is expected.
    """

    # Arrange: Create a regular file.
    file_path = tmp_path / "README.md"
    file_path.write_text("# Sample project")

    # Act and Assert: A file path must raise ValueError.
    scanner = DirectoryScanner()

    with pytest.raises(ValueError):
        scanner.scan(file_path)
