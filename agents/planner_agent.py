import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from retrieval.hybrid_retriever import hybrid_search, format_context
from tools.muscle_freshness import get_muscle_freshness, format_freshness_report
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL, USER_GOAL, TRAINING_DAYS_PER_WEEK


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0.2,
    )


PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are FitMind Weekly Planner.
Create a personalised weekly workout plan based on:
- User goal and training frequency
- Recent training history (avoid overtraining)
- Muscle recovery status

Format the plan clearly as:
Day 1: [Split name] — [muscles]
Day 2: Rest
Day 3: [Split name] — [muscles]
etc.

Then list 4-5 recommended exercises per training day.
Add a brief note about nutrition focus for the week."""),

    ("human", """User goal: {goal}
Training days per week: {training_days}

Recent training history:
{history_context}

Current muscle recovery status:
{freshness_report}

Create the weekly plan:""")
])


def weekly_planner(query: str = "plan my week") -> str:
    """
    Generates a personalised weekly workout plan
    based on training history and muscle recovery.
    """
    print(f"\nPlanner Agent activated...")
    print("-" * 50)

    # Get recent history
    results = hybrid_search("workout training this week muscles", k=5)
    history_context = format_context(results)

    # Muscle freshness
    freshness = get_muscle_freshness()
    freshness_report = format_freshness_report(freshness)

    llm = get_llm()
    chain = PLANNER_PROMPT | llm | StrOutputParser()

    response = chain.invoke({
        "goal": USER_GOAL,
        "training_days": TRAINING_DAYS_PER_WEEK,
        "history_context": history_context,
        "freshness_report": freshness_report,
    })

    return response


if __name__ == "__main__":
    print("=" * 60)
    print("FITMIND PLANNER AGENT TEST")
    print("=" * 60)
    plan = weekly_planner()
    print(plan)
