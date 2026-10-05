const express = require("express");
const fs = require("fs");
const path = require("path");
const { execFile } = require("child_process");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;

const frontendDir = path.join(__dirname, "..", "frontend");
const backendDir = path.join(__dirname, "..", "backend");
const dataDir = path.join(__dirname, "..", "data");

const ALGORITHMS = new Set([
  "fcfs", "sjf", "srtf", "priority", "rr",
  "hrrn", "mqs", "mlfq", "ljf", "lrtf"
]);

app.use(cors());
app.use(express.json({ limit: "64kb" }));
app.use(express.static(frontendDir));

function validateInput(input) {
  if (!input || !Array.isArray(input.processes) || input.processes.length === 0) {
    return "At least one process is required.";
  }
  if (input.processes.length > 1000) {
    return "At most 1000 processes are supported.";
  }

  const ids = new Set();
  for (const p of input.processes) {
    if (!p.pid || ids.has(p.pid)) return "Process IDs must be non-empty and unique.";
    ids.add(p.pid);

    if (!Number.isInteger(p.arrival) || p.arrival < 0) return "Arrival times must be non-negative integers.";
    if (!Number.isInteger(p.burst) || p.burst <= 0) return "Burst times must be positive integers.";
    if (p.priority !== undefined && (!Number.isInteger(p.priority) || p.priority < 0)) {
      return "Priority values must be non-negative integers.";
    }
  }

  if (input.time_quantum !== undefined &&
      (!Number.isInteger(input.time_quantum) || input.time_quantum <= 0)) {
    return "Time quantum must be a positive integer.";
  }

  return null;
}

app.post("/simulate", (req, res) => {
  const { algorithm, input } = req.body || {};

  if (!ALGORITHMS.has(algorithm)) {
    return res.status(400).json({ error: "Unsupported scheduling algorithm." });
  }

  const validationError = validateInput(input);
  if (validationError) {
    return res.status(400).json({ error: validationError });
  }

  const execPath = path.join(backendDir, algorithm);
  if (!fs.existsSync(execPath)) {
    return res.status(503).json({
      error: `Backend executable '${algorithm}' is not built. Run 'npm run build' first.`
    });
  }

  const inputPath = path.join(dataDir, "input.json");
  const outputPath = path.join(dataDir, "output.json");

  try {
    fs.writeFileSync(inputPath, JSON.stringify(input, null, 2));
    if (fs.existsSync(outputPath)) fs.unlinkSync(outputPath);
  } catch (error) {
    return res.status(500).json({ error: "Unable to prepare simulation input." });
  }

  execFile(execPath, [], {
    cwd: backendDir,
    timeout: 10000,
    maxBuffer: 1024 * 1024
  }, (error, stdout, stderr) => {
    if (error) {
      console.error(stderr || error.message);
      return res.status(500).json({ error: "Scheduling simulation failed." });
    }

    try {
      const outputData = JSON.parse(fs.readFileSync(outputPath, "utf8"));
      return res.json(outputData);
    } catch (parseError) {
      console.error(parseError);
      return res.status(500).json({ error: "Invalid scheduler output." });
    }
  });
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.listen(PORT, () => {
  console.log(`CPU Scheduler Simulator: http://localhost:${PORT}`);
});
