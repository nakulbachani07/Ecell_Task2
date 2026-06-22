import time
import json

from train import search_document,generate_answer,calculate_confidence

test_queries = [
    "What is the attendance requirement in NIT Trichy?",
    "What are Programme Electives in B.Tech?",
    "What is the admission rule for foreign students in PG programmes?",
    "What are microcredit courses in B.Arch?",
    "Is NIT Trichy a smoking free and alcohol free campus?",
    "What is the procedure for scholarship and fee reimbursement?",
    "What is the mess menu for Monday?"
]

def evaluate_system():
    results = []

    for query in test_queries:
        print("Testing query:", query)

        start_time = time.time()

        search_results = search_document(query, top_k=5)
        answer = generate_answer(query, search_results)
        confidence = calculate_confidence(search_results)

        end_time = time.time()
        latency = round(end_time - start_time, 2)

        #create source list
        #if answer not found keep sources empty
        # otherwise, add unique sources only.
        if "could not find enough information" in answer.lower():
            sources = []
        else:
            sources = []
            used_sources = set()
 

            for result in search_results:
              source_file = result.get("source_file", "unknown")
              page_number = result.get("page_number", "unknown")

              source_key = (source_file , page_number)

              if source_key not in used_sources:
                  sources.append({
                      "source_file": source_file,
                      "page_number": page_number
                  })
                  used_sources.add(source_key)
            

        results.append({
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "latency_seconds": latency,
            "sources_found": len(sources),
            "sources": sources
        })

        print("Done")
        print("-" * 80)

    with open("evaluation_results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print("Evaluation completed.")
    print("Saved to evaluation_results.json")


if __name__ == "__main__":
    evaluate_system()
