# PetStop — RAG, Human Handoff & Answer Correctness Evaluations

> Evaluating document retrieval, operational human escalation, and factual answer quality for a RAG-based pet shop customer support assistant.

## Overview

The **AI Pet Shop Assistant (PetStop)** uses a fictional knowledge base covering services, pricing, appointments, post-grooming care, and customer support policies. These experiments assess three complementary capabilities:

1. **Retrieval Evaluation:** Does the system retrieve the expected documents needed to address a customer request?
2. **Human Handoff Evaluation:** Does the agent correctly identify when **PetStop staff must intervene** to continue or resolve a request?
3. **Answer Correctness Evaluation:** Does the generated answer cover expected facts without material factual mistakes or prohibited claims?

The experiments use a **30-case Golden Dataset**, including factual questions, multi-document queries, conversational follow-ups, unavailable information, and requests requiring human assistance.

> **Current status:** Initial Retrieval, Human Handoff, and Answer Correctness evaluations have been run. Answer Correctness v1 is an **uncalibrated LLM-as-a-Judge baseline**. Judge calibration identified a scoring inconsistency; the proposed hybrid-scoring implementation and a full v2 evaluation have **not** been completed.

## Knowledge Base

The evaluated version uses five fictional reference documents:

| Document | Contents |
| --- | --- |
| `01_servicos_banho_tosa.md` | Service scope, grooming options, and service conditions |
| `02_tabela_precos_pacotes.md` | Reference prices, dog size classifications, and commercial terms |
| `03_agendamento_cancelamento.md` | Business hours, booking requests, rescheduling, and cancellations |
| `04_cuidados_apos_tosa_bem_estar.md` | General hygiene and wellness guidance and limits of veterinary advice |
| `05_atendimento_produtos_escalonamento.md` | Inventory, special requests, safety, and escalation to staff |

The agent cannot verify real-time availability or complete bookings based solely on these documents.

## Golden Dataset

Dataset v2 retains the same **30 cases** and identifiers as the previous version.

| Category | Cases |
| --- | ---: |
| `factual` | 8 |
| `multi_documento` | 6 |
| `historico` | 5 |
| `informacao_indisponivel` | 6 |
| `encaminhamento_humano` | 5 |
| **Total** | **30** |

Each record in `petstop_eval_dataset_v2.jsonl` contains these fields:

```json
{
  "id": "U01",
  "category": "informacao_indisponivel",
  "question": "Tem horário livre amanhã às 10h para banho?",
  "chat_history": [],
  "expected_facts": [
    "Não existe acesso a disponibilidade em tempo real.",
    "Pode encaminhar solicitação para confirmação pela equipe."
  ],
  "expected_sources": ["03_agendamento_cancelamento.md"],
  "expected_outcome": "escalate",
  "needs_human_review": true,
  "forbidden_claims": ["Há vaga às 10h", "Agendamento confirmado"]
}
```

The dataset v2 contains **8 positive cases** (`needs_human_review=true`) and **22 negative cases**. A question's category does not automatically determine its handoff label.

### Handoff policy used in v2

`needs_human_review=true` means **PetStop staff must take action** to resolve or continue a customer request—for example, verifying appointment availability or stock, changing bookings, or handling requests and complaints that require a staff member.

Recommending that a customer consult **an external veterinarian** does not, by itself, mean the conversation must be transferred to PetStop staff. The assistant must still refrain from providing diagnoses, prescriptions, or clinical treatment recommendations. However, an incident related to a PetStop service that requires staff action may warrant an operational handoff.

The v1 → v2 review changed **five labels** (H03, U05, E01, E04, and E05). The rationale for each change is documented in `petstop_eval_dataset_v2_audit.csv`.

## 1. Retrieval Evaluation

The metric used was **Source Recall**, calculated from the names of expected and retrieved documents:

\[
\operatorname{Recall}(q) = \frac{|\text{expected sources} \cap \text{retrieved sources}|}{|\text{expected sources}|}
\]

The overall result is the average recall across individual cases. **This metric does not measure whether the LLM's final answer is correct**, nor does it guarantee that a retrieved chunk contains the relevant supporting evidence within a document.

### Results

| Metric | `k=3` | `k=5` |
| --- | ---: | ---: |
| **Retrieval Source Recall** | **86.67%** | **89.44%** |
| Factual | 100.00% | 100.00% |
| Multi-document | 83.33% | 88.89% |
| Conversation history | 90.00% | 90.00% |
| Unavailable information | 83.33% | 83.33% |
| Human handoff | 70.00% | 80.00% |

**Observations:**

- Increasing `k` from 3 to 5 improved overall Source Recall by **2.77 percentage points**.
- The largest category-level gain was in `encaminhamento_humano` (+10 percentage points).
- Better retrieval does not prove that generated answers are more accurate, and it may increase the amount of context processed.
- A MultiQuery Retriever experiment was proposed but **is not part of this comparison**.

## 2. Human Handoff Evaluation

The evaluator compares the dataset's expected value against the `needs_human_review` field returned by the agent. Metrics are derived from the confusion matrix:

- **TP (True Positive):** Human intervention was required and correctly flagged.
- **TN (True Negative):** Human intervention was unnecessary and correctly not flagged.
- **FP (False Positive):** Human intervention was flagged unnecessarily.
- **FN (False Negative):** Human intervention was required but not flagged by the agent.

| Metric | Formula |
| --- | --- |
| Accuracy | `(TP + TN) / (TP + TN + FP + FN)` |
| Precision | `TP / (TP + FP)` |
| Recall | `TP / (TP + FN)` |
| False Negative Rate (FNR) | `FN / (TP + FN)` |

### Observed results

| Metric | v1 | v2 |
| --- | ---: | ---: |
| **Accuracy** | **70.00%** | **86.67%** |
| Precision | 60.00% | 70.00% |
| Recall | 54.55% | 87.50% |
| False Negative Rate | 45.45% | 12.50% |
| True Positives (TP) | 6 | 7 |
| True Negatives (TN) | 15 | 19 |
| False Positives (FP) | 4 | 3 |
| False Negatives (FN) | 5 | 1 |
| Total cases | 30 | 30 |

In v2, the agent made **26 correct decisions out of 30** and identified **7 of the 8 cases** requiring escalation to PetStop staff.

### Important comparability caveat

**The v1 and v2 results do not represent a controlled experiment that changed only the prompt.** Between versions, the handoff policy was revised and five Golden Dataset labels were changed. Accordingly, the metric differences reflect these combined changes and **must not be attributed exclusively to improvements in the model or prompt**.

To isolate the effect of the prompt, both agent versions would need to be evaluated against **the same dataset and labeling policy**, with other conditions held constant.

## 3. Answer Correctness Evaluation (LLM-as-a-Judge, v1)

This experiment evaluates the *final answers* generated by the PetShopAgent, rather than the retrieved document list or the handoff decision. It uses **the 30-case Golden Dataset v2** and reuses the answers previously saved in `handoff_eval_v2.csv`, joined by case `id`. The agent itself does not need to be invoked again for this evaluation; the judge makes separate LLM API calls.

### Inputs and rubric

For each case, the judge receives:

- `question`: the user's question;
- `answer`: the assistant's saved response;
- `expected_facts`: facts against which the response is evaluated;
- `forbidden_claims`: claims that must not appear in the response.

The **v1 judge** uses `gpt-4o-mini` with structured Pydantic output (`AnswerEvaluation`) and a three-level rubric:

| Score | Meaning in the initial rubric |
| --- | --- |
| `1.0` | Expected essential facts covered; no forbidden claims |
| `0.5` | Partially correct or incomplete; no forbidden claims |
| `0.0` | Incorrect, unsupported, or contains forbidden claims |

The output also includes `reasoning`, `missing_facts`, and `forbidden_claims_detected`. The score is **assigned by the LLM in v1**, not computed deterministically in Python.

### Observed results — Answer Correctness v1

| Metric | Result |
| --- | ---: |
| **Mean Answer Correctness score** | **95.00%** |
| Answers rated `1.0` | 27 / 30 (90.00%) |
| Answers rated `0.5` | 3 / 30 (10.00%) |
| Answers rated `0.0` | 0 / 30 (0.00%) |

The mean score is `(27 × 1.0 + 3 × 0.5 + 0 × 0.0) / 30 = 0.95`. **A 95% mean score is not a 95% fully-correct answer rate**; 27 of 30 answers received the maximum rating from the judge. These are *judge-assigned* scores, not independently verified accuracy measurements.

### Manual review of partially scored cases

The three `0.5` cases were examined to diagnose both assistant errors and judge errors:

| Case | Observation | Manual interpretation |
| --- | --- | --- |
| `M02` — Full grooming on Sunday | The assistant correctly said full grooming requires a personalized quote but failed to state that PetStop is closed on Sundays. | `0.5` is reasonable: an essential fact was omitted. |
| `M04` — Bath price and duration for a 28 kg dog | The assistant gave the correct duration (90–130 minutes), but incorrectly quoted **R$ 80** instead of the documented **starting price of R$ 120** for large dogs. | A material factual price error; under the proposed stricter rubric this warrants `0.0`. |
| `H01` — Follow-up about hygienic grooming | The assistant correctly quoted **R$ 40** and included accurate, optional information about adding a bath. | `1.0` is appropriate for factual correctness; optional relevant information should not itself cause a correctness penalty. |

The manual review indicates that the initial judge can be both **too lenient about incorrect business facts** (`M04`) and **too strict about harmless extra detail** (`H01`). This is why `0` answers rated incorrect **must not** be interpreted as evidence that no incorrect answers exist.

### Calibration experiment and known failure

Three known-answer cases (`M02`: expected `0.5`; `M04`: expected `0.0`; `H01`: expected `1.0`) were prepared as external integration tests for the judge. During calibration, the `M04` test failed: the judge returned `0.5` instead of `0.0` despite explicitly detecting the incorrect price and listing the corresponding forbidden claim.

This demonstrates a gap between **error detection** and **score assignment**. A planned but **not yet implemented** improvement is a *hybrid judge*: let the LLM identify missing facts, forbidden claims, and material errors; then calculate the score through explicit Python rules. Independent, unseen calibration examples are also needed to validate detection quality, rather than only the numeric scoring logic.

### What this evaluation does *not* establish

- It does not independently verify every generated claim against the retrieved chunks (a separate groundedness/faithfulness evaluation would be needed).
- The original `expected_facts` may include useful but nonessential information; the gold criteria require further calibration.
- The judge is probabilistic. `temperature=0` does not guarantee identical judgments across runs.
- The same 30-case dataset was used to inspect failures and design calibration changes; use a fresh held-out set before making broader quality claims.

## Suggested Project Structure

```text
src/ai_petshop_assistant/evals/
├── README.md
├── run_evals.py
├── run_handoff_evals.py
├── run_answer_evals.py
├── evaluators/
│   ├── handoff_evaluator.py
│   └── answer_evaluator.py
├── datasets/
│   ├── petstop_eval_dataset_v1.jsonl
│   ├── petstop_eval_dataset_v2.jsonl
│   └── petstop_eval_dataset_v2_audit.csv
└── results/
    ├── retrieval_k3_v1.csv
    ├── retrieval_k5_v1.csv
    ├── handoff_eval_v1.csv
    ├── handoff_eval_v2.csv
    └── answer_correctness_v1.csv

tests/
├── unit/
│   ├── test_handoff_evaluator.py
│   └── test_answer_evaluator.py
└── integration/
    └── test_answer_evaluator.py  # LLM judge calibration; external API calls
```

> The filenames and paths above are illustrative. Adjust them if your repository uses a different layout.

## Reproducing the Experiments

### Prerequisites

- Dependencies installed with `uv`.
- Required API credentials configured **outside the repository**.
- The Knowledge Base indexed in the vector store used for evaluation.
- An evaluation namespace/collection isolated from production.

### Human handoff unit tests

From the project root:

```bash
uv run pytest tests/unit/test_handoff_evaluator.py -v
```

### Retrieval Eval

```bash
PYTHONPATH=src uv run python src/ai_petshop_assistant/evals/run_evals.py
```

Before each experiment, configure the dataset, `k` value, and output filename in the runner, without overwriting previous baselines.

### Human Handoff Eval

Configure the runner to use:

```python
DATASET_PATH = EVAL_DIR / "datasets" / "petstop_eval_dataset_v2.jsonl"
RESULTS_PATH = EVAL_DIR / "results" / "handoff_eval_v2.csv"
```

Run:

```bash
PYTHONPATH=src uv run python src/ai_petshop_assistant/evals/run_handoff_evals.py
```

The runner should generate unique identifiers for each case and execution and isolate conversation histories, preventing responses from one case from influencing another. This experiment makes real LLM API calls and may incur costs.

### Answer Correctness unit tests (no LLM calls)

```bash
uv run pytest tests/unit/test_answer_evaluator.py -v
```

### Answer Correctness Eval v1 (uses saved agent answers)

Configure the runner to read `petstop_eval_dataset_v2.jsonl` and `handoff_eval_v2.csv`, and write `answer_correctness_v1.csv`. Run from the repository root:

```bash
PYTHONPATH=src uv run python src/ai_petshop_assistant/evals/run_answer_evals.py
```

This calls the judge LLM for each case and may incur API costs. Keep the generated v1 report when performing further calibration; future runs should use a new results filename.

### Judge calibration integration tests (external API calls)

```bash
uv run pytest tests/integration/test_answer_evaluator.py -m external -v -s
```

The known `M04` price-error calibration case **did not pass** with the v1 judge; this is a documented limitation, not a passing quality gate. Ensure `external` is defined in the project's pytest configuration.

## Limitations and Next Steps

- **Small sample:** 30 cases provide an initial baseline, not evidence of production-level robustness.
- **LLM variability:** Results may vary between runs. Record the model, configuration, prompt version, and experiment date.
- **Gold labels:** The v2 labels were reviewed against the operational policy, but ambiguous cases should still be validated against explicit business criteria.
- **Failure analysis:** Investigate the one FN and three FPs from v2 to distinguish retrieval failures, prompt interpretation issues, validation logic errors, and labeling issues.
- **Answer Correctness judge calibration:** The v1 experiment is complete, but the judge has a confirmed scoring error on `M04`. Implement and validate hybrid scoring later, if prioritised; do not present the baseline as verified factual accuracy.
- **Agent errors:** Investigate the Sunday-hours omission (`M02`) and incorrect large-dog bath price (`M04`) separately from judge scoring issues.
- **Channel integration:** Next development focus is a real Telegram messaging interface connected to the existing FastAPI backend; Meta WhatsApp onboarding remains a possible future integration.
- **Independent test set:** Create unseen cases to check whether improvements are overfitted to the development dataset.

## Scope Note

**PetStop and its Knowledge Base documents are fictional and are used to develop and evaluate a portfolio project.** The metrics reported here are experimental results from this environment, not production service performance indicators. Answer Correctness v1 additionally reflects an uncalibrated LLM judge and must not be presented as independently verified answer accuracy.
