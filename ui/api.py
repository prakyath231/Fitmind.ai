import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage

from agents.router import classify_intent
from tools.muscle_freshness import get_muscle_freshness, get_undertrained_muscles, format_freshness_report
from tools.macro_calculator import calculate_targets, calculate_remaining, format_targets
from tools.usda_api import estimate_macros
from tools.overload_calculator import format_overload_recommendations
from tools.log_extractor import extract_log
from memory.auto_ingest import auto_ingest_log, build_confirmation_message
from retrieval.hybrid_retriever import hybrid_search, format_context
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL, USER_GOAL, TRAINING_DAYS_PER_WEEK

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=4)


class ChatRequest(BaseModel):
    message: str


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
        streaming=True,
    )


def build_system_prompt(message: str, intent: str) -> str:
    results = hybrid_search(message, k=5)
    history = format_context(results)
    freshness = get_muscle_freshness()
    freshness_report = format_freshness_report(freshness)
    undertrained = get_undertrained_muscles(freshness, threshold_days=7)
    undertrained_str = ", ".join(undertrained) if undertrained else "None"
    targets = calculate_targets()

    if intent == "SESSION_COACH":
        exercise_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', message)
        skip_words = {"Pull", "Push", "Leg", "Day", "Today", "Planning", "Doing"}
        exercises = [e for e in exercise_matches if e not in skip_words]
        overload = format_overload_recommendations(exercises) if exercises else "No specific exercises detected."
        prompt = "You are FitMind Session Coach. Give progressive overload targets, exercise order, overtraining warnings and missing exercise suggestions. Be specific with weights from history. Format clearly with sections.\n\n"
        prompt += "Training history:\n" + history + "\n\n"
        prompt += "Muscle recovery:\n" + freshness_report + "\n\n"
        prompt += "Undertrained muscles (7+ days): " + undertrained_str + "\n\n"
        prompt += "Progressive overload data:\n" + overload
        return prompt

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
        prompt = "You are FitMind Nutrition Coach. Track meals, show running totals and nudge toward daily targets. Be concise and specific.\n\n"
        prompt += "Meal estimate: " + str(meal_macros["protein_g"]) + "g protein, " + str(meal_macros["calories"]) + " kcal (" + str(meal_macros["source"]) + ")\n"
        prompt += "Running total today: " + str(updated["protein_g"]) + "g protein, " + str(updated["calories"]) + " kcal\n"
        prompt += "Still needed: " + str(remaining["protein_g"]) + "g protein, " + str(remaining["calories"]) + " kcal\n"
        prompt += "Daily targets: " + format_targets() + "\n\n"
        prompt += "History:\n" + history
        return prompt

    elif intent == "PROGRESS":
        prompt = "You are FitMind Progress Coach. Analyse training and nutrition history and give a weekly progress report covering consistency, muscle balance, nutrition averages, wins and focus areas.\n\n"
        prompt += "History:\n" + history + "\n\n"
        prompt += "Muscle status:\n" + freshness_report + "\n\n"
        prompt += "Undertrained: " + undertrained_str + "\n\n"
        prompt += "Targets: " + format_targets()
        return prompt

    elif intent == "PLANNER":
        prompt = "You are FitMind Weekly Planner. Create a personalised " + str(TRAINING_DAYS_PER_WEEK) + "-day workout plan based on goal and recovery status. List 4-5 exercises per day.\n\n"
        prompt += "Goal: " + str(USER_GOAL) + "\n"
        prompt += "Training days: " + str(TRAINING_DAYS_PER_WEEK) + "\n\n"
        prompt += "History:\n" + history + "\n\n"
        prompt += "Recovery:\n" + freshness_report
        return prompt

    else:
        prompt = "You are FitMind, a personal AI fitness coach. Answer based on the user training history. Be specific and helpful.\n\n"
        prompt += "History:\n" + history
        return prompt


@app.post("/chat/stream")
async def stream_chat(req: ChatRequest):
    loop = asyncio.get_event_loop()

    async def generate():
        try:
            extracted = await loop.run_in_executor(executor, extract_log, req.message)

            if extracted.get("is_log"):
                yield "data: " + json.dumps({"type": "intent", "intent": "LOG"}) + "\n\n"
                success = await loop.run_in_executor(executor, auto_ingest_log, extracted)
                if success:
                    confirmation = build_confirmation_message(extracted)
                    full_response = "Got it! Your log has been saved.\n\n**" + confirmation + "**\n\nYour data is now indexed — ask me anything about it!"
                else:
                    full_response = "Sorry, I had trouble saving your log. Please try again."
                for char in full_response:
                    yield "data: " + json.dumps({"type": "token", "token": char}) + "\n\n"
                    await asyncio.sleep(0.01)
                yield "data: " + json.dumps({"type": "done"}) + "\n\n"
                return

            intent = await loop.run_in_executor(executor, classify_intent, req.message)
            yield "data: " + json.dumps({"type": "intent", "intent": intent}) + "\n\n"

            system_prompt = await loop.run_in_executor(executor, build_system_prompt, req.message, intent)

            llm = get_llm()
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=req.message)
            ]

            await asyncio.sleep(0.15)

            first_token = True
            async for chunk in llm.astream(messages):
                token = chunk.content
                if token:
                    if first_token:
                        await asyncio.sleep(0.05)
                        first_token = False
                    yield "data: " + json.dumps({"type": "token", "token": token}) + "\n\n"

            yield "data: " + json.dumps({"type": "done"}) + "\n\n"

        except Exception as e:
            print("Stream error: " + str(e))
            yield "data: " + json.dumps({"type": "token", "token": "Sorry, something went wrong. Please try again."}) + "\n\n"
            yield "data: " + json.dumps({"type": "done"}) + "\n\n"

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