
from collections import deque
from typing import Callable, Iterable

from process import (
    Process,
    ProcessResult,
    ScheduleReport,
    TimelineSegment,
)


class Scheduler:
    """Implements non-preemptive and preemptive CPU scheduling."""

    def __init__(self, processes: Iterable[Process]) -> None:
        self.processes = tuple(processes)

        if not self.processes:
            raise ValueError("At least one process is required.")

        process_ids = [process.pid for process in self.processes]

        if len(process_ids) != len(set(process_ids)):
            raise ValueError("Process IDs must be unique.")

    @staticmethod
    def _add_segment(
        timeline: list[TimelineSegment],
        start: int,
        end: int,
        pid: int | None,
    ) -> None:
        """Add a timeline segment and merge adjacent identical segments."""
        if end <= start:
            return

        if (
            timeline
            and timeline[-1].pid == pid
            and timeline[-1].end_time == start
        ):
            previous = timeline[-1]
            timeline[-1] = TimelineSegment(
                previous.start_time, end, pid
            )
        else:
            timeline.append(TimelineSegment(start, end, pid))

    def _build_report(
        self,
        algorithm: str,
        timeline: list[TimelineSegment],
        first_start: dict[int, int],
        completion: dict[int, int],
    ) -> ScheduleReport:
        """Calculate process metrics from the completed schedule."""
        results = []

        for process in sorted(self.processes, key=lambda p: p.pid):
            if process.pid not in completion:
                raise RuntimeError(
                    f"Process {process.pid} was not completed."
                )

            completion_time = completion[process.pid]
            turnaround_time = (
                completion_time - process.arrival_time
            )
            waiting_time = turnaround_time - process.burst_time
            response_time = (
                first_start[process.pid] - process.arrival_time
            )

            results.append(
                ProcessResult(
                    pid=process.pid,
                    arrival_time=process.arrival_time,
                    burst_time=process.burst_time,
                    priority=process.priority,
                    start_time=first_start[process.pid],
                    completion_time=completion_time,
                    waiting_time=waiting_time,
                    turnaround_time=turnaround_time,
                    response_time=response_time,
                )
            )

        return ScheduleReport(
            algorithm=algorithm,
            results=tuple(results),
            timeline=tuple(timeline),
        )

    def _run_non_preemptive(
        self,
        algorithm: str,
        selection_key: Callable[[Process], tuple[int, ...]],
    ) -> ScheduleReport:
        """Run a non-preemptive scheduling algorithm."""
        pending = list(self.processes)
        timeline: list[TimelineSegment] = []
        first_start: dict[int, int] = {}
        completion: dict[int, int] = {}
        current_time = 0

        while pending:
            available = [
                process
                for process in pending
                if process.arrival_time <= current_time
            ]

            if not available:
                next_arrival = min(
                    process.arrival_time for process in pending
                )
                self._add_segment(
                    timeline, current_time, next_arrival, None
                )
                current_time = next_arrival
                continue

            process = min(available, key=selection_key)
            start_time = current_time
            end_time = start_time + process.burst_time

            first_start[process.pid] = start_time
            self._add_segment(
                timeline, start_time, end_time, process.pid
            )

            current_time = end_time
            completion[process.pid] = current_time
            pending.remove(process)

        return self._build_report(
            algorithm, timeline, first_start, completion
        )

    def first_come_first_served(self) -> ScheduleReport:
        """Schedule processes in arrival order."""
        return self._run_non_preemptive(
            "First Come First Served (FCFS)",
            lambda p: (p.arrival_time, p.pid),
        )

    def shortest_job_first(self) -> ScheduleReport:
        """Run non-preemptive Shortest Job First."""
        return self._run_non_preemptive(
            "Shortest Job First (SJF)",
            lambda p: (p.burst_time, p.arrival_time, p.pid),
        )

    def priority_scheduling(self) -> ScheduleReport:
        """Run non-preemptive priority scheduling.

        A lower priority number represents a higher priority.
        """
        return self._run_non_preemptive(
            "Priority Scheduling (Non-Preemptive)",
            lambda p: (p.priority, p.arrival_time, p.pid),
        )

    def _run_preemptive(
        self,
        algorithm: str,
        selection_key: Callable[
            [Process, int], tuple[int, ...]
        ],
    ) -> ScheduleReport:
        """Run a preemptive algorithm one time unit at a time.

        When scheduling keys tie, the currently running process is
        preferred to avoid unnecessary context switches.
        """
        ordered = sorted(
            self.processes,
            key=lambda p: (p.arrival_time, p.pid),
        )

        remaining = {
            process.pid: process.burst_time
            for process in ordered
        }

        timeline: list[TimelineSegment] = []
        first_start: dict[int, int] = {}
        completion: dict[int, int] = {}

        current_time = 0
        current_pid: int | None = None

        while len(completion) < len(ordered):
            available = [
                process
                for process in ordered
                if (
                    process.arrival_time <= current_time
                    and remaining[process.pid] > 0
                )
            ]

            if not available:
                next_arrival = min(
                    process.arrival_time
                    for process in ordered
                    if remaining[process.pid] > 0
                )

                self._add_segment(
                    timeline, current_time, next_arrival, None
                )
                current_time = next_arrival
                current_pid = None
                continue

            process = min(
                available,
                key=lambda p: (
                    selection_key(p, remaining[p.pid]),
                    0 if p.pid == current_pid else 1,
                    p.arrival_time,
                    p.pid,
                ),
            )

            current_pid = process.pid
            first_start.setdefault(process.pid, current_time)

            self._add_segment(
                timeline,
                current_time,
                current_time + 1,
                process.pid,
            )

            remaining[process.pid] -= 1
            current_time += 1

            if remaining[process.pid] == 0:
                completion[process.pid] = current_time
                current_pid = None

        return self._build_report(
            algorithm, timeline, first_start, completion
        )

    def shortest_remaining_time_first(self) -> ScheduleReport:
        """Run preemptive SJF (Shortest Remaining Time First)."""
        return self._run_preemptive(
            "Shortest Remaining Time First (SRTF)",
            lambda process, remaining: (remaining,),
        )

    def preemptive_priority_scheduling(self) -> ScheduleReport:
        """Run preemptive priority scheduling.

        Lower priority numbers represent higher priority. A running
        process is interrupted only when a strictly higher-priority
        process becomes available.
        """
        return self._run_preemptive(
            "Priority Scheduling (Preemptive)",
            lambda process, remaining: (process.priority,),
        )

    def round_robin(self, quantum: int) -> ScheduleReport:
        """Run Round Robin scheduling with arrival-time support."""
        if quantum <= 0:
            raise ValueError("Time quantum must be positive.")

        ordered = sorted(
            self.processes,
            key=lambda p: (p.arrival_time, p.pid),
        )

        remaining = {
            process.pid: process.burst_time
            for process in ordered
        }

        timeline: list[TimelineSegment] = []
        first_start: dict[int, int] = {}
        completion: dict[int, int] = {}

        ready: deque[Process] = deque()
        next_process = 0
        current_time = 0

        while next_process < len(ordered) or ready:
            if not ready:
                next_arrival = ordered[next_process].arrival_time

                if current_time < next_arrival:
                    self._add_segment(
                        timeline, current_time, next_arrival, None
                    )
                    current_time = next_arrival

                while (
                    next_process < len(ordered)
                    and ordered[next_process].arrival_time <= current_time
                ):
                    ready.append(ordered[next_process])
                    next_process += 1

            process = ready.popleft()
            first_start.setdefault(process.pid, current_time)

            execution_time = min(
                quantum, remaining[process.pid]
            )
            end_time = current_time + execution_time

            self._add_segment(
                timeline, current_time, end_time, process.pid
            )

            current_time = end_time
            remaining[process.pid] -= execution_time

            while (
                next_process < len(ordered)
                and ordered[next_process].arrival_time <= current_time
            ):
                ready.append(ordered[next_process])
                next_process += 1

            if remaining[process.pid] == 0:
                completion[process.pid] = current_time
            else:
                ready.append(process)

        return self._build_report(
            f"Round Robin (quantum={quantum})",
            timeline,
            first_start,
            completion,
        )
