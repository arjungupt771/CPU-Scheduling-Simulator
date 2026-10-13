
from process import Process, ScheduleReport
from scheduler import Scheduler



def display_report(report: ScheduleReport) -> None:
    """Display a scheduling report with an aligned Gantt chart."""
    print("\n" + "=" * 82)
    print(report.algorithm)
    print("=" * 82)

    print("\nGantt Chart:")

    if report.timeline:
        widths = [
            max(7, len(f"P{segment.pid}") if segment.pid is not None else 6)
            for segment in report.timeline
        ]

        # Keep every block wide enough for its label and boundaries.
        widths = [
            max(width, len(str(segment.start_time)) + 1,
                len(str(segment.end_time)) + 1)
            for width, segment in zip(widths, report.timeline)
        ]

        top_border = "+"
        process_row = "|"
        bottom_border = "+"
        time_row = ""

        for width, segment in zip(widths, report.timeline):
            label = f"P{segment.pid}" if segment.pid is not None else "IDLE"

            top_border += "-" * width + "+"
            process_row += f"{label:^{width}}|"
            bottom_border += "-" * width + "+"

        time_row = str(report.timeline[0].start_time)

        for width, segment in zip(widths, report.timeline):
            time_row += (
                " " * max(1, width - len(str(segment.end_time)) + 1)
                + str(segment.end_time)
            )

        print(top_border)
        print(process_row)
        print(bottom_border)
        print(time_row)

    print("\n")

    print(
        f"{'PID':<6}"
        f"{'Arrival':<9}"
        f"{'Burst':<8}"
        f"{'Priority':<10}"
        f"{'Start':<8}"
        f"{'Complete':<11}"
        f"{'Waiting':<9}"
        f"{'Turnaround':<12}"
        f"{'Response':<9}"
    )
    print("-" * 82)

    for result in report.results:
        print(
            f"{result.pid:<6}"
            f"{result.arrival_time:<9}"
            f"{result.burst_time:<8}"
            f"{result.priority:<10}"
            f"{result.start_time:<8}"
            f"{result.completion_time:<11}"
            f"{result.waiting_time:<9}"
            f"{result.turnaround_time:<12}"
            f"{result.response_time:<9}"
        )

    print("-" * 82)
    print(f"Average waiting time:    {report.average_waiting_time:.2f}")
    print(
        f"Average turnaround time: "
        f"{report.average_turnaround_time:.2f}"
    )
    print(f"Average response time:   {report.average_response_time:.2f}")



def display_comparison(reports: list[ScheduleReport]) -> None:
    """Compare average metrics across scheduling algorithms."""
    print("\n" + "=" * 100)
    print("SCHEDULING ALGORITHM COMPARISON")
    print("=" * 100)

    print(
        f"{'Algorithm':<42}"
        f"{'Avg Waiting':>14}"
        f"{'Avg Turnaround':>18}"
        f"{'Avg Response':>16}"
    )
    print("-" * 100)

    for report in reports:
        print(
            f"{report.algorithm:<42}"
            f"{report.average_waiting_time:>14.2f}"
            f"{report.average_turnaround_time:>18.2f}"
            f"{report.average_response_time:>16.2f}"
        )

    print("-" * 100)

    best_waiting = min(reports, key=lambda r: r.average_waiting_time)
    best_turnaround = min(
        reports, key=lambda r: r.average_turnaround_time
    )
    best_response = min(reports, key=lambda r: r.average_response_time)

    print(f"\nLowest average waiting time: {best_waiting.algorithm}")
    print(f"Lowest average turnaround time: {best_turnaround.algorithm}")
    print(f"Lowest average response time: {best_response.algorithm}")


def read_integer(
    prompt: str,
    minimum: int,
    default: int | None = None,
) -> int:
    """Read and validate an integer from the terminal."""
    while True:
        suffix = f" [{default}]" if default is not None else ""
        raw_value = input(f"{prompt}{suffix}: ").strip()

        if not raw_value and default is not None:
            return default

        try:
            value = int(raw_value)
        except ValueError:
            print("Please enter a valid whole number.")
            continue

        if value < minimum:
            print(f"Value must be at least {minimum}.")
            continue

        return value


def read_processes() -> list[Process]:
    """Collect process details interactively."""
    print("\nCPU SCHEDULING SIMULATOR")
    print("-" * 32)

    count = read_integer("Number of processes", minimum=1)
    processes: list[Process] = []
    used_ids: set[int] = set()

    for index in range(count):
        print(f"\nProcess {index + 1}")

        while True:
            pid = read_integer("Process ID", minimum=1)
            if pid in used_ids:
                print("That process ID already exists. Use a unique ID.")
                continue
            used_ids.add(pid)
            break

        burst_time = read_integer("Burst time", minimum=1)
        arrival_time = read_integer("Arrival time", minimum=0)
        priority = read_integer("Priority (lower number = higher priority)", minimum=0)

        processes.append(
            Process(
                pid=pid,
                burst_time=burst_time,
                arrival_time=arrival_time,
                priority=priority,
            )
        )

    return processes



def main() -> None:
    """Run selected CPU scheduling algorithms interactively."""
    try:
        processes = read_processes()
        scheduler = Scheduler(processes)

        while True:
            print("\n" + "=" * 42)
            print("CPU SCHEDULING ALGORITHM MENU")
            print("=" * 42)
            print("1. First Come First Served (FCFS)")
            print("2. Shortest Job First (SJF)")
            print("3. Shortest Remaining Time First (SRTF)")
            print("4. Round Robin")
            print("5. Priority Scheduling (Non-Preemptive)")
            print("6. Priority Scheduling (Preemptive)")
            print("7. Run All Algorithms")
            print("8. Exit")
            print("=" * 42)

            choice = read_integer(
                "Select an option",
                minimum=1,
            )

            if choice > 8:
                print("Invalid option. Please choose between 1 and 8.")
                continue

            if choice == 8:
                print("Exiting CPU Scheduling Simulator. Goodbye!")
                break

            if choice == 4 or choice == 7:
                quantum = read_integer(
                    "Round Robin time quantum",
                    minimum=1,
                    default=3,
                )
            else:
                quantum = 3

            algorithm_map = {
                1: lambda: scheduler.first_come_first_served(),
                2: lambda: scheduler.shortest_job_first(),
                3: lambda: scheduler.shortest_remaining_time_first(),
                4: lambda: scheduler.round_robin(quantum),
                5: lambda: scheduler.priority_scheduling(),
                6: lambda: scheduler.preemptive_priority_scheduling(),
            }

            if choice == 7:
                reports = [
                    scheduler.first_come_first_served(),
                    scheduler.shortest_job_first(),
                    scheduler.shortest_remaining_time_first(),
                    scheduler.round_robin(quantum),
                    scheduler.priority_scheduling(),
                    scheduler.preemptive_priority_scheduling(),
                ]
            else:
                reports = [algorithm_map[choice]()]

            for report in reports:
                display_report(report)

            if len(reports) > 1:
                display_comparison(reports)

    except (KeyboardInterrupt, EOFError):
        print("\n\nSimulation cancelled.")
    except ValueError as error:
        print(f"\nInput error: {error}")


if __name__ == "__main__":
    main()
