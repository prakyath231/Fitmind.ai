import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from retrieval.hybrid_retriever import hybrid_search, format_context
from tools.muscle_freshness import get_muscle_freshness, format_freshness_report, get_undertrained_muscles
from tools.macro_calculator import calculate_targets, format_targets
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
    )


PROGRESS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are FitMind Progress Coach.
Your job: analyse the user's training and nutrition 
history and give a clear weekly progress report.

Always cover:
1. Training consistency — how many days trained
2. Muscle balance — which groups trained vs neglected
3. Nutrition averages — avg protein and calories
4. Wins — what improved this week
5. Focus areas — what needs work next week

Be specific with numbers. Be honest but motivating."""),

    ("human", """Recent training and nutrition logs:
{history_context}

Muscle recovery status:
{freshness_report}

Undertrained muscles:
{undertrained}

Daily targets for reference:
{targets}

Give a weekly progress report:""")
])


def progress_report(query: str = "weekly progress summary") -> str:
    """
    Generates a weekly progress report by
    reasoning over the last 7 days of logs.
    """
    print(f"\nProgress Agent activated...")
    print("-" * 50)

    # Get recent history
    results = hybrid_search("workout nutrition protein calories this week", k=5)
    history_context = format_context(results)

    # Muscle freshness
    freshness = get_muscle_freshness()
    freshness_report = format_freshness_report(freshness)
    undertrained = get_undertrained_muscles(freshness, threshold_days=5)

    llm = get_llm()
    chain = PROGRESS_PROMPT | llm | StrOutputParser()

    response = chain.invoke({
        "history_context": history_context,
        "freshness_report": freshness_report,
        "undertrained": ", ".join(undertrained) if undertrained else "None",
        "targets": format_targets(),
    })

    return response


if __name__ == "__main__":
    print("=" * 60)
    print("FITMIND PROGRESS AGENT TEST")
    print("=" * 60)
    report = progress_report()
    print(report)
