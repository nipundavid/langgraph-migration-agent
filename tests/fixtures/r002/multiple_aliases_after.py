from langgraph.prebuilt import (
    create_react_agent as cra,
    create_react_agent as react_agent,
)

agent1 = cra(model, tools)
agent2 = react_agent(model, tools)