from langgraph.prebuilt import (
    create_react_agent as cra,
    some_other_function,
)

agent = cra(model, tools)
other = some_other_function()