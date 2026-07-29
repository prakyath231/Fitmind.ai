import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
    )


ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a router for a fitness AI system.
Classify the user message into EXACTLY one of these categories:

SESSION_COACH - user mentions a workout plan, exercises they will do today, sets/reps
NUTRITION - user logs food, mentions a meal, asks about protein or calories
PROGRESS - user asks how they are doing, wants a summary, asks about trends
PLANNER - user asks to plan their week or schedule workouts
GENERAL - anything else about fitness, history, or general questions

Reply with ONLY the category name. Nothing else."""),
    ("human", "{message}")
])


def classify_intent(message: str) -> str:
    """
    Classifies user message into one of 5 intents.
    Returns the intent as a string.
    """
    llm = get_llm()
    chain = ROUTER_PROMPT | llm | StrOutputParser()
    intent = chain.invoke({"message": message}).strip().upper()

    # Safety fallback
    valid_intents = ["SESSION_COACH", "NUTRITION", "PROGRESS", "PLANNER", "GENERAL"]
    if intent not in valid_intents:
        intent = "GENERAL"

    return intent


if __name__ == "__main__":
    test_messages = [
        "Pull day today, planning lat pulldown and seated row",
        "Had chicken rice bowl for lunch",
        "How am I doing this week?",
        "Plan my workouts for next week",
        "When did I last train chest?",
    ]

    print("ROUTER TEST")
    print("=" * 50)
    for msg in test_messages:
        intent = classify_intent(msg)
        print(f"Message : {msg[:50]}")
        print(f"Intent  : {intent}")
        print("-" * 50)
