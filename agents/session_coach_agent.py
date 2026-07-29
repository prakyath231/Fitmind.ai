import json
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from retrieval.hybrid_retriever import hybrid_search, format_context
from tools.muscle_freshness import (
    get_muscle_freshness,
    get_undertrained_muscles,
    format_freshness_report
)
from tools.overload_calculator import format_overload_recommendations
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL
import json


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
    )


SESSION_COACH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are FitMind Session Coach — a personal AI 
fitness trainer who knows the user's complete training history.

Your job when a user tells you their planned session:
1. Review their exercise selection
2. Give progressive overload targets based on history
3. Suggest optimal exercise ORDER
4. Warn about any overtraining risks
5. Suggest any missing exercises for the muscle groups
6. Keep it motivating and concise

Always be specific with weights and reps from history.
Format your response clearly with sections."""),

    ("human", """User's planned session today: {planned_session}

Training history context:
{history_context}

Muscle recovery status:
{freshness_report}

Progressive overload data:
{overload_data}

Undertrained muscles (not trained in 7+ days):
{undertrained}

Give your coaching response:""")
])


def session_coach(planned_session: str) -> str:
    """
    Main session coach function.

    User says: "Pull day today — lat pulldown, seated row, 
                face pulls, bicep curls"
    
    Agent responds with:
    - Progressive overload targets
    - Exercise order
    - Overtraining warnings
    - Missing exercise suggestions
    """
    print(f"\nSession Coach activated...")
    print(f"Planned: {planned_session}")
    print("-" * 50)

    # 1. Retrieve relevant history from RAG
    history_results = hybrid_search(planned_session, k=3)
    history_context = format_context(history_results)

    # 2. Get muscle freshness
    freshness = get_muscle_freshness()
    freshness_report = format_freshness_report(freshness)
    undertrained = get_undertrained_muscles(freshness, threshold_days=7)

    # 3. Extract exercise names from planned session
    # Simple extraction — find capitalized words
    import re
    exercise_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    exercises = re.findall(exercise_pattern, planned_session)

    # Filter common non-exercise words
    skip_words = {"Pull", "Push", "Leg", "Day", "Today", "Planning"}
    exercises = [e for e in exercises if e not in skip_words]

    # 4. Get progressive overload for each exercise
    overload_data = format_overload_recommendations(exercises) if exercises else "No specific exercises detected."

    # 5. Generate coaching response
    llm = get_llm()
    chain = SESSION_COACH_PROMPT | llm | StrOutputParser()

    response = chain.invoke({
        "planned_session": planned_session,
        "history_context": history_context,
        "freshness_report": freshness_report,
        "overload_data": overload_data,
        "undertrained": ", ".join(undertrained) if undertrained else "None — great balance!",
    })

    return response


if __name__ == "__main__":
    print("=" * 60)
    print("FITMIND SESSION COACH TEST")
    print("=" * 60)

    # Test 1 — Pull day
    response = session_coach(
        "Pull day today. Planning Lat Pulldown, Seated Cable Row, "
        "Face Pulls, Barbell Curl, Hammer Curl"
    )
    print("\nCoach Response:")
    print(response)

    print("\n" + "=" * 60)

    # Test 2 — Push day
    response = session_coach(
        "Push day. Thinking Bench Press, Overhead Press, "
        "Lateral Raises, Tricep Pushdown"
    )
    print("\nCoach Response:")
    print(response)
