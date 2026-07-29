import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import chainlit as cl
from concurrent.futures import ThreadPoolExecutor


# Thread pool for running sync agent code
executor = ThreadPoolExecutor(max_workers=4)


def run_chat(message: str) -> str:
    """Runs the sync agent in a thread."""
    from agents.graph import chat
    return chat(message)


def run_intent(message: str) -> str:
    """Runs intent classifier in a thread."""
    from agents.router import classify_intent
    return classify_intent(message)


def get_stats() -> dict:
    """Gets startup stats in a thread."""
    from tools.muscle_freshness import get_muscle_freshness, get_undertrained_muscles
    from tools.macro_calculator import calculate_targets
    freshness = get_muscle_freshness()
    undertrained = get_undertrained_muscles(freshness, threshold_days=7)
    targets = calculate_targets()
    return {"undertrained": undertrained, "targets": targets}


# ON CHAT START
@cl.on_chat_start
async def on_start():
    loop = asyncio.get_event_loop()

    try:
        stats = await loop.run_in_executor(executor, get_stats)
        undertrained = stats["undertrained"]
        targets = stats["targets"]
        undertrained_str = ", ".join(undertrained) if undertrained else "None - great balance!"

        welcome = f"""## Hey Prakyath! \U0001f4aa

**Protein target:** {targets['protein_g']}g / day
**Calorie target:** {targets['calories']} kcal / day
**Goal:** {targets['goal'].title()}
**Muscles needing attention:** {undertrained_str}

---
Try asking me:
- *"Pull day today - lat pulldown, rows, bicep curls"*
- *"Had chicken rice for lunch"*
- *"How am I doing this week?"*
- *"Plan my workouts for next week"*
"""
    except Exception as e:
        welcome = """## Hey! I am FitMind \U0001f4aa

Your personal AI fitness coach. Ask me anything!

- *"Pull day today - lat pulldown, rows, bicep curls"*
- *"Had chicken rice for lunch"*
- *"How am I doing this week?"*
- *"Plan my workouts for next week"*
"""

    await cl.Message(content=welcome).send()


# ON MESSAGE
@cl.on_message
async def on_message(message: cl.Message):
    loop = asyncio.get_event_loop()

    async with cl.Step(name="FitMind Agent") as step:

        # Classify intent
        step.output = "Classifying your message..."
        await step.update()

        intent = await loop.run_in_executor(
            executor,
            run_intent,
            message.content
        )

        intent_labels = {
            "SESSION_COACH": "Workout Session Coach",
            "NUTRITION": "Nutrition Coach",
            "PROGRESS": "Progress Analysis",
            "PLANNER": "Weekly Planner",
            "GENERAL": "General Coach",
        }

        label = intent_labels.get(intent, "Coach")
        step.output = f"Routing to {label}..."
        await step.update()

        # Run agent
        step.output = f"Searching your training history..."
        await step.update()

        response = await loop.run_in_executor(
            executor,
            run_chat,
            message.content
        )

        step.output = f"Done - handled by {label}"

    await cl.Message(content=response).send()
