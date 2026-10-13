# CPU Scheduling Simulator

A Python-based CPU Scheduling Simulator implementing six operating-system scheduling algorithms, Gantt chart visualization, performance comparisons, and a machine-learning-powered AI Scheduling Advisor.

The advisor uses a Random Forest classifier trained on synthetic workloads to recommend a scheduling algorithm based on the selected optimization objective. Its recommendations are evaluated against the measured results of all six scheduling algorithms.

## Features

- **Six CPU scheduling algorithms** covering preemptive and non-preemptive scheduling.
- **AI Scheduling Advisor** powered by scikit-learn's Random Forest classifier.
- **Five optimization objectives** covering balanced performance, waiting time, turnaround time, response time, and priority-aware waiting.
- **15 workload features** describing process counts, burst times, arrival times, priorities, time quantum, and relationships between workload attributes.
- **Gantt chart visualization** showing process execution intervals and CPU idle periods.
- **Process-level performance metrics** including start time, completion time, waiting time, turnaround time, and response time.
- **Algorithm comparison** using measured simulation results.
- **Recommendation validation** comparing ML predictions with the best measured algorithm for the current workload.
- **Synthetic workload evaluation** to measure recommendation accuracy and score gaps.
- **Automated testing** using pytest.

## Scheduling Algorithms

| Algorithm | Type | Description |
|---|---|---|
| First Come First Served (FCFS) | Non-preemptive | Executes processes in arrival order. |
| Shortest Job First (SJF) | Non-preemptive | Selects the available process with the shortest burst time. |
| Shortest Remaining Time First (SRTF) | Preemptive | Selects the available process with the shortest remaining execution time. |
| Round Robin (RR) | Preemptive | Allocates CPU time in fixed time slices using a configurable quantum. |
| Priority Scheduling | Non-preemptive | Selects the available process with the highest priority. |
| Priority Scheduling | Preemptive | Allows a higher-priority process to interrupt the currently running process. |

**Priority convention:** A lower numerical value represents a higher priority.

## AI Scheduling Advisor

The advisor trains a Random Forest classifier using generated synthetic workloads. For each training workload, it simulates all six algorithms and uses their measured scores to determine the best algorithm for each optimization objective.

### Optimization objectives

| Objective | Goal |
|---|---|
| Balanced performance | Balance average waiting, turnaround, and response times. |
| Lowest average waiting time | Minimize average time spent waiting for CPU execution. |
| Lowest average turnaround time | Minimize average time from process arrival to completion. |
| Lowest average response time | Minimize the time until processes first receive CPU execution. |
| Priority-aware waiting time | Minimize a priority-weighted waiting-time score. |

### Feature engineering

The model uses 15 numeric features, including:

- Number of processes.
- Average, standard deviation, minimum, and maximum burst time.
- Relative burst-time variation.
- Average arrival time, arrival-time standard deviation, and arrival-time span.
- Average priority, priority standard deviation, and priority diversity.
- Round Robin time quantum.
- Correlation between process priorities and burst times.
- Correlation between process priorities and arrival times.

### Recommendation workflow

1. Collect the process workload and selected optimization objective.
2. Extract numeric workload features.
3. Predict a scheduling algorithm using the trained classifier.
4. Display the recommendation and its trade-offs.
5. Simulate all six algorithms for the current workload.
6. Compare measured metrics and check whether the recommendation matches a best-performing algorithm.

The model's reported score is a predicted class probability, not a guarantee of optimal performance. The measured comparison provides an additional validation layer.

## Scheduling Metrics

The simulator calculates the following metrics for each process:

- **Arrival Time:** Time at which the process becomes available.
- **Burst Time:** CPU execution time required by the process.
- **Start Time:** First time the process receives CPU execution.
- **Completion Time:** Time at which the process finishes execution.
- **Turnaround Time:** Total time from arrival to completion.
- **Waiting Time:** Total time spent waiting for CPU execution.
- **Response Time:** Time from arrival until the process first receives CPU execution.

The formulas are:

- Turnaround Time = Completion Time − Arrival Time
- Waiting Time = Turnaround Time − Burst Time
- Response Time = First Start Time − Arrival Time

The simulator also calculates average waiting, turnaround, and response times across all processes.

## Project Structure

```text
CPU-Scheduling-Simulator/
├── main.py
├── process.py
├── scheduler.py
├── advisor.py
├── evaluate_advisor.py
├── requirements.txt
├── tests/
│   ├── test_scheduler.py
│   └── test_advisor.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or later
- scikit-learn for the AI Scheduling Advisor
- pytest for running tests

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/arjungupt771/CPU-Scheduling-Simulator.git
cd CPU-Scheduling-Simulator
```

### 2. Create and activate a virtual environment

**Linux or macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the simulator

```bash
python main.py
```

Enter the number of processes, then provide each process's ID, burst time, arrival time, and priority.

### 5. Choose a scheduling option

The interactive menu provides:

1. First Come First Served (FCFS)
2. Shortest Job First (SJF)
3. Shortest Remaining Time First (SRTF)
4. Round Robin
5. Priority Scheduling (Non-Preemptive)
6. Priority Scheduling (Preemptive)
7. Run All Algorithms
8. AI Scheduling Advisor
9. Exit

For Round Robin, provide a positive time quantum. Press Enter to use the default value of 3.

When using the AI advisor for the first time, the model trains on synthetic workloads. Select an optimization objective and time quantum to receive a recommendation and compare it with the measured simulation results.

## Evaluating the AI Advisor

Run the evaluation script:

```bash
python evaluate_advisor.py
```

The default experiment trains the advisor on 1,500 synthetic workloads and evaluates it on 100 generated workloads using a separate random seed.

The evaluation reports:

- **Exact-match rate:** Percentage of workloads for which the recommendation is among the algorithms achieving the best measured score. Tied best algorithms count as correct.
- **Average score gap:** Difference between the recommended algorithm's score and the best measured score. Zero indicates no gap.

Lower scores are better for all five objectives. Score gaps use objective-specific units and should only be compared within the same objective.

### Five-seed benchmark

The advisor was evaluated on five generated test sets of 100 workloads each, using training seed `42` and evaluation seeds `2026` through `2030`. Each run used 1,500 training workloads.

| Objective | Average exact-match rate | Observed range |
|---|---:|---:|
| Balanced performance | 77.0% | 75–80% |
| Waiting time | 82.8% | 77–86% |
| Turnaround time | 82.8% | 77–86% |
| Response time | 77.0% | 66–84% |
| Priority-aware waiting | 59.4% | 56–63% |

These results describe this particular synthetic-workload experiment. They do not guarantee accuracy on real operating-system workloads. Additional testing across different workload distributions is needed to assess generalization.

## Running Tests

Install dependencies if necessary:

```bash
python -m pip install -r requirements.txt
```

Run the complete test suite:

```bash
python -m pytest -v
```

The current test suite contains **38 tests** covering scheduling calculations, preemption, idle periods, Round Robin behavior, input validation, menu interactions, Gantt chart formatting, feature extraction, objective scoring, and advisor recommendations.

## Implementation Details

- `process.py` defines the process model, scheduling results, timeline segments, and report metrics.
- `scheduler.py` implements the six scheduling algorithms.
- `advisor.py` extracts workload features, generates synthetic training workloads, trains the Random Forest models, and produces recommendations.
- `main.py` handles terminal interaction, scheduling selection, report formatting, and advisor integration.
- `evaluate_advisor.py` evaluates recommendations against measured algorithm performance.
- `tests/test_scheduler.py` tests scheduling behavior and terminal interactions.
- `tests/test_advisor.py` tests advisor features, scoring, and recommendations.

## Scope and Limitations

- The simulator models CPU scheduling using integer arrival and burst times.
- Preemptive algorithms simulate execution in one-time-unit increments.
- Lower numerical priority values represent higher priorities.
- Round Robin uses a configurable positive time quantum.
- Synthetic training data may not represent real-world process distributions.
- Recommendation accuracy depends on the training and evaluation workloads.
- The simulator models scheduling behavior rather than actual operating-system process execution or real context-switch overhead.

## Future Enhancements

- Export scheduling reports to CSV.
- Generate consolidated benchmark reports across multiple random seeds.
- Evaluate model performance across broader workload distributions.
- Add graphical Gantt charts and performance visualizations.
- Measure and report simulated context switches.
- Explore alternative models and feature-engineering strategies.

## License

No license has been specified. Add a `LICENSE` file if you intend to publish the project for reuse by others.
