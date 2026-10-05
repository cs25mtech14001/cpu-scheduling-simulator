# CPU Scheduler Simulator

An interactive **Operating Systems project** for simulating and comparing CPU scheduling policies. The scheduling engine is implemented in **C++**, exposed through a lightweight **Node.js/Express API**, and visualized through a browser-based interface.

## Highlights

- **10 scheduling policies:** FCFS, SJF, SRTF, Priority, Round Robin, HRRN, Multilevel Queue, MLFQ, LJF, and LRTF.
- Uses `std::queue` and `std::priority_queue` to model ready queues and scheduling decisions.
- Computes completion time, turnaround time, waiting time, and average metrics.
- Generates an execution trace and renders a compact **Gantt chart** in the browser.
- JSON-based interface between the web layer and C++ scheduling engine.
- Input validation and API-level error handling.
- Makefile-based C++ build and smoke-test workflow.

## Architecture

```text
Browser UI
   │
   │ POST /simulate
   ▼
Node.js + Express
   │
   │ JSON input / process execution
   ▼
C++ Scheduling Engine
   ├── FCFS
   ├── SJF / SRTF
   ├── Priority
   ├── Round Robin
   ├── HRRN
   ├── Multilevel Queue / MLFQ
   └── LJF / LRTF
   │
   ▼
Scheduling Metrics + Execution Trace
   │
   ▼
Gantt Chart + Results Table
```

## Repository Structure

```text
.
├── backend/             # C++ scheduling implementations + JSON library
├── frontend/            # HTML/CSS/JS interface and visualization
├── server/              # Express API
├── data/                # Runtime input/output JSON
├── sample_data/         # Reproducible manual test cases
├── tests/               # Human-readable regression + validation tests
├── Makefile
├── package.json
└── README.md
```

## Requirements

- C++17 compiler (`g++` or compatible)
- Node.js 18+
- npm
- Python 3 (for the smoke-test script)

## Run Locally

### 1. Install server dependencies

```bash
npm install --prefix server
```

### 2. Build the C++ scheduling engine

```bash
npm run build
```

### 3. Start the application

```bash
npm start
```

Open:

```text
http://localhost:3000
```

## Testing

Run the full human-readable verification suite:

```bash
npm test
```

The test runner builds all 10 schedulers, executes a reproducible sample workload, prints each algorithm's Gantt chart, completion/turnaround/waiting times, and average metrics, and checks metric invariants. FCFS, SJF, and Round Robin are additionally compared against manually verified reference answers.

You can also run it directly:

```bash
bash tests/test_algorithms.sh
```

For the worked example and hand calculations, see [`docs/MANUAL_TEST.md`](docs/MANUAL_TEST.md).

## Scheduling Metrics

For every completed process:

- **Completion Time:** time at which the process finishes.
- **Turnaround Time:** `Completion Time - Arrival Time`.
- **Waiting Time:** `Turnaround Time - Burst Time`.

These metrics make it possible to compare scheduling policies under the same workload.

## Complexity Notes

The implementation uses different ready-queue strategies depending on the policy:

| Policy | Core structure / idea |
|---|---|
| FCFS | Arrival-order queue |
| SJF | Min-priority queue by burst time |
| SRTF | Min-priority queue by remaining time |
| Priority | Priority queue |
| RR | FIFO ready queue + time quantum |
| HRRN | Highest response-ratio selection |
| MQS | Multiple priority levels |
| MLFQ | Multiple feedback queues |
| LJF | Max-priority queue by burst time |
| LRTF | Max-priority queue by remaining time |

Actual runtime depends on workload size and the scheduling policy; benchmark claims should be added only after measuring them.

## Resume-Oriented Description

Use only the bullets that accurately describe **your own contribution**:

- Developed an interactive **CPU scheduling simulator in C++** supporting 10 scheduling policies and computing completion, waiting, and turnaround-time metrics.
- Implemented ready-queue management using **FIFO queues and priority queues**, including preemptive and non-preemptive scheduling behavior.
- Integrated the C++ scheduling engine with a **Node.js/Express REST API** using JSON for process configuration and execution results.
- Built a browser-based visualization layer that renders **CPU execution timelines as Gantt charts** and presents process-level scheduling metrics.

## Note on Attribution

If this repository is based on an existing implementation, preserve the original project's attribution/license requirements and describe your work as an **extension or enhancement** unless you independently implemented the corresponding components. Do not add performance or user-study numbers unless you have actually measured them.
