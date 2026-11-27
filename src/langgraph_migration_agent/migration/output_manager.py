from pathlib import Path
import logging
import shutil

logger = logging.getLogger(__name__)

class OutputManager:

    def prepare(
        self,
        input_path: Path,
        output_path: Path | None = None,
    ) -> Path:
        """
        Prepare the output directory for migration results.

        If an output path is provided, it is used as-is. If not, a
        default output directory named 'migration_output' is created
        in the same parent directory as the input path.

        Args:
            input_path (Path): The path to the input directory.
            output_path (Path | None): Optional path to the output directory.

        Returns: The path to the prepared output directory.
        """
         # Generate default output path if none was provided.
        if output_path is None:
            output_path = input_path.parent / f"{input_path.name}_migration_output"

        # Resolve paths for reliable comparison.
        input_resolved = input_path.resolve()
        output_resolved = output_path.resolve()

        # Prevent output from overwriting or containing input.
        if (
            output_resolved == input_resolved
            or input_resolved.is_relative_to(output_resolved)
        ):
            raise RuntimeError(
                "Output path cannot be the same as or a parent of the input path."
            )

        # Reject an existing file at the output path.
        if output_path.exists() and not output_path.is_dir():
            raise ValueError(f"Output path {output_path} exists but is not a directory.")

        # Handle an existing output directory.
        if output_path.exists():
            if not self._confirm_overwrite(output_path):
                raise RuntimeError("Migration cancelled by user.")

            shutil.rmtree(output_path)
            logger.info("Existing output directory '%s' deleted.", output_path)

        # Create the output directory.
        output_path.mkdir(parents=True, exist_ok=True)

        return output_path


    def _confirm_overwrite(self, output_path: Path) -> bool:
        """
        Confirm with the user whether to overwrite an existing output directory.

        Args:
            output_path (Path): The path to the output directory.

        Returns: True if the user confirms overwrite, False otherwise.
        """
        response = input(
            f"Output directory '{output_path}' already exists. Its contents will be deleted. Proceed? [y/N]: "
        )
        return response.strip().lower() in ("y", "yes")