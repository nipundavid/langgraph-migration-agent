from pathlib import Path

class DirectoryScanner:

    def scan(self, input_path: Path) -> list[Path]:
        if not input_path.is_dir():
            raise ValueError(f"Input path {input_path} is not a directory.")
        files = []
        input_path = input_path.resolve()
        for file_path in input_path.rglob("*.py"):
            files.append(file_path.relative_to(input_path))
        return files