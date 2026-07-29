import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.router import classify_intent
from agents.session_coach_agent import session_coach
from agents.nutrition_agent import nutrition_coach
from agents.progress_agent import progress_report
from agents.planner_agent import weekly_planner
from chain import ask


# ── STATE ──
class FitMindState(TypedDict):
    message: str
    intent: str
    response: str


# ── NODES ──
def router_node(state: FitMindState) -> FitMindState:
    """Classifies the user message intent."""
    intent = classify_intent(state["message"])
    print(f"\nIntent detected: {intent}")
    return {**state, "intent": intent}


def session_coach_node(state: FitMindState) -> FitMindState:
    response = session_coach(state["message"])
    return {**state, "response": response}


def nutrition_node(state: FitMindState) -> FitMindState:
    response = nutrition_coach(state["message"])
    return {**state, "response": response}


def progress_node(state: FitMindState) -> FitMindState:
    response = progress_report(state["message"])
    return {**state, "response": response}


def planner_node(state: FitMindState) -> FitMindState:
    response = weekly_planner(state["message"])
    return {**state, "response": response}


def general_node(state: FitMindState) -> FitMindState:
    response = ask(state["message"])
    return {**state, "response": response}


# ── ROUTING LOGIC ──
def route_by_intent(state: FitMindState) -> str:
    """Routes to the correct agent based on intent."""
    intent = state["intent"]
    routes = {
        "SESSION_COACH": "session_coach",
        "NUTRITION": "nutrition",
        "PROGRESS": "progress",
        "PLANNER": "planner",
        "GENERAL": "general",
    }
    return routes.get(intent, "general")


# ── BUILD GRAPH ──
def build_graph():
    graph = StateGraph(FitMindState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("session_coach", session_coach_node)
    graph.add_node("nutrition", nutrition_node)
    graph.add_node("progress", progress_node)
    graph.add_node("planner", planner_node)
    graph.add_node("general", general_node)

    # Entry point
    graph.set_entry_point("router")

    # Conditional routing from router
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "session_coach": "session_coach",
            "nutrition": "nutrition",
            "progress": "progress",
            "planner": "planner",
            "general": "general",
        }
    )

    # All agents lead to END
    for node in ["session_coach", "nutrition", "progress", "planner", "general"]:
        graph.add_edge(node, END)

    return graph.compile()


# ── MAIN INTERFACE ──
def chat(message: str) -> str:
    """
    Single entry point for all user messages.
    Routes to the right agent automatically.
    """
    app = build_graph()
    result = app.invoke({"message": message, "intent": "", "response": ""})
    return result["response"]


if __name__ == "__main__":
    print("=" * 60)
    print("FITMIND MULTI-AGENT SYSTEM TEST")
    print("=" * 60)

    test_messages = [
        "Pull day today. Planning Lat Pulldown, Seated Row, Face Pulls, Bicep Curl",
        "Had chicken rice bowl for lunch",
        "How am I doing this week?",
        "Plan my workouts for next week",
        "When did I last train chest and what weight did I use?",
    ]

    for message in test_messages:
        print(f"\nUser: {message}")
        print("-" * 50)
        response = chat(message)
        print(f"FitMind: {response}")
        print("=" * 60)
