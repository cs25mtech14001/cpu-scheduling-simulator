# Manual Verification Example

Use this small workload whenever you want to visually verify that the scheduler is producing sensible results.

## Input

| Process | Arrival | Burst | Priority | Queue |
|---|---:|---:|---:|---:|
| P1 | 0 | 5 | 2 | 1 |
| P2 | 1 | 3 | 1 | 1 |
| P3 | 2 | 2 | 3 | 2 |

Round Robin uses a time quantum of **2**.

## Formulae

```text
Turnaround Time = Completion Time - Arrival Time
Waiting Time    = Turnaround Time - Burst Time
Average Metric  = Sum of metric / Number of processes
```

## FCFS — manual answer

Gantt chart:

```text
0      5      8      10
|  P1  |  P2  |  P3  |
```

| Process | Completion | Turnaround | Waiting |
|---|---:|---:|---:|
| P1 | 5 | 5 | 0 |
| P2 | 8 | 7 | 4 |
| P3 | 10 | 8 | 6 |

```text
Average Waiting    = 3.33
Average Turnaround = 6.67
```

## SJF — manual answer

Gantt chart:

```text
0      5    7      10
|  P1  | P3 |  P2  |
```

| Process | Completion | Turnaround | Waiting |
|---|---:|---:|---:|
| P1 | 5 | 5 | 0 |
| P2 | 10 | 9 | 6 |
| P3 | 7 | 5 | 3 |

```text
Average Waiting    = 3.00
Average Turnaround = 6.33
```

## Round Robin (quantum = 2) — manual answer

Gantt chart:

```text
0  2  4  6  8  9  10
|P1|P2|P3|P1|P2|P1|
```

| Process | Completion | Turnaround | Waiting |
|---|---:|---:|---:|
| P1 | 10 | 10 | 5 |
| P2 | 9 | 8 | 5 |
| P3 | 6 | 4 | 2 |

```text
Average Waiting    = 4.00
Average Turnaround = 7.33
```

## Run the visual test

From the repository root:

```bash
bash tests/test_algorithms.sh
```

Unlike a smoke test, this command prints the **actual Gantt chart, process table, averages, and reference comparison** for each scheduler.
