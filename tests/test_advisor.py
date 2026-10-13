
import pytest

from advisor import (
    OBJECTIVES,
    SchedulingAdvisor,
    extract_features,
    run_candidate_algorithms,
    score_algorithms,
)
from process import Process


@pytest.fixture
def sample_processes():
    return [
        Process(pid=1, burst_time=5, arrival_time=0, priority=2),
        Process(pid=2, burst_time=3, arrival_time=1, priority=1),
        Process(pid=3, burst_time=8, arrival_time=2, priority=3),
    ]


def test_extract_features_returns_expected_number_of_features(
    sample_processes,
):
    features = extract_features(sample_processes, quantum=2)

    assert len(features) == 15
    assert all(isinstance(value, (int, float)) for value in features)
    assert features[0] == 3
    assert features[1] == pytest.approx(16 / 3)
    assert features[12] == 2
    assert -1.0 <= features[13] <= 1.0
    assert -1.0 <= features[14] <= 1.0


def test_extract_features_rejects_empty_workload():
    with pytest.raises(ValueError, match="At least one process"):
        extract_features([])


@pytest.mark.parametrize("quantum", [0, -1])
def test_extract_features_rejects_invalid_quantum(
    sample_processes, quantum
):
    with pytest.raises(ValueError, match="Time quantum"):
        extract_features(sample_processes, quantum=quantum)


def test_run_candidate_algorithms_returns_all_six_algorithms(
    sample_processes,
):
    reports = run_candidate_algorithms(sample_processes, quantum=2)

    expected = {
        "FCFS",
        "SJF",
        "SRTF",
        "RR",
        "PRIORITY_NP",
        "PRIORITY_P",
    }

    assert set(reports.keys()) == expected
    assert all(report.results for report in reports.values())


@pytest.mark.parametrize(
    ("objective", "attribute"),
    [
        ("waiting", "average_waiting_time"),
        ("turnaround", "average_turnaround_time"),
        ("response", "average_response_time"),
    ],
)
def test_score_algorithms_uses_requested_metric(
    sample_processes, objective, attribute
):
    reports = run_candidate_algorithms(sample_processes, quantum=2)

    scores = score_algorithms(reports, objective)

    assert set(scores) == set(reports)

    for algorithm, report in reports.items():
        assert scores[algorithm] == pytest.approx(
            getattr(report, attribute)
        )


def test_balanced_scores_are_normalized(sample_processes):
    reports = run_candidate_algorithms(sample_processes, quantum=2)

    scores = score_algorithms(reports, "balanced")

    assert set(scores) == set(reports)
    assert all(0.0 <= score <= 1.0 for score in scores.values())


def test_score_algorithms_rejects_unknown_objective(sample_processes):
    reports = run_candidate_algorithms(sample_processes, quantum=2)

    with pytest.raises(ValueError):
        score_algorithms(reports, "unknown")


def test_objectives_contains_expected_options():
    assert set(OBJECTIVES) == {
        "balanced",
        "waiting",
        "turnaround",
        "response",
        "priority",
    }


def test_advisor_recommends_valid_algorithm(sample_processes):
    pytest.importorskip("sklearn")

    advisor = SchedulingAdvisor(
        training_samples=30,
        random_seed=42,
    )

    recommendation = advisor.recommend(
        sample_processes,
        objective="balanced",
        quantum=2,
    )

    assert recommendation.algorithm_key in {
        "FCFS",
        "SJF",
        "SRTF",
        "RR",
        "PRIORITY_NP",
        "PRIORITY_P",
    }
    assert recommendation.algorithm_name
    assert recommendation.objective == "balanced"
    assert 0.0 <= recommendation.model_score <= 1.0
    assert recommendation.explanation
    assert recommendation.trade_off


def test_advisor_rejects_unknown_objective(sample_processes):
    pytest.importorskip("sklearn")

    advisor = SchedulingAdvisor(
        training_samples=30,
        random_seed=42,
    )

    with pytest.raises(ValueError):
        advisor.recommend(
            sample_processes,
            objective="unknown",
            quantum=2,
        )
