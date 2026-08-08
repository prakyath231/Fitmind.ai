import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL
from datetime import datetime
import json
import re


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
    )


EXTRACT_SYSTEM = """You are a fitness log extractor.
Extract workout and nutrition data from the user message.
Return ONLY valid JSON. No explanation. No markdown. No code blocks.

JSON format:
{
  "is_log": true,
  "date": "YYYY-MM-DD",
  "type": "Workout",
  "muscles_trained": ["Chest", "Triceps"],
  "exercises": [
    {"name": "Bench Press", "weight_kg": 65, "sets": 4, "reps": 10}
  ],
  "meals": [
    {"time": "Lunch", "food": "Chicken rice bowl", "protein_g": 52, "calories": 620}
  ],
  "macros": {
    "protein_g": 52,
    "calories": 620,
    "carbs_g": 68,
    "fat_g": 12
  },
  "notes": "any notes mentioned",
  "mood": "strong"
}

If the message is a QUESTION or general chat — not a log — return:
{"is_log": false}

Use today date if no date is mentioned.
mood options: strong, tired, average, sore"""


def extract_log(message: str) -> dict:
    """
    Uses Mistral to extract structured log data from natural language.
    Returns dict with is_log flag and extracted data.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    llm = get_llm()

    human_text = "Today is " + today + ". Extract from this message: " + message

    messages = [
        SystemMessage(content=EXTRACT_SYSTEM),
        HumanMessage(content=human_text)
    ]

    try:
        response = llm.invoke(messages)
        result = response.content.strip()

        # Clean up any markdown code blocks if present
        if result.startswith("```"):
            result = re.sub(r"```json|```", "", result).strip()

        data = json.loads(result)
        return data

    except Exception as e:
        print(f"Extraction error: {e}")
        return {"is_log": False}


def format_log_entry(data: dict) -> str:
    """
    Converts extracted data back into the daily_logs.txt format
    for storage and ingestion.
    """
    lines = []
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    lines.append("Date: " + date_str)
    lines.append("Type: " + data.get("type", "Workout"))

    muscles = data.get("muscles_trained", [])
    if muscles:
        lines.append("Muscles Trained: " + ", ".join(muscles))

    exercises = data.get("exercises", [])
    if exercises:
        lines.append("\nExercises:")
        for ex in exercises:
            name = ex.get("name", "")
            weight = str(ex.get("weight_kg", "")) + "kg, " if ex.get("weight_kg") else ""
            sets = str(ex.get("sets", ""))
            reps = str(ex.get("reps", ""))
            lines.append("- " + name + ": " + weight + sets + " sets x " + reps + " reps")

    meals = data.get("meals", [])
    if meals:
        lines.append("\nNutrition:")
        for meal in meals:
            time = meal.get("time", "Meal")
            food = meal.get("food", "")
            lines.append("- " + time + ": " + food)

    macros = data.get("macros", {})
    if macros:
        lines.append("\nEstimated Macros:")
        if macros.get("calories"):
            lines.append("- Calories: " + str(macros["calories"]))
        if macros.get("protein_g"):
            lines.append("- Protein: " + str(macros["protein_g"]) + "g")
        if macros.get("carbs_g"):
            lines.append("- Carbs: " + str(macros["carbs_g"]) + "g")
        if macros.get("fat_g"):
            lines.append("- Fat: " + str(macros["fat_g"]) + "g")

    notes = data.get("notes", "")
    if notes:
        lines.append("\nNotes: " + notes)

    return "\n".join(lines)


if __name__ == "__main__":
    test_messages = [
        "Did chest today - bench press 65kg 4x10, incline DB 22kg 3x12. Had chicken rice for lunch.",
        "Pull day - lat pulldown 55kg, seated row 50kg, bicep curls 30kg. Felt strong!",
        "How am I doing this week?",
        "Rest day today. Had dal rice and paneer for dinner.",
    ]

    for msg in test_messages:
        print("\nMessage: " + msg)
        result = extract_log(msg)
        print("Is log: " + str(result.get("is_log")))
        if result.get("is_log"):
            print("Type: " + str(result.get("type")))
            print("Exercises: " + str(result.get("exercises")))
            print("Macros: " + str(result.get("macros")))