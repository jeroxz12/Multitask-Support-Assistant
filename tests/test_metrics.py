import pytest

from src.support_assistant.metrics import estimate_cost_usd, persist_run


def test_cost_for_one_million_input_tokens():
    assert estimate_cost_usd("gpt-4o-mini", 1_000_000, 0) == 0.15


def test_cost_for_one_million_output_tokens():
    assert estimate_cost_usd("gpt-4o-mini", 0, 1_000_000) == 0.60


def test_cost_for_mixed_tokens():
    cost = estimate_cost_usd("gpt-4o-mini", 1000, 500)
    expected = 1000 * 0.15 / 1_000_000 + 500 * 0.60 / 1_000_000
    assert cost == pytest.approx(expected)


def test_unknown_model_cost_is_zero():
    assert estimate_cost_usd("unknown-model", 1000, 1000) == 0.0


def test_persist_run_writes_success_row(tmp_path, monkeypatch):
    metrics_file = tmp_path / "metrics.csv"
    monkeypatch.setattr("src.support_assistant.metrics.METRICS_PATH", metrics_file)

    persist_run(
        status="success",
        model="gpt-4o-mini",
        input_tokens=1000,
        output_tokens=80,
        total_tokens=1080,
        latency_ms=123.45,
    )

    content = metrics_file.read_text(encoding="utf-8")
    assert "timestamp" in content
    assert "success" in content
    assert "gpt-4o-mini" in content
    assert "1000" in content
    assert "80" in content
    assert "1080" in content
