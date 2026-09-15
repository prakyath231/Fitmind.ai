import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp.server.fastmcp import FastMCP
from retrieval.hybrid_retriever import hybrid_search, format_context
from tools.muscle_freshness import get_muscle_freshness, get_undertrained_muscles, format_freshness_report
from tools.macro_calculator import calculate_targets, calculate_remaining, format_targets
from tools.overload_calculator import calculate_progressive_overload, format_overload_recommendations
from tools.usda_api import estimate_macros
from tools.log_extractor import extract_log
from memory.auto_ingest import auto_ingest_log, build_confirmation_message
import json
mcp = FastMCP("FitMind")
@mcp.tool()
def search_fitness_history(query: str) -> str:
    """
    Search the user's complete workout and nutrition history using hybrid RAG.
    Use this when the user asks about past sessions, exercises, meals, weights,
    protein intake, or any historical fitness data.
    """
    results = hybrid_search(query, k=5)
    return format_context(results)
@mcp.tool()
def get_muscle_recovery_status() -> str:
    """
    Returns how many days ago each muscle group was last trained.
    Use this to check recovery status, identify undertrained muscles,
    or warn about overtraining risk before a session.
    """
    freshness = get_muscle_freshness()
    return format_freshness_report(freshness)
@mcp.tool()
def get_undertrained_muscles_list() -> str:
    """
    Returns muscles that have not been trained in 7 or more days.
    Use this when the user asks which muscles they are neglecting
    or need to prioritise in upcoming sessions.
    """
    freshness = get_muscle_freshness()
    undertrained = get_undertrained_muscles(freshness, threshold_days=7)
    if not undertrained:
        return "No undertrained muscles - great balance!"
    return "Undertrained muscles (7+ days): " + ", ".join(undertrained)
@mcp.tool()
def get_progressive_overload(exercise_name: str) -> str:
    """
    Returns the recommended weight and sets/reps for today based on
    the user's last performance for a specific exercise.
    Use this when the user asks about weights for a specific exercise
    or wants to know if they should increase weight today.
    """
    result = calculate_progressive_overload(exercise_name)
    return result["recommendation"]
@mcp.tool()
def get_session_recommendations(planned_exercises: str) -> str:
    """
    Takes a comma-separated list of planned exercises and returns
    progressive overload targets for all of them.
    Use this when the user shares their full session plan and wants
    weight recommendations for multiple exercises at once.
    """
    exercises = [e.strip() for e in planned_exercises.split(",")]
    return format_overload_recommendations(exercises)
@mcp.tool()
def get_daily_macro_targets() -> str:
    """
    Returns the user's daily protein, calorie, carb and fat targets
    based on their goal and body weight.
    Use this when the user asks about their daily nutrition targets
    or wants to know how much they still need to eat.
    """
    return format_targets()
@mcp.tool()
def estimate_food_macros(food_description: str) -> str:
    """
    Estimates macros (protein, calories, carbs, fat) for a given food item.
    Use this when the user mentions eating something and wants to know
    the nutritional content. Supports Indian foods like dal rice, paneer,
    chicken rice bowl, roti, etc.
    """
    result = estimate_macros(food_description)
    return (
        f"Food: {result['food']}\n"
        f"Protein: {result['protein_g']}g\n"
        f"Calories: {result['calories']} kcal\n"
        f"Carbs: {result['carbs_g']}g\n"
        f"Fat: {result['fat_g']}g\n"
        f"Source: {result['source']}"
    )
@mcp.tool()
def log_workout_or_meal(user_message: str) -> str:
    """
    Extracts and saves workout or nutrition data from natural language.
    Use this when the user says they did a workout or ate something
    and wants it logged. For example: 'Did chest today, bench 65kg 4x10'
    or 'Had chicken rice for lunch'.
    """
    extracted = extract_log(user_message)
    if not extracted.get("is_log"):
        return "Could not detect a log entry in this message. Please describe your workout or meal more specifically."
    success = auto_ingest_log(extracted)
    if success:
        confirmation = build_confirmation_message(extracted)
        return "Logged successfully!\n\n" + confirmation + "\n\nYour data is now indexed and searchable."
    return "Sorry, there was an error saving your log. Please try again."
@mcp.resource("fitness://logs")
def get_all_logs() -> str:
    """Returns the complete fitness and nutrition log file."""
    try:
        with open("data/logs/daily_logs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No logs found. Start logging your workouts and meals."
@mcp.resource("fitness://targets")
def get_targets_resource() -> str:
    """Returns daily macro targets summary."""
    return format_targets()
@mcp.resource("fitness://muscles")
def get_muscle_status_resource() -> str:
    """Returns current muscle recovery status for all muscle groups."""
    freshness = get_muscle_freshness()
    return format_freshness_report(freshness)
@mcp.prompt()
def session_coach_prompt(planned_exercises: str) -> str:
    """
    Generates a session coaching prompt for the planned exercises.
    Use this to get a structured coaching response for a workout session.
    """
    return f"""You are FitMind Session Coach with access to the user's complete training history.
The user plans to train: {planned_exercises}
Your job:
1. Check their history for each exercise using search_fitness_history
2. Get progressive overload targets using get_session_recommendations
3. Check muscle recovery using get_muscle_recovery_status
4. Give specific weight/rep targets based on their actual history
5. Warn about overtraining if needed
6. Suggest exercise order (compounds first)
7. Flag any undertrained muscles they should add
Be specific with numbers. Be motivating."""
@mcp.prompt()
def nutrition_coach_prompt(meal_logged: str) -> str:
    """
    Generates a nutrition coaching prompt after a meal is logged.
    """
    return f"""You are FitMind Nutrition Coach.
The user just logged: {meal_logged}
Your job:
1. Estimate macros using estimate_food_macros
2. Get their daily targets using get_daily_macro_targets
3. Search today's logs using search_fitness_history for 'today nutrition'
4. Calculate what they still need
5. Suggest specific foods to hit their protein target
6. Keep it concise and encouraging"""
if __name__ == "__main__":
    print("Starting FitMind MCP Server...")
    mcp.run()
