
from ai_petshop_assistant.evals.evaluators.answer_evaluator import (
    AnswerEvaluator,
)


evaluator = AnswerEvaluator()

result = evaluator.evaluate(
    question=(
        "Quanto custa banho e tosa higiênica para meu Shih Tzu de 8 kg?"
    ),
    answer=(
        "O banho custa R$ 55 e a tosa higiênica "
        "R$ 40, totalizando R$ 95. "
        "O orçamento precisa ser confirmado "
        "pela equipe."
    ),
    expected_facts=[
        "Um Shih Tzu de 8 kg é de pequeno porte.",
        "Banho padrão para pequeno porte custa R$ 55.",
        "Tosa higiênica custa R$ 40.",
        "A soma dos serviços é R$ 95.",
        "Não existe desconto automático de combo.",
    ],
    forbidden_claims=[
        "Existe desconto promocional de combo.",
        "O preço final está garantido.",
    ],
)

print(result.model_dump())
