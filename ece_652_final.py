#!/usr/bin/env python3

import math
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

#lcm of two int
def _lcm(a: int, b: int) -> int:
    return a * b // math.gcd(a, b)

#lcm of a list
def _hyper_period(periods: List[int]) -> int:
    hp = periods[0]
    for p in periods[1:]:
        hp = _lcm(hp, p)
    return hp

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class Task:

    def __init__(self, task_id: int, exec_time: float, period: float, deadline: float, scale: int = 1000):
        self.id = task_id
        self.e = int(round(exec_time * scale))
        self.p = int(round(period * scale))
        self.d = int(round(deadline * scale))

        if self.e <= 0 or self.p <= 0 or self.d <= 0:
            raise ValueError("Execution time, period, and deadline must be positive numbers.")

    # Sorting by period then task id implements RM priority order
    def __lt__(self, other: "Task") -> bool: 
        return (self.p, self.id) < (other.p, other.id)

#single instance of a periodic task
class Job:

    def __init__(self, task: Task, release_time: int):
        self.task = task
        self.remaining = task.e
        self.deadline = release_time + task.d

    def __repr__(self) -> str:
        return f"Job(T{self.task.id}, rem={self.remaining}, ddl={self.deadline})"


# ---------------------------------------------------------------------------
# Core RM simulation
# ---------------------------------------------------------------------------

def simulate_rm(tasks: List[Task]) -> Tuple[bool, List[int]]:

    num_tasks = len(tasks)
    preempts = [0] * num_tasks

    # Hyper‑period and simulation horizon (H + max deadline)
    hyper = _hyper_period([t.p for t in tasks])
    horizon = hyper + max(t.d for t in tasks)

    ready: List[Job] = []
    current: Job | None = None

    time = 0
    while time < horizon:
        # ------------------------------------------------------------
        # 1) Release new jobs (at every multiple of period)
        # ------------------------------------------------------------
        for task in tasks:
            if time % task.p == 0:
                ready.append(Job(task, time))

        # ------------------------------------------------------------
        # 2) Deadline check *before* executing this time unit
        # ------------------------------------------------------------
        for job in ready:
            if time >= job.deadline and job.remaining > 0:
                return False, preempts  # Deadline miss detected

        # ------------------------------------------------------------
        # 3) Select highest‑priority ready job
        # ------------------------------------------------------------
        if ready:
            chosen = min(ready, key=lambda j: (j.task.p, j.task.id))
        else:
            time += 1  # Idle CPU
            continue

        # ------------------------------------------------------------
        # 4) Pre‑emption accounting (only inside first hyper‑period)
        # ------------------------------------------------------------
        if current is not None and current is not chosen and time < hyper:
            preempts[current.task.id] += 1

        current = chosen

        # ------------------------------------------------------------
        # 5) Execute the chosen job for one time unit
        # ------------------------------------------------------------
        current.remaining -= 1
        if current.remaining == 0:
            ready.remove(current)
            current = None

        time += 1

        # Early exit: after hyper‑period, stop once all outstanding jobs have finished
        if time >= hyper and not ready:
            break

    return True, preempts

# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_workload(path: Path) -> List[Task]:
    tasks: List[Task] = []
    with path.open(encoding="utf‑8") as fh:
        for idx, line in enumerate(fh):
            if not line.strip():
                continue  # Skip blank lines safely
            try:
                e_str, p_str, d_str = (field.strip() for field in line.split(","))
                e, p, d = float(e_str), float(p_str), float(d_str)
            except ValueError as exc:
                raise ValueError(f"Invalid line in {path}: '{line.strip()}'") from exc
            tasks.append(Task(idx, e, p, d))

    if not tasks:
        raise ValueError(f"Input file '{path}' does not define any tasks.")

    return tasks

# ---------------------------------------------------------------------------
# Main 
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 ece_652_final.py <workload_file>", file=sys.stderr)
        sys.exit(1)

    workload_file = Path(sys.argv[1])
    if not workload_file.is_file():
        print(f"Error: '{workload_file}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    try:
        tasks = load_workload(workload_file)
    except ValueError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    feasible, preempts = simulate_rm(tasks)

    # ---------------------------------------------------------------------
    # output (two lines)
    # ---------------------------------------------------------------------
    if feasible:
        print("1")
        print(",".join(str(x) for x in preempts))
    else:
        print("0")
        print()  # Blank second line


if __name__ == "__main__":
    main()
