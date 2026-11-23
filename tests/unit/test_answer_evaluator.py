
import pytest
from pydantic import ValidationError
from unittest.mock import Mock
from ai_petshop_assistant.evals.evaluators.answer_evaluator import (
    AnswerEvaluator,
    AnswerEvaluation,
    calculate_correctness_score,
)

@pytest.mark.parametrize(
    "score",
    [0.0, 0.5, 1.0],
)
def test_answer_evaluation_accepts_valid_scores(score):
    evaluation = AnswerEvaluation(
        score=score,
        reasoning="Test evaluation",
    )

    assert evaluation.score == score
    assert evaluation.missing_facts == []
    assert evaluation.forbidden_claims_detected == []


def test_answer_evaluation_rejects_invalid_score():
    with pytest.raises(ValidationError):
        AnswerEvaluation(
            score=0.75,
            reasoning="Invalid score",
        )


def test_answer_evaluator_invokes_chain_with_expected_inputs():
    # Create an instance without calling __init__,
    # avoiding real OpenAI client initialization.
    evaluator = AnswerEvaluator.__new__(AnswerEvaluator)

    expected_result = AnswerEvaluation(
        score=1.0,
        reasoning="All expected facts are covered.",
        missing_facts=[],
        forbidden_claims_detected=[],
    )

    evaluator.chain = Mock()
    evaluator.chain.invoke.return_value = expected_result

    result = evaluator.evaluate(
        question="How much is a bath?",
        answer="A bath costs R$ 55 for small dogs.",
        expected_facts=[
            "Bath for small dogs costs R$ 55."
        ],
        forbidden_claims=[
            "Bath is free."
        ],
    )

    evaluator.chain.invoke.assert_called_once_with({
        "question": "How much is a bath?",
        "answer": "A bath costs R$ 55 for small dogs.",
        "expected_facts": [
            "Bath for small dogs costs R$ 55."
        ],
        "forbidden_claims": [
            "Bath is free."
        ],
    })

    assert result == expected_result


@pytest.mark.parametrize(
    "missing_facts, forbidden_claims, expected_score",
    [
        ([], [], 1.0),
        (["Missing price"], [], 0.5),
        ([], ["Incorrect price"], 0.0),
        (["Missing price"], ["Incorrect price"], 0.0),
    ],
)
def test_calculate_correctness_score(
    missing_facts,
    forbidden_claims,
    expected_score,
):
    evaluation = AnswerEvaluation(
        score=1.0,
        reasoning="Test",
        missing_facts=missing_facts,
        forbidden_claims_detected=forbidden_claims,
    )

    score = calculate_correctness_score(
        evaluation
    )

    assert score == expected_score

