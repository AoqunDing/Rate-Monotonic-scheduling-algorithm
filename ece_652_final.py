#!/usr/bin/env python3

import math
import sys
from pathlib import Path
from typing import List, Tuple

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

if __name__ == "__main__":
    main()
