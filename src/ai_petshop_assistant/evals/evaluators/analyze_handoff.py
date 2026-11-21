
import csv
from pathlib import Path

RESULTS_PATH = Path(
    "src/ai_petshop_assistant/evals/results/handoff_eval_v1.csv"
)


def analyze_handoff_errors():

    with RESULTS_PATH.open(
        encoding="utf-8",
        newline="",
    ) as file:
        results = list(csv.DictReader(file))

    false_negatives = []
    false_positives = []

    for result in results:

        expected = result["expected_handoff"] == "True"
        predicted = result["predicted_handoff"] == "True"

        if expected and not predicted:
            false_negatives.append(result)

        elif not expected and predicted:
            false_positives.append(result)

    print("\n=== FALSE NEGATIVES ===")

    for case in false_negatives:
        print(f"\nCase: {case['id']}")
        print(f"Category: {case['category']}")
        print(f"Question: {case['question']}")
        print(f"Answer: {case['answer']}")
        print(f"Confidence: {case['confidence']}")

    print("\n=== FALSE POSITIVES ===")

    for case in false_positives:
        print(f"\nCase: {case['id']}")
        print(f"Category: {case['category']}")
        print(f"Question: {case['question']}")
        print(f"Answer: {case['answer']}")
        print(f"Confidence: {case['confidence']}")


if __name__ == "__main__":
    analyze_handoff_errors()
