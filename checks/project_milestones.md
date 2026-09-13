# Project Milestones

## M0 — Project Foundation
- [ ] Repository initialized
- [ ] Python project structure defined
- [ ] `.gitignore`
- [ ] `.env.example`
- [ ] Dependency management configured
- [ ] `OPENAI_API_KEY` loaded from environment
- [ ] Basic README created

### Definition of Done
The project can be cloned, dependencies installed and configuration understood.

---

## M1 — Core LLM Flow
- [ ] CLI accepts a `question`
- [ ] OpenAI API integration implemented
- [ ] SupportResponse schema implemented
- [ ] Action schema implemented
- [ ] Confidence enum implemented
- [ ] ActionType enum implemented
- [ ] Structured Output used
- [ ] Response validated against schema
- [ ] Valid JSON printed to console
- [ ] API/configuration errors handled

### Definition of Done
A command like:

python -m src.run_query "My payment was rejected. Why?"

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
- [ ] Small evaluation dataset created
- [ ] High-confidence case tested
- [ ] Medium-confidence case tested
- [ ] Low-confidence case tested
- [ ] Human escalation case tested
- [ ] Multiple-action case tested
- [ ] Out-of-scope case tested
- [ ] Results reviewed manually

### Definition of Done
The expected behavior has been evaluated using a repeatable set of representative queries.

---

## M7 — Documentation
- [ ] README completed
- [ ] Installation documented
- [ ] Environment variables documented
- [ ] Execution examples included
- [ ] Architecture documented
- [ ] Prompting technique justified
- [ ] Metrics explained
- [ ] Known limitations documented
- [ ] Future improvements documented
- [ ] Final 1–2 page report completed

### Definition of Done
Another developer can understand, install and run the project without assistance.

---

## M8 — Final Delivery
- [ ] Clean clone tested
- [ ] No secrets committed
- [ ] At least one metrics execution included
- [ ] README and implementation are consistent
- [ ] Report and implementation are consistent
- [ ] Tests passing
- [ ] Repository public
- [ ] Final Git tag/release created

### Definition of Done
The repository satisfies the complete project checklist and is ready for submission.