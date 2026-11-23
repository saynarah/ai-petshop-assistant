
import csv
import json
from pathlib import Path

from ai_petshop_assistant.evals.evaluators.answer_evaluator import (
    AnswerEvaluator,
)


EVAL_DIR = Path("src/ai_petshop_assistant/evals")

DATASET_PATH = (
    EVAL_DIR / "datasets" / "petstop_eval_dataset_v2.jsonl"
)

HANDOFF_RESULTS_PATH = (
    EVAL_DIR / "results" / "handoff_eval_v2.csv"
)

ANSWER_RESULTS_PATH = (
    EVAL_DIR / "results" / "answer_correctness_v1.csv"
)


def load_dataset() -> list[dict]:
    with DATASET_PATH.open(encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def load_agent_answers() -> dict[str, dict]:
    with HANDOFF_RESULTS_PATH.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    answers = {}

    for row in rows:
        case_id = row["id"]

        if case_id in answers:
            raise ValueError(
                f"Duplicate answer for case: {case_id}"
            )

        answers[case_id] = row

    return answers


def run_answer_evals():
    dataset = load_dataset()
    agent_answers = load_agent_answers()

    if not dataset:
        raise ValueError("Evaluation dataset is empty")

    case_ids = [case["id"] for case in dataset]

    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Duplicate IDs in evaluation dataset")

    if set(case_ids) != set(agent_answers):
        raise ValueError(
            "Dataset and agent answer IDs do not match"
        )

    evaluator = AnswerEvaluator()
    results = []

    for case in dataset:
        case_id = case["id"]
        answer = agent_answers[case_id]["answer"]

        if not answer.strip():
            raise ValueError(
                f"Empty agent answer for case {case_id}"
            )

        evaluation = evaluator.evaluate(
            question=case["question"],
            answer=answer,
            expected_facts=case["expected_facts"],
            forbidden_claims=case["forbidden_claims"],
        )

        results.append({
            "id": case_id,
            "category": case["category"],
            "question": case["question"],
            "answer": answer,
            "score": evaluation.score,
            "reasoning": evaluation.reasoning,
            "missing_facts": json.dumps(
                evaluation.missing_facts,
                ensure_ascii=False,
            ),
            "forbidden_claims_detected": json.dumps(
                evaluation.forbidden_claims_detected,
                ensure_ascii=False,
            ),
        })

        print(
            f"{case_id} | "
            f"Score: {evaluation.score:.1f} | "
            f"Evaluated: {len(results)}/{len(dataset)}"
        )

    ANSWER_RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ANSWER_RESULTS_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )

        writer.writeheader()
        writer.writerows(results)

    scores = [row["score"] for row in results]

    average_score = sum(scores) / len(scores)

    full_scores = sum(
        score == 1.0 for score in scores
    )

    partial_scores = sum(
        score == 0.5 for score in scores
    )

    zero_scores = sum(
        score == 0.0 for score in scores
    )

    print("\n=== ANSWER CORRECTNESS EVALUATION ===")
    print(f"Cases: {len(results)}")
    print(f"Average score: {average_score:.2%}")
    print(f"Full correctness (1.0): {full_scores}")
    print(f"Partial correctness (0.5): {partial_scores}")
    print(f"Incorrect (0.0): {zero_scores}")
    print(f"Results saved to: {ANSWER_RESULTS_PATH}")


if __name__ == "__main__":
    run_answer_evals()
