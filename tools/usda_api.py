import requests
import os
from config.settings import USDA_API_KEY, USDA_BASE_URL


# Common Indian foods — hardcoded fallback
# because USDA doesn't have all Indian foods
INDIAN_FOOD_DB = {
    "chicken rice": {"calories": 620, "protein_g": 52, "carbs_g": 68, "fat_g": 12},
    "chicken rice bowl": {"calories": 620, "protein_g": 52, "carbs_g": 68, "fat_g": 12},
    "dal rice": {"calories": 450, "protein_g": 18, "carbs_g": 78, "fat_g": 6},
    "paneer curry": {"calories": 380, "protein_g": 22, "carbs_g": 18, "fat_g": 24},
    "chapati": {"calories": 120, "protein_g": 3, "carbs_g": 22, "fat_g": 2},
    "roti": {"calories": 120, "protein_g": 3, "carbs_g": 22, "fat_g": 2},
    "egg": {"calories": 70, "protein_g": 6, "carbs_g": 0, "fat_g": 5},
    "eggs": {"calories": 70, "protein_g": 6, "carbs_g": 0, "fat_g": 5},
    "4 eggs": {"calories": 280, "protein_g": 24, "carbs_g": 0, "fat_g": 20},
    "oats": {"calories": 150, "protein_g": 5, "carbs_g": 27, "fat_g": 3},
    "banana": {"calories": 90, "protein_g": 1, "carbs_g": 23, "fat_g": 0},
    "greek yoghurt": {"calories": 100, "protein_g": 17, "carbs_g": 6, "fat_g": 0},
    "peanut butter": {"calories": 190, "protein_g": 8, "carbs_g": 6, "fat_g": 16},
    "milk": {"calories": 150, "protein_g": 8, "carbs_g": 12, "fat_g": 8},
    "biryani": {"calories": 500, "protein_g": 22, "carbs_g": 65, "fat_g": 14},
    "bread": {"calories": 80, "protein_g": 3, "carbs_g": 15, "fat_g": 1},
    "rice": {"calories": 200, "protein_g": 4, "carbs_g": 44, "fat_g": 0},
    "chicken": {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 4},
    "protein shake": {"calories": 120, "protein_g": 25, "carbs_g": 3, "fat_g": 1},
    "whey protein": {"calories": 120, "protein_g": 25, "carbs_g": 3, "fat_g": 1},
}


def estimate_macros(food_description: str) -> dict:
    """
    Estimates macros for a food item.
    First checks Indian food database.
    Then tries USDA API.
    Falls back to LLM estimation if both fail.
    """
    food_lower = food_description.lower().strip()

    # Check Indian food DB first
    for key, macros in INDIAN_FOOD_DB.items():
        if key in food_lower:
            return {
                "food": food_description,
                "source": "local_db",
                **macros
            }

    # Try USDA API if key available
    if USDA_API_KEY and USDA_API_KEY != "your_usda_key_here":
        try:
            result = _search_usda(food_description)
            if result:
                return result
        except Exception:
            pass

    # Fallback — return estimate flag
    return {
        "food": food_description,
        "source": "estimated",
        "calories": 300,
        "protein_g": 15,
        "carbs_g": 30,
        "fat_g": 10,
        "note": "Rough estimate — update manually for accuracy"
    }


def _search_usda(query: str) -> dict:
    """Search USDA FoodData Central API."""
    url = f"{USDA_BASE_URL}/foods/search"
    params = {
        "query": query,
        "api_key": USDA_API_KEY,
        "pageSize": 1,
        "dataType": "Survey (FNDDS)"
    }

    response = requests.get(url, params=params, timeout=5)

    if response.status_code != 200:
        return {}

    data = response.json()
    foods = data.get("foods", [])

    if not foods:
        return {}

    food = foods[0]
    nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}

    return {
        "food": food.get("description", query),
        "source": "usda",
        "calories": int(nutrients.get("Energy", 0)),
        "protein_g": round(nutrients.get("Protein", 0), 1),
        "carbs_g": round(nutrients.get("Carbohydrate, by difference", 0), 1),
        "fat_g": round(nutrients.get("Total lipid (fat)", 0), 1),
    }


if __name__ == "__main__":
    test_foods = [
        "chicken rice bowl",
        "4 eggs",
        "dal rice",
        "greek yoghurt",
        "banana",
    ]
    for food in test_foods:
        result = estimate_macros(food)
        print(f"{food}: {result['protein_g']}g protein, "
              f"{result['calories']} kcal ({result['source']})")
