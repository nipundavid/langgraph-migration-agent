from langgraph.prebuilt import create_react_agent as cra

agent = cra(model, tools)

other = create_react_agent(model, tools)