import sys, os, asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from agents.graph import run_pipeline

TEST_QUERIES = [
    "What is retrieval augmented generation?",
    "Which authors have published papers on transformers?",
    "How do diffusion models compare to GANs for image generation?",
]

async def main():
    print("=" * 60)
    print("GraphRAG Pipeline Smoke Test")
    print("=" * 60)

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 40)
        result = await run_pipeline(query)
        print(f"Type:   {result['query_type']}")
        print(f"Winner: LLM {result['winner']} | {result['reason']}")
        print(f"Answer: {result['final_answer'][:300]}...")
        print(f"Sources: {len(result['sources'])} retrieved")
        print("-" * 40)

    print("\nAll tests passed! 🎉")

if __name__ == "__main__":
    asyncio.run(main())
