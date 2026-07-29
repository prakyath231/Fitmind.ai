from retrieval.hybrid_retriever import hybrid_search, format_context

print("=" * 60)
print("FITMIND HYBRID RETRIEVAL TEST")
print("=" * 60)

# Test 1 - semantic query
print("\nTEST 1: Semantic query")
results = hybrid_search("when did I feel tired after training")
context = format_context(results)
print(context[:500])

# Test 2 - exact keyword query
print("\nTEST 2: Exact keyword query")
results = hybrid_search("bench press chest day")
context = format_context(results)
print(context[:500])

# Test 3 - nutrition query
print("\nTEST 3: Nutrition query")
results = hybrid_search("protein intake meals")
context = format_context(results)
print(context[:500])

# Test 4 - muscle group query
print("\nTEST 4: Muscle group query")
results = hybrid_search("back biceps pull day")
context = format_context(results)
print(context[:500])
