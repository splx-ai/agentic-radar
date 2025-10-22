from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agents import research_agent, coder_agent, browser_agent


class State:
    messages: list


def research_node(state: State) -> Command:
    """Research node that invokes research agent"""
    result = research_agent.invoke(state)
    return Command(update={"messages": result["messages"]}, goto="supervisor")


def code_node(state: State) -> Command:
    """Coder node that invokes coder agent"""
    result = coder_agent.invoke(state)
    return Command(update={"messages": result["messages"]}, goto="supervisor")


def browser_node(state: State) -> Command:
    """Browser node that invokes browser agent"""
    result = browser_agent.invoke(state)
    return Command(update={"messages": result["messages"]}, goto="supervisor")


def supervisor_node(state: State) -> Command:
    """Supervisor decides next step"""
    return Command(goto="__end__")


def build_graph():
    """Build the workflow graph"""
    builder = StateGraph(State)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("coder", code_node)
    builder.add_node("browser", browser_node)
    return builder.compile()
