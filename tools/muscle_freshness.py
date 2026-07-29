import pickle
from datetime import datetime, timedelta
from config.settings import BM25_INDEX_PATH


def get_muscle_freshness() -> dict:
    """
    Reads all logs and calculates how many days ago
    each muscle group was last trained.

    Returns dict like:
    {
        "Chest": 2,
        "Back": 4,
        "Shoulders": 9,
        "Legs": 11,
        ...
    }
    """
    try:
        with open(BM25_INDEX_PATH, "rb") as f:
            data = pickle.load(f)
        documents = data["documents"]
    except FileNotFoundError:
        print("No BM25 index found. Run ingest.py first.")
        return {}

    today = datetime.today()
    muscle_last_trained = {}

    for doc in documents:
        metadata = doc.metadata
        muscles = metadata.get("muscles_trained", [])
        date_str = metadata.get("date", "unknown")
        is_rest = metadata.get("is_rest_day", False)

        if is_rest or not muscles or date_str == "unknown":
            continue

        try:
            trained_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        for muscle in muscles:
            muscle = muscle.strip()
            if muscle not in muscle_last_trained:
                muscle_last_trained[muscle] = trained_date
            else:
                if trained_date > muscle_last_trained[muscle]:
                    muscle_last_trained[muscle] = trained_date

    # Convert to days ago
    freshness = {}
    for muscle, last_date in muscle_last_trained.items():
        days_ago = (today - last_date).days
        freshness[muscle] = days_ago

    return freshness


def get_fresh_muscles(freshness: dict, min_days: int = 2) -> list:
    """
    Returns muscles that have rested enough to train again.
    Default: muscles rested 2+ days are ready.
    """
    return [
        muscle for muscle, days in freshness.items()
        if days >= min_days
    ]


def get_undertrained_muscles(freshness: dict, threshold_days: int = 7) -> list:
    """
    Returns muscles not trained in threshold_days.
    These are being neglected.
    """
    return [
        muscle for muscle, days in freshness.items()
        if days >= threshold_days
    ]


def format_freshness_report(freshness: dict) -> str:
    """
    Formats muscle freshness into a readable report
    for the LLM prompt.
    """
    if not freshness:
        return "No muscle training history found."

    lines = ["Muscle group recovery status:"]
    for muscle, days in sorted(freshness.items(), key=lambda x: x[1]):
        if days == 0:
            status = "trained TODAY"
        elif days == 1:
            status = "trained yesterday - needs rest"
        elif days <= 2:
            status = f"{days} days ago - still recovering"
        elif days <= 5:
            status = f"{days} days ago - ready to train"
        else:
            status = f"{days} days ago - UNDERTRAINED, needs attention"

        lines.append(f"  {muscle}: {status}")

    return "\n".join(lines)


if __name__ == "__main__":
    freshness = get_muscle_freshness()
    print(format_freshness_report(freshness))
    print("\nUndertrained muscles:", get_undertrained_muscles(freshness))
