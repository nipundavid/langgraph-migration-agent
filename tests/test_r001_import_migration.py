from pathlib import Path

import libcst as cst

from langgraph_migration_agent.rules.r001_import_migration import (
    R001ImportMigration,
)


def test_r001_import_migration():

    fixtures = Path(__file__).parent / "fixtures" / "r001"

    before = (fixtures / "before.py").read_text()
    expected = (fixtures / "after.py").read_text()

    module = cst.parse_module(before)

    migrated = module.visit(R001ImportMigration())

    assert migrated.code == expected