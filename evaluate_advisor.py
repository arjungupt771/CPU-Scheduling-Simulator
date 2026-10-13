
"""Evaluate the AI scheduling advisor on unseen synthetic workloads."""

import random
from statistics import mean

from advisor import (
    ALGORITHMS,
    OBJECTIVES,
    SchedulingAdvisor,
    run_candidate_algorithms,
    score_algorithms,
)
from process import Process
from math import isclose

def generate_test_workload(rng):
    """Generate a test workload independently of advisor training."""
    count = rng.randint(2, 8)

    return [
        Process(
            pid=pid,
            burst_time=rng.randint(1, 20),
            arrival_time=rng.randint(0, 15),
            priority=rng.randint(0, 4),
        )
        for pid in range(1, count + 1)
    ]


def evaluate_advisor(
    training_samples=300,
    evaluation_samples=100,
    training_seed=42,
    evaluation_seed=2026,
):
    if evaluation_samples < 1:
        raise ValueError("Evaluation samples must be at least 1.")

    if training_seed == evaluation_seed:
        raise ValueError(
            "Use different seeds for training and evaluation."
        )

    print("Training the scheduling advisor...")
    advisor = SchedulingAdvisor(
        training_samples=training_samples,
        random_seed=training_seed,
    )

    rng = random.Random(evaluation_seed)
    results = {
        objective: {
            "matches": 0,
            "regrets": [],
        }
        for objective in OBJECTIVES
    }

    algorithm_order = list(ALGORITHMS)

    print(
        f"Evaluating on {evaluation_samples} unseen workloads..."
    )

    for _ in range(evaluation_samples):
        processes = generate_test_workload(rng)
        quantum = rng.randint(1, 6)

        reports = run_candidate_algorithms(processes, quantum)

        for objective in OBJECTIVES:
            recommendation = advisor.recommend(
                processes,
                objective=objective,
                quantum=quantum,
            )

            scores = score_algorithms(reports, objective)

            # Lower scores are better for every objective.
            best_score = min(scores.values())
            best_algorithms = {
                algorithm
                for algorithm, score in scores.items()
                if isclose(score, best_score, rel_tol=1e-9, abs_tol=1e-9)
                }

            recommended = recommendation.algorithm_key
            if recommended in best_algorithms:
                results[objective]["matches"] += 1

            regret = max(0.0, scores[recommended] - best_score)
            results[objective]["regrets"].append(regret)

    print("\n" + "=" * 76)
    print("AI SCHEDULING ADVISOR — EVALUATION RESULTS")
    print("=" * 76)
    print(f"Training workloads:   {training_samples}")
    print(f"Evaluation workloads: {evaluation_samples}")
    print(f"Training seed:        {training_seed}")
    print(f"Evaluation seed:      {evaluation_seed}")
    print("\nLower scores are better; zero regret means the")
    print("recommendation matched the best measured score.")
    print("-" * 76)

    for objective, data in results.items():
        accuracy = (
            data["matches"] / evaluation_samples
        ) * 100
        average_regret = mean(data["regrets"])

        print(f"\n{OBJECTIVES[objective]}")
        print(
            f"  Exact-match rate: {accuracy:.1f}% "
            f"({data['matches']}/{evaluation_samples})"
        )
        print(f"  Average score gap: {average_regret:.4f}")

    print("\n" + "=" * 76)
    print("Evaluation complete.")


if __name__ == "__main__":
    for seed in [2026, 2027, 2028, 2029, 2030]:
        print(f"\n\n{'#' * 76}")
        print(f"EVALUATION SEED: {seed}")
        print(f"{'#' * 76}")

        evaluate_advisor(
            training_samples=1500,
            evaluation_samples=100,
            training_seed=42,
            evaluation_seed=seed,
        )