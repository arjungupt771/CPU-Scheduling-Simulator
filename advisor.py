
from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Callable
from math import sqrt
from process import Process, ScheduleReport
from scheduler import Scheduler


ALGORITHMS = {
    "FCFS": "First Come First Served (FCFS)",
    "SJF": "Shortest Job First (SJF)",
    "SRTF": "Shortest Remaining Time First (SRTF)",
    "RR": "Round Robin",
    "PRIORITY_NP": "Priority Scheduling (Non-Preemptive)",
    "PRIORITY_P": "Priority Scheduling (Preemptive)",
}

OBJECTIVES = {
    "balanced": "Balanced performance",
    "waiting": "Lowest average waiting time",
    "turnaround": "Lowest average turnaround time",
    "response": "Lowest average response time",
    "priority": "Priority-aware waiting time",
}

TRADE_OFFS = {
    "FCFS": (
        "Simple and predictable, but a long process can delay "
        "shorter processes arriving behind it."
    ),
    "SJF": (
        "Favors short jobs and can reduce waiting time, but long "
        "jobs may wait longer when short jobs keep arriving."
    ),
    "SRTF": (
        "Adapts to remaining execution time and often improves "
        "waiting time, but preemption can delay longer jobs."
    ),
    "RR": (
        "Time slices improve responsiveness and sharing, but results "
        "depend strongly on the chosen time quantum."
    ),
    "PRIORITY_NP": (
        "Respects process priorities without interrupting a running "
        "process, but a high-priority arrival may have to wait."
    ),
    "PRIORITY_P": (
        "Allows high-priority processes to run sooner, but lower-"
        "priority processes may experience longer waits."
    ),
}


@dataclass(frozen=True)
class AdvisorRecommendation:
    algorithm_key: str
    algorithm_name: str
    objective: str
    model_score: float
    explanation: str
    trade_off: str


def run_candidate_algorithms(
    processes: list[Process] | tuple[Process, ...],
    quantum: int = 3,
) -> dict[str, ScheduleReport]:
    """Run all six algorithms against the same process workload."""
    scheduler = Scheduler(processes)

    return {
        "FCFS": scheduler.first_come_first_served(),
        "SJF": scheduler.shortest_job_first(),
        "SRTF": scheduler.shortest_remaining_time_first(),
        "RR": scheduler.round_robin(quantum),
        "PRIORITY_NP": scheduler.priority_scheduling(),
        "PRIORITY_P": scheduler.preemptive_priority_scheduling(),
    }


def _correlation(left: list[float], right: list[float]) -> float:
    """Return Pearson correlation, or zero if either list is constant."""
    left_mean = mean(left)
    right_mean = mean(right)

    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]

    numerator = sum(
        x * y for x, y in zip(left_centered, right_centered)
    )
    left_sum_squares = sum(x * x for x in left_centered)
    right_sum_squares = sum(y * y for y in right_centered)

    denominator = sqrt(left_sum_squares * right_sum_squares)

    return numerator / denominator if denominator else 0.0


def extract_features(
    processes: list[Process] | tuple[Process, ...],
    quantum: int = 3,
) -> list[float]:
    """Convert a workload into numeric features for the ML model."""
    if not processes:
        raise ValueError("At least one process is required.")

    if quantum <= 0:
        raise ValueError("Time quantum must be positive.")

    bursts = [process.burst_time for process in processes]
    arrivals = [process.arrival_time for process in processes]
    priorities = [process.priority for process in processes]

    average_burst = mean(bursts)
    burst_variation = (
        pstdev(bursts) / average_burst if average_burst else 0.0
    )

    return [
        float(len(processes)),
        average_burst,
        pstdev(bursts),
        float(min(bursts)),
        float(max(bursts)),
        burst_variation,
        mean(arrivals),
        pstdev(arrivals),
        float(max(arrivals) - min(arrivals)),
        mean(priorities),
        pstdev(priorities),
        len(set(priorities)) / len(priorities),
        float(quantum),
        _correlation(priorities, bursts),
        _correlation(priorities, arrivals),
    ]


def score_algorithms(
    reports: dict[str, ScheduleReport],
    objective: str,
) -> dict[str, float]:
    """Score algorithms using their measured simulation results."""
    if objective == "waiting":
        return {
            key: report.average_waiting_time
            for key, report in reports.items()
        }

    if objective == "turnaround":
        return {
            key: report.average_turnaround_time
            for key, report in reports.items()
        }

    if objective == "response":
        return {
            key: report.average_response_time
            for key, report in reports.items()
        }

    if objective == "priority":
        scores = {}

        for key, report in reports.items():
            total_weight = sum(
                1.0 / (result.priority + 1)
                for result in report.results
            )

            scores[key] = sum(
                result.waiting_time / (result.priority + 1)
                for result in report.results
            ) / total_weight

        return scores

    if objective == "balanced":
        metrics = {
            key: (
                report.average_waiting_time,
                report.average_turnaround_time,
                report.average_response_time,
            )
            for key, report in reports.items()
        }

        normalized_columns = []

        for column_index in range(3):
            values = [
                metric[column_index]
                for metric in metrics.values()
            ]
            lowest = min(values)
            highest = max(values)
            difference = highest - lowest

            normalized_columns.append({
                key: (
                    (metric[column_index] - lowest) / difference
                    if difference
                    else 0.0
                )
                for key, metric in metrics.items()
            })

        return {
            key: mean(
                normalized_columns[column][key]
                for column in range(3)
            )
            for key in metrics
        }

    raise ValueError(
        f"Unknown objective: {objective}. "
        f"Choose one of: {', '.join(OBJECTIVES)}."
    )


def _generate_workload(
    rng: random.Random,
) -> list[Process]:
    """Generate a reproducible synthetic workload."""
    count = rng.randint(2, 8)
    processes = []

    for pid in range(1, count + 1):
        processes.append(
            Process(
                pid=pid,
                burst_time=rng.randint(1, 20),
                arrival_time=rng.randint(0, 15),
                priority=rng.randint(0, 4),
            )
        )

    return processes


class SchedulingAdvisor:
    """Train and query a Random Forest scheduling advisor."""

    def __init__(
        self,
        training_samples: int = 300,
        random_seed: int = 42,
    ) -> None:
        if training_samples < 30:
            raise ValueError(
                "Use at least 30 training samples for the advisor."
            )

        # Import lazily so the existing simulator can still be imported
        # without scikit-learn installed when the advisor is not used.
        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError as error:
            raise ImportError(
                "The AI advisor requires scikit-learn. "
                "Install it with: python -m pip install scikit-learn"
            ) from error

        rng = random.Random(random_seed)
        training_features = []
        training_labels = {objective: [] for objective in OBJECTIVES}

        for _ in range(training_samples):
            processes = _generate_workload(rng)
            quantum = rng.randint(1, 6)

            reports = run_candidate_algorithms(processes, quantum)
            training_features.append(
                extract_features(processes, quantum)
            )

            for objective in OBJECTIVES:
                scores = score_algorithms(reports, objective)
                best_algorithm = min(
                    scores,
                    key=lambda algorithm: (
                        scores[algorithm],
                        list(ALGORITHMS).index(algorithm),
                    ),
                )
                training_labels[objective].append(best_algorithm)

        self.models: dict[str, RandomForestClassifier] = {}

        for objective, labels in training_labels.items():
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=random_seed,
                class_weight="balanced",
            )
            model.fit(training_features, labels)
            self.models[objective] = model

    def recommend(
        self,
        processes: list[Process] | tuple[Process, ...],
        objective: str = "balanced",
        quantum: int = 3,
    ) -> AdvisorRecommendation:
        """Recommend an algorithm for a workload and chosen objective."""
        if objective not in OBJECTIVES:
            raise ValueError(
                f"Unknown objective: {objective}. "
                f"Choose one of: {', '.join(OBJECTIVES)}."
            )

        features = extract_features(processes, quantum)
        model = self.models[objective]

        predicted = str(model.predict([features])[0])
        probabilities = model.predict_proba([features])[0]
        class_index = list(model.classes_).index(predicted)
        model_score = float(probabilities[class_index])

        burst_mean = mean(p.burst_time for p in processes)
        burst_std = pstdev(p.burst_time for p in processes)
        arrival_span = (
            max(p.arrival_time for p in processes)
            - min(p.arrival_time for p in processes)
        )

        explanation = (
            f"The model selected {ALGORITHMS[predicted]} for the "
            f"'{OBJECTIVES[objective]}' objective. Its input included "
            f"{len(processes)} processes, an average burst time of "
            f"{burst_mean:.2f}, burst-time standard deviation of "
            f"{burst_std:.2f}, arrival-time span of {arrival_span}, "
            f"and the distribution of process priorities. This is a "
            f"learned prediction, not a guarantee of the best result."
        )

        return AdvisorRecommendation(
            algorithm_key=predicted,
            algorithm_name=ALGORITHMS[predicted],
            objective=objective,
            model_score=model_score,
            explanation=explanation,
            trade_off=TRADE_OFFS[predicted],
        )
