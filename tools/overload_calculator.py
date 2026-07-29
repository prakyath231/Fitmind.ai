import pickle
import re
from config.settings import (
    BM25_INDEX_PATH,
    OVERLOAD_INCREMENT_KG,
    OVERLOAD_TARGET_REPS
)


def get_last_session_for_exercise(exercise_name: str) -> dict:
    """
    Searches logs for the last time this exercise was performed.
    Returns weight, sets, reps from that session.
    """
    try:
        with open(BM25_INDEX_PATH, "rb") as f:
            data = pickle.load(f)
        documents = data["documents"]
    except FileNotFoundError:
        return {}

    exercise_lower = exercise_name.lower()
    best_match = None
    best_date = None

    for doc in documents:
        content = doc.page_content.lower()
        date_str = doc.metadata.get("date", "unknown")

        if exercise_lower not in content:
            continue

        # Find the exercise line
        pattern = rf"{re.escape(exercise_lower)}[:\s]+([\d.]+)\s*kg[,\s]+([\d]+)\s*sets?\s*[x×]\s*([\d]+)\s*reps?"
        match = re.search(pattern, content)

        if match:
            weight = float(match.group(1))
            sets = int(match.group(2))
            reps = int(match.group(3))

            if best_date is None or date_str > best_date:
                best_date = date_str
                best_match = {
                    "exercise": exercise_name,
                    "date": date_str,
                    "weight_kg": weight,
                    "sets": sets,
                    "reps": reps,
                }

    return best_match or {}


def calculate_progressive_overload(exercise_name: str) -> dict:
    """
    Calculates the recommended weight for today
    based on last session performance.

    Logic:
    - If last session hit target reps → increase weight
    - If last session missed reps → keep same weight
    - If no history → suggest starting weight
    """
    last = get_last_session_for_exercise(exercise_name)

    if not last:
        return {
            "exercise": exercise_name,
            "recommendation": "No history found. Start with a comfortable weight and focus on form.",
            "suggested_weight": None,
            "last_weight": None,
        }

    last_weight = last["weight_kg"]
    last_reps = last["reps"]
    last_sets = last["sets"]

    if last_reps >= OVERLOAD_TARGET_REPS:
        suggested = last_weight + OVERLOAD_INCREMENT_KG
        recommendation = (
            f"Last session: {last_weight}kg x {last_sets}x{last_reps} "
            f"on {last['date']}. You hit your target reps! "
            f"Increase to {suggested}kg today."
        )
    else:
        suggested = last_weight
        recommendation = (
            f"Last session: {last_weight}kg x {last_sets}x{last_reps} "
            f"on {last['date']}. Keep the same weight and aim for "
            f"{OVERLOAD_TARGET_REPS} reps before increasing."
        )

    return {
        "exercise": exercise_name,
        "recommendation": recommendation,
        "suggested_weight": suggested,
        "last_weight": last_weight,
        "last_reps": last_reps,
        "last_date": last["date"],
    }


def format_overload_recommendations(exercises: list) -> str:
    """
    Formats progressive overload recommendations
    for a list of exercises into LLM-readable text.
    """
    lines = ["Progressive overload recommendations:"]
    for exercise in exercises:
        result = calculate_progressive_overload(exercise)
        lines.append(f"\n{result['exercise']}:")
        lines.append(f"  {result['recommendation']}")
    return "\n".join(lines)


if __name__ == "__main__":
    exercises = ["Bench Press", "Lat Pulldown", "Squat"]
    print(format_overload_recommendations(exercises))
