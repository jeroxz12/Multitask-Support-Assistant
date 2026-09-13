import json
from pathlib import Path

from src.support_assistant.config import PROJECT_ROOT
from src.support_assistant.llm import generate_support_response
from src.support_assistant.safety import inspect_question, inspect_response

DATASET_PATH = PROJECT_ROOT / "evals" / "dataset.json"
RESULTS_PATH = PROJECT_ROOT / "evals" / "results.json"


def load_dataset() -> list[dict]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def score_case(case: dict, response: dict) -> dict:
    actual_confidence = response["confidence"]
    actual_actions = [item["type"] for item in response["actions"]]
    confidence_pass = actual_confidence in case["expected_confidence"]
    actions_pass = all(
        action_type in actual_actions for action_type in case["expected_action_types"]
    )
    return {
        "confidence_pass": confidence_pass,
        "actions_pass": actions_pass,
        "checks_pass": confidence_pass and actions_pass,
    }


def run_case(case: dict) -> dict:
    question = case["question"]
    safety = inspect_question(question)
    if safety["action"] == "fallback":
        raise RuntimeError(
            f"Case {case['id']} was blocked by the safety filter. "
            "Eval cases should be support questions, not injection attacks."
        )

    result, usage = generate_support_response(question)
    leak = inspect_response(result)
    if leak["action"] == "fallback":
        raise RuntimeError(f"Case {case['id']} looked like a prompt leak.")

    payload = result.model_dump(mode="json")
    return {
        "id": case["id"],
        "category": case["category"],
        "question": question,
        "expected_confidence": case["expected_confidence"],
        "expected_action_types": case["expected_action_types"],
        "review_focus": case["review_focus"],
        "response": payload,
        "usage": {
            "model": usage["model"],
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["total_tokens"],
            "latency_ms": round(usage["latency_ms"], 2),
        },
        "score": score_case(case, payload),
    }


def run_evaluation() -> dict:
    cases = load_dataset()
    results = [run_case(case) for case in cases]
    passed = sum(1 for item in results if item["score"]["checks_pass"])
    summary = {
        "total": len(results),
        "passed_automatic_checks": passed,
        "failed_automatic_checks": len(results) - passed,
        "cases": results,
    }
    RESULTS_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    summary = run_evaluation()
    print(
        f"Evaluation: {summary['passed_automatic_checks']}/{summary['total']} "
        "cases passed automatic checks."
    )
    print(f"Wrote {RESULTS_PATH}")
    for case in summary["cases"]:
        score = case["score"]
        mark = "PASS" if score["checks_pass"] else "FAIL"
        print(
            f"- {case['id']}: {mark} "
            f"(confidence={case['response']['confidence']}, "
            f"actions={[item['type'] for item in case['response']['actions']]})"
        )


if __name__ == "__main__":
    main()
