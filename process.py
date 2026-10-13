
from dataclasses import dataclass


@dataclass(frozen=True)
class Process:
    """Represents a process submitted to the CPU scheduler."""

    pid: int
    burst_time: int
    arrival_time: int = 0
    priority: int = 0

    def __post_init__(self) -> None:
        if self.pid <= 0:
            raise ValueError("Process ID must be positive.")

        if self.burst_time <= 0:
            raise ValueError("Burst time must be positive.")

        if self.arrival_time < 0:
            raise ValueError("Arrival time cannot be negative.")


@dataclass(frozen=True)
class ProcessResult:
    """Stores the scheduling metrics for a completed process."""

    pid: int
    arrival_time: int
    burst_time: int
    priority: int
    start_time: int
    completion_time: int
    waiting_time: int
    turnaround_time: int
    response_time: int


@dataclass(frozen=True)
class TimelineSegment:
    """Represents one continuous segment of CPU execution."""

    start_time: int
    end_time: int
    pid: int | None

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time


@dataclass(frozen=True)
class ScheduleReport:
    """Contains the results and execution timeline of an algorithm."""

    algorithm: str
    results: tuple[ProcessResult, ...]
    timeline: tuple[TimelineSegment, ...]

    @property
    def average_waiting_time(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            result.waiting_time for result in self.results
        ) / len(self.results)

    @property
    def average_turnaround_time(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            result.turnaround_time for result in self.results
        ) / len(self.results)

    @property
    def average_response_time(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            result.response_time for result in self.results
        ) / len(self.results)
