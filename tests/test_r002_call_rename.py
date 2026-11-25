
from textwrap import dedent

import libcst as cst

from langgraph_migration_agent.analysis.import_analyzer import ImportAnalyzer
from langgraph_migration_agent.rules.r002_call_rename import R002CallRename


def test_r002_renames_unaliased_imported_call():
    source = dedent("""\
        from langgraph.prebuilt import create_react_agent

        agent = create_react_agent(model, tools)
    """)

    expected = dedent("""\
        from langgraph.prebuilt import create_react_agent

        agent = create_agent(model, tools)
    """)

    module = cst.parse_module(source)

    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    migrated = module.visit(
        R002CallRename(analyzer.imported_names)
    )

    assert migrated.code == expected
