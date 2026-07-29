from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from retrieval.hybrid_retriever import hybrid_search, format_context
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL

# ── LLM ──
def get_llm():
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=0,
    )

# ── PROMPT ──
SYSTEM_PROMPT = """
You are FitMind — a personal AI fitness coach with access 
to the user's complete workout and nutrition history.

Rules:
- Answer ONLY using the context provided below
- Be specific — mention exact exercises, weights, dates
- If data is missing, say so honestly
- Give actionable advice based on the data
- Keep answers concise and motivating

User profile:
- Goal: Muscle gain + fat loss (recomposition)
- Training: 4 days per week
- Protein target: 150g per day
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """Here is the relevant data from your logs:

{context}

Question: {question}

Answer as FitMind coach:""")
])

# ── RAG CHAIN ──
def ask(question: str) -> str:
    """
    Full RAG chain:
    1. Hybrid search your logs
    2. Format retrieved chunks as context
    3. Pass to Mistral with prompt
    4. Return answer
    """
    print(f"\nQuestion: {question}")
    print("-" * 50)

    # 1. Retrieve
    results = hybrid_search(question)

    # 2. Format context
    context = format_context(results)

    # 3. Generate
    llm = get_llm()
    chain = PROMPT_TEMPLATE | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": question
    })

    return answer


if __name__ == "__main__":
    questions = [
        "What did I train last chest day and what weight did I use on bench press?",
        "Am I hitting my protein target consistently?",
        "Which muscle groups am I neglecting?",
        "How was my energy and mood this week?",
        "What should I focus on improving?",
    ]

    print("\n" + "="*60)
    print("FITMIND RAG CHAIN TEST")
    print("="*60)

    for q in questions:
        answer = ask(q)
        print(f"\nAnswer: {answer}")
        print("="*60)
