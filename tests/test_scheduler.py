
import pytest

from process import Process
from scheduler import Scheduler
from unittest.mock import patch
import main
from main import read_integer, read_processes
from process import Process

def test_fcfs_calculates_metrics_correctly():
    scheduler = Scheduler([
        Process(pid=1, burst_time=3, arrival_time=0),
        Process(pid=2, burst_time=2, arrival_time=5),
    ])

    report = scheduler.first_come_first_served()
    results = {result.pid: result for result in report.results}

    assert results[1].completion_time == 3
    assert results[2].start_time == 5
    assert results[2].completion_time == 7
    assert results[2].waiting_time == 0
    assert results[2].turnaround_time == 2


def test_cpu_idle_time_is_recorded():
    scheduler = Scheduler([
        Process(pid=1, burst_time=2, arrival_time=4),
    ])

    report = scheduler.first_come_first_served()

    assert report.timeline[0].pid is None
    assert report.timeline[0].start_time == 0
    assert report.timeline[0].end_time == 4

    assert report.timeline[1].pid == 1
    assert report.timeline[1].start_time == 4
    assert report.timeline[1].end_time == 6


def test_sjf_selects_shortest_available_process():
    scheduler = Scheduler([
        Process(pid=1, burst_time=6, arrival_time=0),
        Process(pid=2, burst_time=2, arrival_time=1),
        Process(pid=3, burst_time=4, arrival_time=1),
    ])

    report = scheduler.shortest_job_first()

    # P1 runs first because it is the only available process.
    # P2 then runs before P3.
    assert [segment.pid for segment in report.timeline] == [1, 2, 3]


def test_round_robin_metrics():
    scheduler = Scheduler([
        Process(pid=1, burst_time=5, arrival_time=0),
        Process(pid=2, burst_time=3, arrival_time=1),
    ])

    report = scheduler.round_robin(quantum=2)
    results = {result.pid: result for result in report.results}

    assert results[1].completion_time == 8
    assert results[1].waiting_time == 3
    assert results[1].response_time == 0

    assert results[2].completion_time == 7
    assert results[2].waiting_time == 3
    assert results[2].response_time == 1


def test_round_robin_rejects_invalid_quantum():
    scheduler = Scheduler([
        Process(pid=1, burst_time=5),
    ])

    with pytest.raises(ValueError):
        scheduler.round_robin(quantum=0)

    with pytest.raises(ValueError):
        scheduler.round_robin(quantum=-1)


def test_duplicate_process_ids_are_rejected():
    with pytest.raises(ValueError):
        Scheduler([
            Process(pid=1, burst_time=3),
            Process(pid=1, burst_time=5),
        ])


def test_running_algorithms_does_not_change_input():
    processes = [
        Process(pid=1, burst_time=8, arrival_time=0),
        Process(pid=2, burst_time=2, arrival_time=1),
        Process(pid=3, burst_time=4, arrival_time=2),
    ]

    scheduler = Scheduler(processes)

    fcfs_before = scheduler.first_come_first_served()
    scheduler.shortest_job_first()
    scheduler.round_robin(quantum=2)
    scheduler.priority_scheduling()
    fcfs_after = scheduler.first_come_first_served()

    assert fcfs_before == fcfs_after



def test_srtf_preempts_when_shorter_process_arrives():
    scheduler = Scheduler([
        Process(pid=1, burst_time=8, arrival_time=0),
        Process(pid=2, burst_time=4, arrival_time=1),
    ])

    report = scheduler.shortest_remaining_time_first()
    results = {result.pid: result for result in report.results}

    assert [
        (segment.start_time, segment.end_time, segment.pid)
        for segment in report.timeline
    ] == [
        (0, 1, 1),
        (1, 5, 2),
        (5, 12, 1),
    ]

    assert results[1].completion_time == 12
    assert results[1].waiting_time == 4
    assert results[2].completion_time == 5
    assert results[2].waiting_time == 0


def test_preemptive_priority_interrupts_lower_priority():
    scheduler = Scheduler([
        Process(pid=1, burst_time=5, arrival_time=0, priority=3),
        Process(pid=2, burst_time=2, arrival_time=2, priority=1),
    ])

    report = scheduler.preemptive_priority_scheduling()
    results = {result.pid: result for result in report.results}

    assert [
        (segment.start_time, segment.end_time, segment.pid)
        for segment in report.timeline
    ] == [
        (0, 2, 1),
        (2, 4, 2),
        (4, 7, 1),
    ]

    assert results[1].completion_time == 7
    assert results[1].waiting_time == 2
    assert results[2].completion_time == 4
    assert results[2].waiting_time == 0


def test_preemptive_priority_does_not_interrupt_on_equal_priority():
    scheduler = Scheduler([
        Process(pid=1, burst_time=4, arrival_time=0, priority=2),
        Process(pid=2, burst_time=2, arrival_time=1, priority=2),
    ])

    report = scheduler.preemptive_priority_scheduling()

    assert [
        (segment.start_time, segment.end_time, segment.pid)
        for segment in report.timeline
    ] == [
        (0, 4, 1),
        (4, 6, 2),
    ]


def test_srtf_preserves_running_process_on_equal_remaining_time():
    scheduler = Scheduler([
        Process(pid=1, burst_time=4, arrival_time=0),
        Process(pid=2, burst_time=3, arrival_time=1),
    ])

    report = scheduler.shortest_remaining_time_first()

    assert [
        (segment.start_time, segment.end_time, segment.pid)
        for segment in report.timeline
    ] == [
        (0, 4, 1),
        (4, 7, 2),
    ]


def test_preemptive_algorithms_handle_initial_idle_time():
    scheduler = Scheduler([
        Process(pid=1, burst_time=2, arrival_time=3, priority=2),
        Process(pid=2, burst_time=1, arrival_time=7, priority=1),
    ])

    srtf_report = scheduler.shortest_remaining_time_first()
    priority_report = scheduler.preemptive_priority_scheduling()

    assert srtf_report.timeline[0].pid is None
    assert srtf_report.timeline[0].start_time == 0
    assert srtf_report.timeline[0].end_time == 3

    assert priority_report.timeline[0].pid is None
    assert priority_report.timeline[0].start_time == 0
    assert priority_report.timeline[0].end_time == 3

    assert srtf_report.results[0].completion_time == 5
    assert priority_report.results[1].completion_time == 8



def test_read_integer_accepts_valid_input():
    with patch("builtins.input", return_value="5"):
        assert read_integer("Enter value", minimum=1) == 5


def test_read_integer_rejects_invalid_then_accepts_valid_input():
    with patch("builtins.input", side_effect=["abc", "0", "3"]):
        assert read_integer("Enter value", minimum=1) == 3


def test_read_integer_uses_default_when_input_is_empty():
    with patch("builtins.input", return_value=""):
        assert read_integer(
            "Enter value",
            minimum=1,
            default=3,
        ) == 3


def test_read_processes_collects_user_input():
    user_inputs = [
        "2",       # Number of processes
        "1", "5", "0", "2",
        "2", "3", "1", "1",
    ]

    with patch("builtins.input", side_effect=user_inputs):
        processes = read_processes()

    assert processes == [
        Process(pid=1, burst_time=5, arrival_time=0, priority=2),
        Process(pid=2, burst_time=3, arrival_time=1, priority=1),
    ]


def test_read_processes_rejects_duplicate_ids():
    user_inputs = [
        "2",                  # Number of processes
        "1", "5", "0", "2",  # First process: ID, burst, arrival, priority
        "1",                  # Duplicate ID; rejected
        "2", "3", "1", "1",  # Second process: valid ID and remaining fields
    ]

    with patch("builtins.input", side_effect=user_inputs):
        processes = read_processes()

    assert [process.pid for process in processes] == [1, 2]
    assert processes[1] == Process(
        pid=2,
        burst_time=3,
        arrival_time=1,
        priority=1,
    )


def test_menu_runs_selected_algorithm_only():
    processes = [
        Process(pid=1, burst_time=5, arrival_time=0, priority=2)
    ]

    with (
        patch("main.read_processes", return_value=processes),
        patch("main.display_report") as display_report,
        patch("main.display_comparison") as display_comparison,
        patch("builtins.input", side_effect=["1", "8"]),
    ):
        main.main()

    display_report.assert_called_once()
    assert display_report.call_args.args[0].algorithm == (
        "First Come First Served (FCFS)"
    )
    display_comparison.assert_not_called()


def test_menu_runs_all_six_algorithms():
    processes = [
        Process(pid=1, burst_time=5, arrival_time=0, priority=2)
    ]

    with (
        patch("main.read_processes", return_value=processes),
        patch("main.display_report") as display_report,
        patch("main.display_comparison") as display_comparison,
        patch("builtins.input", side_effect=["7", "2", "8"]),
    ):
        main.main()

    assert display_report.call_count == 6
    display_comparison.assert_called_once()

    algorithms = [
        call.args[0].algorithm
        for call in display_report.call_args_list
    ]

    assert algorithms == [
        "First Come First Served (FCFS)",
        "Shortest Job First (SJF)",
        "Shortest Remaining Time First (SRTF)",
        "Round Robin (quantum=2)",
        "Priority Scheduling (Non-Preemptive)",
        "Priority Scheduling (Preemptive)",
    ]


def test_menu_rejects_out_of_range_choice(capsys):
    processes = [
        Process(pid=1, burst_time=5, arrival_time=0, priority=2)
    ]

    with (
        patch("main.read_processes", return_value=processes),
        patch("main.display_report") as display_report,
        patch("builtins.input", side_effect=["9", "8"]),
    ):
        main.main()

    output = capsys.readouterr().out

    assert "Invalid option" in output
    display_report.assert_not_called()


def test_menu_exits_without_running_algorithms(capsys):
    processes = [
        Process(pid=1, burst_time=5, arrival_time=0, priority=2)
    ]

    with (
        patch("main.read_processes", return_value=processes),
        patch("main.display_report") as display_report,
        patch("main.display_comparison") as display_comparison,
        patch("builtins.input", side_effect=["8"]),
    ):
        main.main()

    output = capsys.readouterr().out

    assert "Goodbye!" in output
    display_report.assert_not_called()
    display_comparison.assert_not_called()



def test_gantt_chart_displays_process_labels(capsys):
    process = Process(pid=1, burst_time=5, arrival_time=0, priority=2)
    report = Scheduler([process]).first_come_first_served()

    main.display_report(report)
    output = capsys.readouterr().out

    assert "P1" in output
    assert "Gantt Chart:" in output
    assert "0" in output
    assert "5" in output


def test_gantt_chart_displays_initial_idle_period(capsys):
    processes = [
        Process(pid=1, burst_time=2, arrival_time=3, priority=1)
    ]
    report = Scheduler(processes).first_come_first_served()

    main.display_report(report)
    output = capsys.readouterr().out

    assert "IDLE" in output
    assert "3" in output


def test_gantt_chart_displays_multiple_processes(capsys):
    processes = [
        Process(pid=1, burst_time=2, arrival_time=0, priority=1),
        Process(pid=2, burst_time=3, arrival_time=2, priority=2),
    ]
    report = Scheduler(processes).first_come_first_served()

    main.display_report(report)
    output = capsys.readouterr().out

    assert "P1" in output
    assert "P2" in output


def test_gantt_chart_supports_multi_digit_timestamps(capsys):
    process = Process(pid=1, burst_time=15, arrival_time=0, priority=1)
    report = Scheduler([process]).first_come_first_served()

    main.display_report(report)
    output = capsys.readouterr().out

    assert "15" in output
    assert "P1" in output
