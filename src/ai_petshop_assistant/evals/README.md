# PetStop — RAG & Human Handoff Evaluations

> Evaluating context retrieval quality and human escalation decisions for a RAG-based pet shop customer support assistant.

## Overview

The **AI Pet Shop Assistant (PetStop)** uses a fictional knowledge base covering services, pricing, appointments, post-grooming care, and customer support policies. These experiments assess two distinct capabilities:

1. **Retrieval Evaluation:** Does the system retrieve the expected documents needed to address a customer request?
2. **Human Handoff Evaluation:** Does the agent correctly identify when **PetStop staff must intervene** to continue or resolve a request?

The experiments use a **30-case Golden Dataset**, including factual questions, multi-document queries, conversational follow-ups, unavailable information, and requests requiring human assistance.

> **Current status:** Retrieval and Human Handoff evaluations have been completed. **Answer Correctness / LLM-as-a-Judge** is planned and is not included in the results below.

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

## Suggested Project Structure

```text
src/ai_petshop_assistant/evals/
├── README.md
├── run_evals.py
├── run_handoff_evals.py
├── evaluators/
│   └── handoff_evaluator.py
├── datasets/
│   ├── petstop_eval_dataset_v1.jsonl
│   ├── petstop_eval_dataset_v2.jsonl
│   └── petstop_eval_dataset_v2_audit.csv
└── results/
    ├── retrieval_k3_v1.csv
    ├── retrieval_k5_v1.csv
    ├── handoff_eval_v1.csv
    └── handoff_eval_v2.csv

tests/unit/
└── test_handoff_evaluator.py
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

## Limitations and Next Steps

- **Small sample:** 30 cases provide an initial baseline, not evidence of production-level robustness.
- **LLM variability:** Results may vary between runs. Record the model, configuration, prompt version, and experiment date.
- **Gold labels:** The v2 labels were reviewed against the operational policy, but ambiguous cases should still be validated against explicit business criteria.
- **Failure analysis:** Investigate the one FN and three FPs from v2 to distinguish retrieval failures, prompt interpretation issues, validation logic errors, and labeling issues.
- **Answer Correctness:** The next planned experiment will evaluate `expected_facts` and `forbidden_claims`, ideally reusing saved agent responses and using an LLM-as-a-Judge calibrated through human review.
- **Independent test set:** Create unseen cases to check whether improvements are overfitted to the development dataset.

## Scope Note

**PetStop and its Knowledge Base documents are fictional and are used to develop and evaluate a portfolio project.** The metrics reported here are experimental results from this environment, not production service performance indicators.
