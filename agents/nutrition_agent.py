from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from retrieval.hybrid_retriever import hybrid_search, format_context
from tools.macro_calculator import calculate_targets, calculate_remaining, format_targets
from tools.usda_api import estimate_macros
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL


def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
    )


NUTRITION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are FitMind Nutrition Coach.
Your job: track meals, estimate macros, and nudge the 
user toward their daily targets.

Always:
- Show running totals clearly
- Show what is still needed
- Give specific food suggestions to hit remaining targets
- Be encouraging but honest about gaps
- Keep it concise"""),

    ("human", """User logged: {meal_input}

Macro estimate for this meal:
{meal_macros}

Today's running total (from logs):
{todays_total}

Daily targets:
{targets}

Remaining to hit today:
{remaining}

Nutrition history context:
{history_context}

Give your nutrition coaching response:""")
])


def get_todays_total() -> dict:
    """
    Gets today's macro total from logs.
    In production this would track within-day entries.
    For now returns from most recent log entry.
    """
    results = hybrid_search("today nutrition meals protein calories", k=1)

    if not results:
        return {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

    doc = results[0][0]
    metadata = doc.metadata

    return {
        "calories": metadata.get("calories", 0),
        "protein_g": metadata.get("protein_g", 0),
        "carbs_g": metadata.get("carbs_g", 0),
        "fat_g": metadata.get("fat_g", 0),
    }


def nutrition_coach(meal_input: str) -> str:
    """
    User logs a meal — agent estimates macros,
    updates running total, gives nudges.
    """
    print(f"\nNutrition Coach activated...")
    print(f"Meal logged: {meal_input}")
    print("-" * 50)

    # 1. Estimate macros for this meal
    meal_macros = estimate_macros(meal_input)

    # 2. Get today's running total
    todays_total = get_todays_total()

    # 3. Get targets
    targets = calculate_targets()

    # 4. Calculate remaining
    # Add this meal to today's total
    updated_total = {
        "calories": todays_total["calories"] + meal_macros["calories"],
        "protein_g": todays_total["protein_g"] + meal_macros["protein_g"],
        "carbs_g": todays_total["carbs_g"] + meal_macros["carbs_g"],
        "fat_g": todays_total["fat_g"] + meal_macros["fat_g"],
    }
    remaining = calculate_remaining(updated_total, targets)

    # 5. Get history context
    history_results = hybrid_search(f"nutrition protein {meal_input}", k=2)
    history_context = format_context(history_results)

    # 6. Format for prompt
    meal_macros_str = (
        f"  Calories : {meal_macros['calories']} kcal\n"
        f"  Protein  : {meal_macros['protein_g']}g\n"
        f"  Carbs    : {meal_macros['carbs_g']}g\n"
        f"  Fat      : {meal_macros['fat_g']}g\n"
        f"  Source   : {meal_macros['source']}"
    )

    todays_total_str = (
        f"  Calories : {updated_total['calories']} kcal\n"
        f"  Protein  : {updated_total['protein_g']}g\n"
        f"  Carbs    : {updated_total['carbs_g']}g\n"
        f"  Fat      : {updated_total['fat_g']}g"
    )

    remaining_str = (
        f"  Calories : {remaining['calories']} kcal\n"
        f"  Protein  : {remaining['protein_g']}g still needed\n"
        f"  Carbs    : {remaining['carbs_g']}g\n"
        f"  Fat      : {remaining['fat_g']}g"
    )

    # 7. Generate response
    llm = get_llm()
    chain = NUTRITION_PROMPT | llm | StrOutputParser()

    response = chain.invoke({
        "meal_input": meal_input,
        "meal_macros": meal_macros_str,
        "todays_total": todays_total_str,
        "targets": format_targets(),
        "remaining": remaining_str,
        "history_context": history_context,
    })

    return response


if __name__ == "__main__":
    print("=" * 60)
    print("FITMIND NUTRITION AGENT TEST")
    print("=" * 60)

    meals = [
        "4 eggs and 2 bread slices for breakfast",
        "chicken rice bowl for lunch",
        "greek yoghurt snack",
    ]

    for meal in meals:
        response = nutrition_coach(meal)
        print(f"\nCoach: {response}")
        print("=" * 60)
