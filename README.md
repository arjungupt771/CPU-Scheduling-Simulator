# CPU Scheduling Simulator

A Python-based CPU Scheduling Simulator that implements six operating system scheduling algorithms, visualizes process execution using Gantt charts, and compares scheduling performance through waiting, turnaround, and response time metrics.

## Features

- **Six CPU scheduling algorithms** with preemptive and non-preemptive implementations.
- **Interactive terminal interface** for entering processes and selecting algorithms.
- **Gantt chart visualization** with process labels, execution intervals, and CPU idle periods.
- **Process-level metrics** including start time, completion time, waiting time, turnaround time, and response time.
- **Algorithm comparison** based on average waiting, turnaround, and response times.
- **Input validation** for process IDs, burst times, arrival times, priorities, and Round Robin time quantum.
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

## Scheduling Metrics

The simulator calculates the following metrics for each process:

- **Arrival Time:** Time at which the process becomes available.
- **Burst Time:** CPU execution time required by the process.
- **Start Time:** First time the process receives CPU execution.
- **Completion Time:** Time at which the process finishes execution.
- **Turnaround Time:** Total time from arrival to completion.
- **Waiting Time:** Total time spent waiting for CPU execution.
- **Response Time:** Time from arrival until the process first receives CPU execution.

The formulas used are:

- Turnaround Time = Completion Time − Arrival Time
- Waiting Time = Turnaround Time − Burst Time
- Response Time = First Start Time − Arrival Time

The simulator also calculates average waiting, turnaround, and response times across all processes.

## Project Structure

```text
Cpp-Projects/
├── main.py
├── process.py
├── scheduler.py
├── tests/
│   └── test_scheduler.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or later
- pytest for running the test suite

The scheduling simulator itself uses Python's standard library. Pytest is needed only for testing.

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Cpp-Projects
```

Replace `<YOUR_REPOSITORY_URL>` with your GitHub repository URL.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Run the simulator

```bash
python main.py
```

Enter the number of processes and provide each process's ID, burst time, arrival time, and priority when prompted.

### 4. Select a scheduling algorithm

The interactive menu provides these options:

1. First Come First Served (FCFS)
2. Shortest Job First (SJF)
3. Shortest Remaining Time First (SRTF)
4. Round Robin
5. Priority Scheduling (Non-Preemptive)
6. Priority Scheduling (Preemptive)
7. Run All Algorithms
8. Exit

For Round Robin, enter a positive time quantum. Press Enter to use the default quantum of 3.

The menu allows you to run multiple algorithms against the same set of processes without re-entering process information.

## Example Output

A scheduling report contains a Gantt chart, a process metrics table, and average performance metrics.

```text
Gantt Chart:

+-------+-------+-------+
|  P1   |  P2   |  P3   |
+-------+-------+-------+
0       5       8       16

Average waiting time:    3.33
Average turnaround time: 8.67
Average response time:   3.33
```

The values above illustrate the output format; actual results depend on the processes and scheduling algorithm selected.

When the CPU has no process available to execute, the timeline records an `IDLE` segment.

## Running Tests

Install pytest if it is not already installed:

```bash
python -m pip install pytest
```

Run the complete test suite:

```bash
python -m pytest -v
```

The project currently has **25 passing tests** covering scheduling calculations, preemption, idle periods, Round Robin behavior, input validation, menu interactions, and Gantt chart formatting.

## Implementation Details

- `process.py` defines the process model, scheduling results, timeline segments, and report metrics.
- `scheduler.py` implements the scheduling algorithms and calculates process execution metrics.
- `main.py` handles terminal input, algorithm selection, report formatting, and performance comparisons.
- `tests/test_scheduler.py` contains the automated test suite.

## Scope and Limitations

- The simulator models CPU scheduling using integer arrival and burst times.
- Preemptive algorithms simulate execution in one-time-unit increments.
- The priority convention uses lower numbers for higher priorities.
- Round Robin uses a configurable positive time quantum.
- The simulator focuses on scheduling behavior and metrics rather than operating-system process execution or real context-switch overhead.

## Future Enhancements

- Export scheduling reports to CSV.
- Add graphical Gantt charts.
- Support user-selectable algorithms in batch experiments.
- Add performance visualizations for comparing algorithms.
- Measure and report simulated context switches.

## License

No license has been specified yet. Add a `LICENSE` file if you intend to publish the project for reuse by others.