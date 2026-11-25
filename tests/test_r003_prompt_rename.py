import libcst as cst

from langgraph_migration_agent.analysis.import_analyzer import ImportAnalyzer
from langgraph_migration_agent.rules.r003_prompt_rename import (
    R003PromptRename,
)


def test_r003_renames_string_prompt_on_imported_agent_call():
    source = '''\
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=model,
    tools=tools,
    prompt="You are helpful",
)
'''

    expected = '''\
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=model,
    tools=tools,
    system_prompt="You are helpful",
)
'''

    module = cst.parse_module(source)

    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    migrated = module.visit(
        R003PromptRename(analyzer.imported_names)
    )

    assert migrated.code == expected


def test_r003_leaves_dynamic_prompt_unchanged():
    source = '''\
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=build_prompt(),
)
'''

    module = cst.parse_module(source)
    analyzer = ImportAnalyzer()
    module.visit(analyzer)

    migrated = module.visit(
        R003PromptRename(analyzer.imported_names)
    )

    assert migrated.code == source