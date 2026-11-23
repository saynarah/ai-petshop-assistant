
import pytest

from ai_petshop_assistant.evals.evaluators.answer_evaluator import (
    AnswerEvaluator,
)


@pytest.mark.external
@pytest.mark.parametrize(
    "question, answer, expected_facts, forbidden_claims, expected_score",
    [
        (
            "Can I book a full grooming on Sunday? How much?",
            (
                "Full grooming requires a quote. "
                "Please contact the team about availability."
            ),
            [
                "PetStop is closed on Sundays.",
                "Full grooming requires a personalized quote.",
            ],
            [],
            0.5,
        ),
        (
            "My dog weighs 28 kg. Bath price and duration?",
            (
                "The bath costs R$ 80 and takes "
                "90 to 130 minutes."
            ),
            [
                "A 28 kg dog is classified as large.",
                "Bath prices for large dogs start at R$ 120.",
                "Estimated bath duration is 90 to 130 minutes.",
            ],
            [
                "Bath for large dogs costs R$ 80.",
            ],
            0.0,
        ),
        (
            "How much is hygienic grooming for my small dog?",
            (
                "Hygienic grooming costs R$ 40. "
                "If you add a bath, the total is R$ 95."
            ),
            [
                "Hygienic grooming for small dogs costs R$ 40.",
            ],
            [
                "Hygienic grooming is free.",
            ],
            1.0,
        ),
    ],
)
def test_judge_calibration(
    question,
    answer,
    expected_facts,
    forbidden_claims,
    expected_score,
):
    evaluator = AnswerEvaluator()

    result = evaluator.evaluate(
        question=question,
        answer=answer,
        expected_facts=expected_facts,
        forbidden_claims=forbidden_claims,
    )


    print("\nScore:", result.score)
    print("Reasoning:", result.reasoning)
    print("Missing facts:", result.missing_facts)
    print(
    "Forbidden claims detected:",
    result.forbidden_claims_detected,
    )


    assert result.score == expected_score
