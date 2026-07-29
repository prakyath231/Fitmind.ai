import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.graph import chat

print("=" * 60)
print("FITMIND MULTI-AGENT SYSTEM")
print("=" * 60)
print("Type your message. Type 'quit' to exit.")
print("=" * 60)

while True:
    message = input("\nYou: ").strip()
    if message.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    if not message:
        continue
    response = chat(message)
    print(f"\nFitMind: {response}")
