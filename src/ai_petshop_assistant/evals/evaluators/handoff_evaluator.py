
def evaluate_handoff(
    expected: bool,
    predicted: bool,
) -> dict:

    return {
        "correct": expected == predicted,
        "expected": expected,
        "predicted": predicted,
    }


def calculate_handoff_metrics(
    results: list[dict],
) -> dict:

    if not results:
        raise ValueError("Evaluation results cannot be empty")

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for result in results:
        expected = result["expected"]
        predicted = result["predicted"]

        if expected and predicted:
            tp += 1

        elif not expected and not predicted:
            tn += 1

        elif not expected and predicted:
            fp += 1

        elif expected and not predicted:
            fn += 1

    total = len(results)

    accuracy = (tp + tn) / total

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0 else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0 else 0.0
    )

    false_negative_rate = (
        fn / (tp + fn)
        if (tp + fn) > 0 else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "false_negative_rate": false_negative_rate,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "total": total,
    }

