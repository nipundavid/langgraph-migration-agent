from langchain.agents import create_agent

agent = create_react_agent(
    model=model,
    tools=tools
)