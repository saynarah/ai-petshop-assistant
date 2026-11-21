
import pytest

from ai_petshop_assistant.evals.evaluators.handoff_evaluator import (
    evaluate_handoff,
    calculate_handoff_metrics,
)


@pytest.mark.parametrize(
    "expected, predicted, should_be_correct",
    [
        (True, True, True),    # True Positive
        (False, False, True),  # True Negative
        (False, True, False),  # False Positive
        (True, False, False),  # False Negative
    ],
)
def test_evaluate_handoff(
    expected,
    predicted,
    should_be_correct,
):
    result = evaluate_handoff(
        expected=expected,
        predicted=predicted,
    )

    assert result["correct"] == should_be_correct
    assert result["expected"] == expected
    assert result["predicted"] == predicted


def test_calculate_handoff_metrics():

    results = [
        {"expected": True, "predicted": True},    # TP
        {"expected": True, "predicted": True},    # TP
        {"expected": False, "predicted": False},  # TN
        {"expected": False, "predicted": False},  # TN
        {"expected": False, "predicted": True},   # FP
        {"expected": True, "predicted": False},   # FN
    ]

    metrics = calculate_handoff_metrics(results)

    assert metrics["tp"] == 2
    assert metrics["tn"] == 2
    assert metrics["fp"] == 1
    assert metrics["fn"] == 1

    assert metrics["total"] == 6
    assert metrics["accuracy"] == pytest.approx(4 / 6)
    assert metrics["precision"] == pytest.approx(2 / 3)
    assert metrics["recall"] == pytest.approx(2 / 3)
    assert metrics["false_negative_rate"] == pytest.approx(1 / 3)


def test_all_handoff_decisions_correct():

    results = [
        {"expected": True, "predicted": True},
        {"expected": False, "predicted": False},
    ]

    metrics = calculate_handoff_metrics(results)

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["false_negative_rate"] == 0.0


def test_no_positive_predictions():

    results = [
        {"expected": True, "predicted": False},
        {"expected": False, "predicted": False},
    ]

    metrics = calculate_handoff_metrics(results)

    assert metrics["tp"] == 0
    assert metrics["fn"] == 1
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0


def test_empty_results_raises_error():

    with pytest.raises(ValueError):
        calculate_handoff_metrics([])
