import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.router import classify_intent
from tools.muscle_freshness import get_muscle_freshness, get_undertrained_muscles
from tools.macro_calculator import calculate_targets
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from retrieval.hybrid_retriever import hybrid_search, format_context
from tools.muscle_freshness import get_muscle_freshness, get_undertrained_muscles, format_freshness_report
from tools.overload_calculator import format_overload_recommendations
from tools.macro_calculator import calculate_targets, calculate_remaining, format_targets
from tools.usda_api import estimate_macros
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL, USER_GOAL, TRAINING_DAYS_PER_WEEK
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
        streaming=True,
    )

def build_context(message: str, intent: str) -> dict:
    results = hybrid_search(message, k=5)
    history = format_context(results)
    freshness = get_muscle_freshness()
    freshness_report = format_freshness_report(freshness)
    undertrained = get_undertrained_muscles(freshness, threshold_days=7)
    targets = calculate_targets()

    if intent == "SESSION_COACH":
        exercise_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', message)
        skip = {"Pull","Push","Leg","Day","Today","Planning","Doing"}
        exercises = [e for e in exercise_matches if e not in skip]
        overload = format_overload_recommendations(exercises) if exercises else ""
        system = f"""You are FitMind Session Coach. Give progressive overload targets, exercise order, overtraining warnings and missing exercise suggestions. Be specific with weights from history. Format clearly with sections. Stream your response naturally.

Training history:
{history}

Muscle recovery:
{freshness_report}

Undertrained muscles (7+ days): {", ".join(undertrained) if undertrained else "None"}

Progressive overload data:
{overload}"""

    elif intent == "NUTRITION":
        meal_macros = estimate_macros(message)
        todays_total = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
        updated = {
            "calories": todays_total["calories"] + meal_macros["calories"],
            "protein_g": todays_total["protein_g"] + meal_macros["protein_g"],
            "carbs_g": todays_total["carbs_g"] + meal_macros["carbs_g"],
            "fat_g": todays_total["fat_g"] + meal_macros["fat_g"],
        }
        remaining = calculate_remaining(updated, targets)
        system = f"""You are FitMind Nutrition Coach. Track meals, show running totals and nudge toward daily targets. Be concise and specific.

Meal estimate: {meal_macros["protein_g"]}g protein, {meal_macros["calories"]} kcal ({meal_macros["source"]})
Running total today: {updated["protein_g"]}g protein, {updated["calories"]} kcal
Still needed: {remaining["protein_g"]}g protein, {remaining["calories"]} kcal
Daily targets: {format_targets()}
History: {history}"""

    elif intent == "PROGRESS":
        system = f"""You are FitMind Progress Coach. Analyse training and nutrition history and give a weekly progress report covering consistency, muscle balance, nutrition averages, wins and focus areas.

History: {history}
Muscle status: {freshness_report}
Undertrained: {", ".join(undertrained) if undertrained else "None"}
Targets: {format_targets()}"""

    elif intent == "PLANNER":
        system = f"""You are FitMind Weekly Planner. Create a personalised {TRAINING_DAYS_PER_WEEK}-day workout plan based on goal and recovery status. List 4-5 exercises per day.

Goal: {USER_GOAL}
Training days: {TRAINING_DAYS_PER_WEEK}
History: {history}
Recovery: {freshness_report}"""

    else:
        system = f"""You are FitMind, a personal AI fitness coach. Answer based on the user's training history. Be specific and helpful.

History: {history}"""

    return system

@app.post("/chat/stream")
async def stream_chat(req: ChatRequest):
    intent = classify_intent(req.message)
    system_prompt = build_context(req.message, intent)

    async def generate():
        # Send intent first
        yield f"data: {json.dumps({'type': 'intent', 'intent': intent})}\n\n"

        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", req.message)
        ])
        chain = prompt | llm

        async for chunk in chain.astream({}):
            token = chunk.content
            if token:
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/stats")
def get_stats():
    try:
        freshness = get_muscle_freshness()
        undertrained = get_undertrained_muscles(freshness, threshold_days=7)
        targets = calculate_targets()
        return {
            "protein_target": targets["protein_g"],
            "calorie_target": targets["calories"],
            "goal": targets["goal"],
            "undertrained": undertrained,
            "freshness": freshness,
        }
    except Exception as e:
        return {"error": str(e)}
