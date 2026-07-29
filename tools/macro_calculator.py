from config.settings import (
    USER_WEIGHT_KG,
    USER_HEIGHT_CM,
    USER_AGE,
    USER_GOAL,
    PROTEIN_PER_KG,
    CALORIE_SURPLUS_BULK,
    CALORIE_DEFICIT_CUT
)


def calculate_tdee() -> int:
    """
    Mifflin-St Jeor formula for BMR
    then multiply by activity factor for TDEE.
    """
    # BMR for male
    bmr = (10 * USER_WEIGHT_KG) + (6.25 * USER_HEIGHT_CM) - (5 * USER_AGE) + 5

    # Activity multiplier — 4 days training per week
    activity_factor = 1.55

    tdee = int(bmr * activity_factor)
    return tdee


def calculate_targets() -> dict:
    """
    Calculate daily macro targets based on goal.
    """
    tdee = calculate_tdee()

    if USER_GOAL == "bulk":
        calories = tdee + CALORIE_SURPLUS_BULK
    elif USER_GOAL == "cut":
        calories = tdee - CALORIE_DEFICIT_CUT
    else:
        # recomposition or strength
        calories = tdee

    protein_g = int(USER_WEIGHT_KG * PROTEIN_PER_KG)
    fat_g = int((calories * 0.25) / 9)
    carbs_g = int((calories - (protein_g * 4) - (fat_g * 9)) / 4)

    return {
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "tdee": tdee,
        "goal": USER_GOAL,
    }


def calculate_remaining(consumed: dict, targets: dict) -> dict:
    """
    Calculate what's still needed for the day.
    """
    return {
        "calories": targets["calories"] - consumed.get("calories", 0),
        "protein_g": targets["protein_g"] - consumed.get("protein_g", 0),
        "carbs_g": targets["carbs_g"] - consumed.get("carbs_g", 0),
        "fat_g": targets["fat_g"] - consumed.get("fat_g", 0),
    }


def format_targets() -> str:
    targets = calculate_targets()
    return f"""Daily macro targets ({targets['goal']} goal):
  Calories : {targets['calories']} kcal
  Protein  : {targets['protein_g']}g
  Carbs    : {targets['carbs_g']}g
  Fat      : {targets['fat_g']}g"""


if __name__ == "__main__":
    print(format_targets())
