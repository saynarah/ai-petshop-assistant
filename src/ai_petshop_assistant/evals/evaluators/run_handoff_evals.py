
import csv
import json
import uuid

from pathlib import Path

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)

from ai_petshop_assistant.dependencies import get_agent
from ai_petshop_assistant.evals.evaluators.handoff_evaluator import (
    evaluate_handoff,
    calculate_handoff_metrics,
)


EVAL_DIR = Path("src/ai_petshop_assistant/evals")

DATASET_PATH = (
    EVAL_DIR / "datasets" / "petstop_eval_dataset_v2.jsonl"
)

RESULTS_PATH = (
    EVAL_DIR / "results" / "handoff_eval_v2.csv"
)


def load_dataset() -> list[dict]:
    with DATASET_PATH.open(
        encoding="utf-8"
    ) as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def prepare_history(agent, customer_id, messages):
    history = agent._get_customer_history(customer_id)

    history.clear()

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role in ("user", "human"):
            history.add_message(
                HumanMessage(content=content)
            )

        elif role in ("assistant", "ai"):
            history.add_message(
                AIMessage(content=content)
            )

        else:
            raise ValueError(
                f"Unsupported message role: {role}"
            )

    return history


def run_handoff_evals():

    agent = get_agent()
    dataset = load_dataset()

    results = []
    evaluation_results = []

    run_id = uuid.uuid4().hex[:8]

    for case in dataset:

        case_id = case["id"]
        customer_id = f"eval-{run_id}-{case_id}"

        history = prepare_history(
            agent=agent,
            customer_id=customer_id,
            messages=case.get("chat_history", []),
        )

        try:
            response = agent.ask(
                customer_id=customer_id,
                question=case["question"],
                message_id=f"eval-msg-{run_id}-{case_id}",
                use_advanced=False,
            )

            evaluation = evaluate_handoff(
                expected=case["needs_human_review"],
                predicted=response.needs_human_review,
            )

            evaluation_results.append(evaluation)

            results.append({
                "id": case_id,
                "category": case["category"],
                "question": case["question"],
                "answer": response.reply,
                "expected_handoff": evaluation["expected"],
                "predicted_handoff": evaluation["predicted"],
                "correct": evaluation["correct"],
                "confidence": response.confidence,
            })

            print(
                f"{case_id} | "
                f"Expected: {evaluation['expected']} | "
                f"Predicted: {evaluation['predicted']} | "
                f"Correct: {evaluation['correct']}"
            )

        finally:
            history.clear()

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with RESULTS_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )

        writer.writeheader()
        writer.writerows(results)

    metrics = calculate_handoff_metrics(
        evaluation_results
    )

    print("\n=== HUMAN HANDOFF EVALUATION ===")
    print(f"Cases: {metrics['total']}")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(
        "False Negative Rate: "
        f"{metrics['false_negative_rate']:.2%}"
    )

    print("\n=== CONFUSION MATRIX ===")
    print(f"TP: {metrics['tp']}")
    print(f"TN: {metrics['tn']}")
    print(f"FP: {metrics['fp']}")
    print(f"FN: {metrics['fn']}")

    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    run_handoff_evals()
