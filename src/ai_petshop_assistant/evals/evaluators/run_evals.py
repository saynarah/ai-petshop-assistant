
import csv
import json
from pathlib import Path
import time

from langchain_core.messages import HumanMessage, AIMessage

from ai_petshop_assistant.dependencies import get_agent


DATASET_PATH = Path("src/ai_petshop_assistant/evals/datasets/petstop_eval_dataset_v1.jsonl")


def load_dataset() -> list[dict]:
    with DATASET_PATH.open(
        "r", encoding="utf-8"
    ) as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def build_chat_history(messages: list[dict]) -> list:
    history = []

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role in ("user", "human"):
            history.append(HumanMessage(content=content))
        elif role in ("assistant", "ai"):
            history.append(AIMessage(content=content))
        else:
            raise ValueError(f"Unknown role: {role}")

    return history


def calculate_recall(
    expected_sources: list[str],
    retrieved_sources: list[str],
) -> float:

    expected = set(expected_sources)
    retrieved = set(retrieved_sources)

    if not expected:
        raise ValueError(
            "Eval case must define expected_sources"
        )

    relevant_found = expected.intersection(retrieved)

    return len(relevant_found) / len(expected)

from collections import defaultdict


def analyze_results_by_category(results: list[dict]):

    grouped = defaultdict(list)

    for result in results:
        grouped[result["category"]].append(
            result["recall"]
        )

    print("\n=== RECALL BY CATEGORY ===")

    for category, scores in grouped.items():
        average = sum(scores) / len(scores)

        print(
            f"{category}: "
            f"{average:.2%} "
            f"({len(scores)} cases)"
        )

for k in [3,5]:
    def run_evaluations():
        agent = get_agent()
        dataset = load_dataset()

        simple_retriever = agent._build_retriever(
            k=k
        )

        history_retriever = (
            agent._build_history_aware_retriever(
                k=k
            )
        )

        results = []

        for case in dataset:

            question = case["question"]
            history = build_chat_history(
                case.get("chat_history_json", [])
            )

            if history:
                docs = history_retriever.invoke({
                    "input": question,
                    "chat_history": history,
                })
            else:
                docs = simple_retriever.invoke(question)

            expected_sources = case["expected_sources"]

            retrieved_sources = sorted({
                doc.metadata.get("source", "")
                for doc in docs
            })

            recall = calculate_recall(
                expected_sources=expected_sources,
                retrieved_sources=retrieved_sources,
            )

            missing_sources = sorted(
                set(expected_sources) - set(retrieved_sources)
            )

            result = {
                "id": case["id"],
                "category": case["category"],
                "question": question,
                "recall": recall,
                "chunks_retrieved": len(docs),
                "expected_sources": "|".join(expected_sources),
                "retrieved_sources": "|".join(retrieved_sources),
                "missing_sources": "|".join(missing_sources),
            }

            results.append(result)

            print(
                f"{case['id']} | "
                f"Recall: {recall:.2f} | "
                f"Chunks: {len(docs)}"
            )

        RESULTS_PATH = Path(f"src/ai_petshop_assistant/evals/results/retrieval_k{k}_v1.csv")
        
        RESULTS_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with RESULTS_PATH.open(
            "w", newline="", encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=results[0].keys(),
            )

            writer.writeheader()
            writer.writerows(results)

        average_recall = sum(
            result["recall"] for result in results) / len(results)

        print("\n=== EVALUATION SUMMARY ===")
        print(f"Cases evaluated: {len(results)}")
        print(f"Retrieval Recall@{k}: {average_recall:.2%}")
        print(f"Results saved to: {RESULTS_PATH}")

        analyze_results_by_category(results)


def run_evaluations_multiquery_and_history_aware(
        k: int = 3,
        use_advanced: bool = False
):
    agent = get_agent()
    dataset = load_dataset()

    simple_retriever = agent._build_retriever(
        use_advanced=use_advanced,
        k=k
    )

    history_retriever = (
        agent._build_history_aware_retriever(
            use_advanced=use_advanced,
            k=k
        )
    )

    results = []

    for case in dataset:

        question = case["question"]
        history = build_chat_history(
            case.get("chat_history_json", [])
        )

        start = time.perf_counter()

        if history:
            docs = history_retriever.invoke({
                "input": question,
                "chat_history": history,
            })
        else:
            docs = simple_retriever.invoke(question)

        retrieval_latency = time.perf_counter() - start

        expected_sources = case["expected_sources"]

        retrieved_sources = sorted({
            doc.metadata.get("source", "")
            for doc in docs
        })

        recall = calculate_recall(
            expected_sources=expected_sources,
            retrieved_sources=retrieved_sources,
        )

        missing_sources = sorted(
            set(expected_sources) - set(retrieved_sources)
        )

        result = {
            "id": case["id"],
            "category": case["category"],
            "question": question,
            "recall": recall,
            "chunks_retrieved": len(docs),
            "expected_sources": "|".join(expected_sources),
            "retrieved_sources": "|".join(retrieved_sources),
            "missing_sources": "|".join(missing_sources),
            "retrieval_latency_seconds": round(retrieval_latency,3)
        }

        results.append(result)

        print(
            f"{case['id']} | "
            f"Recall: {recall:.2f} | "
            f"Chunks: {len(docs)}"
        )

    RESULTS_PATH = Path(f"src/ai_petshop_assistant/evals/results/retrieval_multiquery_k{k}_v1.csv")

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with RESULTS_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )

        writer.writeheader()
        writer.writerows(results)

    average_recall = sum(
        result["recall"] for result in results) / len(results)

    print("\n=== EVALUATION SUMMARY ===")
    print(f"Cases evaluated: {len(results)}")
    print(f"Retrieval Recall@{k}: {average_recall:.2%}")
    print(f"Results saved to: {RESULTS_PATH}")

    analyze_results_by_category(results)


if __name__ == "__main__":
    # results = run_evaluations()
    results = run_evaluations_multiquery_and_history_aware(3, use_advanced=True)
    
