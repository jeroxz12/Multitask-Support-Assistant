# Project Milestones

## M0 — Project Foundation
- [x] Repository initialized
- [x] Python project structure defined
- [x] `.gitignore`
- [x] `.env.example`
- [x] Dependency management configured
- [x] `OPENAI_API_KEY` loaded from environment
- [x] Basic README created

### Definition of Done
The project can be cloned, dependencies installed and configuration understood.

---

## M1 — Core LLM Flow
- [x] CLI accepts a `question`
- [x] OpenAI API integration implemented
- [x] SupportResponse schema implemented
- [x] Action schema implemented
- [x] Confidence enum implemented
- [x] ActionType enum implemented
- [x] Structured Output used
- [x] Response validated against schema
- [x] Valid JSON printed to console
- [x] API/configuration errors handled

### Definition of Done
A command like:

```bash
python3 -m src.support_assistant "My payment was rejected. Why?"
```

returns a valid SupportResponse JSON.

---

## M2 — Prompt Engineering
- [x] Main prompt stored outside Python code
- [x] Role defined
- [x] Behavioral rules defined
- [x] Confidence rules defined
- [x] Action rules defined
- [x] Few-shot prompting implemented
- [x] Five representative examples included
- [x] Prompt injection instruction included
- [x] Prompt version documented

### Definition of Done
The assistant behaves consistently for:
- direct questions
- missing information
- troubleshooting
- escalation
- ambiguous questions

---

## M3 — Observability & Metrics
- [x] Prompt/input tokens captured
- [x] Completion/output tokens captured
- [x] Total tokens captured
- [x] API latency measured
- [x] Estimated cost calculated
- [x] Model name recorded
- [x] Timestamp recorded
- [x] Execution status recorded
- [x] Metrics persisted to CSV or JSON

### Definition of Done
Every execution creates one auditable metrics record.

---

## M4 — Automated Tests
- [x] JSON/schema validation test
- [x] Cost calculation test
- [x] Invalid response test
- [x] Tests run without requiring an OpenAI API call
- [x] Test execution documented

### Definition of Done
`pytest` runs locally without consuming API credits and core deterministic logic is tested.

---

## M5 — Safety (Bonus)
- [x] Adversarial prompt test defined
- [x] Prompt injection behavior tested
- [x] Safety/moderation strategy defined
- [x] Safe fallback implemented if necessary
- [x] Safety decisions logged
- [x] Example attack documented

### Definition of Done
An adversarial input cannot modify the expected response contract or reveal system instructions.

---

## M6 — Evaluation
- [x] Small evaluation dataset created
- [x] High-confidence case tested
- [x] Medium-confidence case tested
- [x] Low-confidence case tested
- [x] Human escalation case tested
- [x] Multiple-action case tested
- [x] Out-of-scope case tested
- [x] Results reviewed manually

### Definition of Done
The expected behavior has been evaluated using a repeatable set of representative queries.

Held-out cases live in `evals/held_out_cases.json`. Smoke cases (close to few-shot examples) live in `evals/smoke_cases.json`. A real `gpt-4o-mini` run scored 10/13 automatic checks; results are in `evals/results.json`. The three FAIL cases were reviewed manually.

---

## M7 — Documentation
- [x] README completed
- [x] Installation documented
- [x] Environment variables documented
- [x] Execution examples included
- [x] Architecture documented
- [x] Prompting technique justified
- [x] Metrics explained
- [x] Known limitations documented
- [x] Future improvements documented
- [x] Final 1–2 page report completed

### Definition of Done
Another developer can understand, install and run the project without assistance.

README: `README.md` (Spanish). Report: `reports/PI_report.md` (Spanish).

---

## M8 — Final Delivery
- [ ] Clean clone tested
- [x] No secrets committed
- [x] At least one metrics execution included
- [x] README and implementation are consistent
- [x] Report and implementation are consistent
- [x] Tests passing final verification
- [x] Evaluation final reviewed
- [ ] Repository public
- [ ] Final Git tag/release created

### Definition of Done
The repository satisfies the complete project checklist and is ready for submission.
