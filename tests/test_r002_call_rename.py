from pathlib import Path

import libcst as cst

from langgraph_migration_agent.analysis.import_analyzer import ImportAnalyzer
from langgraph_migration_agent.rules.r002_call_rename import R002CallRename


def test_r002_call_rename():

    fixtures = Path(__file__).parent / "fixtures" / "r002"

    before = (fixtures / "before.py").read_text()
    expected = (fixtures / "after.py").read_text()

    # Parse source
    module = cst.parse_module(before)

    # Pass 1: Analyze imports
    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    # Pass 2: Rename function calls
    migrated = module.visit(
        R002CallRename(analyzer.imported_names)
    )

    assert migrated.code == expected