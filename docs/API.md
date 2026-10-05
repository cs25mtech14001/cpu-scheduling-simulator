# API

## POST /simulate

Request:

```json
{
  "algorithm": "rr",
  "input": {
    "time_quantum": 2,
    "quantum": 2,
    "processes": [
      {"pid":"P1","arrival":0,"burst":5,"priority":2}
    ]
  }
}
```

The response contains `gantt_chart`, per-process `results`, `average_waiting`, and `average_turnaround`.

## GET /health

Returns:

```json
{"status":"ok"}
```
