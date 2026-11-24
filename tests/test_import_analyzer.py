import libcst as cst

from langgraph_migration_agent.analysis.import_analyzer import ImportAnalyzer


def test_import_analyzer_finds_unaliased_import() -> None:
    source = "from langgraph.prebuilt import create_react_agent\n"

    module = cst.parse_module(source)
    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    assert analyzer.imported_names == {
        "create_react_agent": "create_react_agent"
    }
