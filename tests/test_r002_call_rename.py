from pathlib import Path

import libcst as cst
import pytest

from langgraph_migration_agent.analysis.import_analyzer import ImportAnalyzer
from langgraph_migration_agent.rules.r002_call_rename import R002CallRename


@pytest.mark.parametrize(
    "fixture_name",
    ["single_alias", "multiple_imports","multiple_aliases"],
)
def test_r002_call_rename(fixture_name):

    fixtures = Path(__file__).parent / "fixtures" / "r002"

    before = (fixtures / f"{fixture_name + '_' if fixture_name else ''}before.py").read_text()
    expected = (fixtures / f"{fixture_name + '_' if fixture_name else ''}after.py").read_text()

    module = cst.parse_module(before)

    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    migrated = module.visit(
        R002CallRename(analyzer.imported_names)
    )

    assert migrated.code == expected

def test_r002_renames_unaliased_imported_call():
    source = """\
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, tools)
"""

    expected = """\
from langgraph.prebuilt import create_react_agent

agent = create_agent(model, tools)
"""

    module = cst.parse_module(source)

    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    migrated = module.visit(
        R002CallRename(analyzer.imported_names)
    )

    assert migrated.code == expected