
import libcst as cst
import pytest
from textwrap import dedent

from langgraph_migration_agent.rules.r001_import_migration import (
    R001ImportMigration,
)


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "from langgraph.prebuilt import create_react_agent\n",
            "from langchain.agents import create_agent\n",
        ),
        (
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


def test_r001_leaves_aliased_import_unchanged() -> None:
    source = dedent("""\
        from langgraph.prebuilt import create_react_agent as cra
    """)

    module = cst.parse_module(source)
    transformer = R001ImportMigration()

    migrated = module.visit(transformer)

    assert migrated.code == source
    assert len(transformer.diagnostics) == 1
    assert "Aliased" in transformer.diagnostics[0]


def test_r001_splits_mixed_imports() -> None:
    source = dedent("""\
        from langgraph.prebuilt import create_react_agent, some_other_function
    """)

    expected = dedent("""\
        from langchain.agents import create_agent
        from langgraph.prebuilt import some_other_function
    """)

    module = cst.parse_module(source)
    transformer = R001ImportMigration()

    migrated = module.visit(transformer)

    assert migrated.code == expected
    assert transformer.diagnostics == []


def test_r001_parenthesized_mixed_imports() -> None:
    source = dedent("""\
        from langgraph.prebuilt import (
            create_react_agent,
            some_other_function,
        )
    """)

    expected = dedent("""\
        from langchain.agents import create_agent
        from langgraph.prebuilt import (
            some_other_function,
        )
    """)

    module = cst.parse_module(source)
    transformer = R001ImportMigration()

    migrated = module.visit(transformer)

    assert migrated.code == expected
    assert transformer.diagnostics == []


def test_r001_preserves_leading_comment() -> None:
    source = dedent("""\
        # LangGraph agent import
        from langgraph.prebuilt import create_react_agent, some_other_function
    """)

    expected = dedent("""\
        # LangGraph agent import
        from langchain.agents import create_agent
        from langgraph.prebuilt import some_other_function
    """)

    module = cst.parse_module(source)
    transformer = R001ImportMigration()

    migrated = module.visit(transformer)

    assert migrated.code == expected
    assert transformer.diagnostics == []
