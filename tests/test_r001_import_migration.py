import libcst as cst
import pytest

from langgraph_migration_agent.rules.r001_import_migration import (
    R001ImportMigration,
)


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            # Unaliased import.
            "from langgraph.prebuilt import create_react_agent\n",
            "from langchain.agents import create_agent\n",
        ),
        (
            # Aliased import: alias must be preserved.
            "from langgraph.prebuilt import create_react_agent as cra\n",
            "from langchain.agents import create_agent as cra\n",
        ),
        (
            # Unrelated import: must remain unchanged.
            "from langgraph.prebuilt import some_other_function\n",
            "from langgraph.prebuilt import some_other_function\n",
        ),
    ],
)
def test_r001_import_migration(source: str, expected: str) -> None:
    module = cst.parse_module(source)

    transformer = R001ImportMigration()
    migrated = module.visit(transformer)

    assert migrated.code == expected
    assert transformer.diagnostics == []


def test_r001_does_not_move_mixed_imports() -> None:
    source = (
        "from langgraph.prebuilt import (\n"
        "    create_react_agent as cra,\n"
        "    some_other_function,\n"
        ")\n"
    )

    module = cst.parse_module(source)

    transformer = R001ImportMigration()
    migrated = module.visit(transformer)

    assert migrated.code == source
    assert len(transformer.diagnostics) == 1
    assert "Mixed import" in transformer.diagnostics[0]