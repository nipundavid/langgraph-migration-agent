import libcst as cst
import pytest

from langgraph_migration_agent.analysis.import_analyzer import ImportAnalyzer


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            # Unaliased import: should be recorded.
            "from langgraph.prebuilt import create_react_agent\n",
            {"create_react_agent": "create_react_agent"},
        )
    ],
)
def test_import_analyzer(source: str, expected: dict[str, str]) -> None:
    module = cst.parse_module(source)

    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    assert analyzer.imported_names == expected