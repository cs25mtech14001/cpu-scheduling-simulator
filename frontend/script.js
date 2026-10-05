const form = document.getElementById("schedulerForm");
const tableBody = document.querySelector("#processTable tbody");
const outputSection = document.getElementById("outputSection");
const errorMessage = document.getElementById("errorMessage");
const runButton = document.getElementById("runButton");

document.getElementById("addProcess").addEventListener("click", () => {
  const index = tableBody.rows.length + 1;
  const row = document.createElement("tr");
  row.innerHTML = `
    <td><input name="pid" value="P${index}" /></td>
    <td><input name="arrival" type="number" min="0" value="0" /></td>
    <td><input name="burst" type="number" min="1" value="5" /></td>
    <td><input name="priority" type="number" min="0" value="1" /></td>
    <td><button type="button" class="icon-button remove-process" title="Remove process">×</button></td>
  `;
  tableBody.appendChild(row);
});

tableBody.addEventListener("click", (event) => {
  if (!event.target.classList.contains("remove-process")) return;
  if (tableBody.rows.length > 1) event.target.closest("tr").remove();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.textContent = "";

  const algorithm = document.getElementById("algorithm").value;
  const quantum = Number(document.getElementById("quantum").value);

  const processes = [...tableBody.rows].map(row => {
    const inputs = row.querySelectorAll("input");
    return {
      pid: inputs[0].value.trim(),
      arrival: Number(inputs[1].value),
      burst: Number(inputs[2].value),
      priority: Number(inputs[3].value)
    };
  });

  if (!Number.isInteger(quantum) || quantum <= 0) {
    errorMessage.textContent = "Time quantum must be a positive integer.";
    return;
  }

  runButton.disabled = true;
  runButton.textContent = "Running…";

  try {
    const response = await fetch("/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ algorithm, input: { time_quantum: quantum, quantum, processes } })
    });

    const output = await response.json();
    if (!response.ok) throw new Error(output.error || "Simulation failed.");

    renderOutput(output, algorithm, processes.length);
  } catch (error) {
    errorMessage.textContent = error.message;
  } finally {
    runButton.disabled = false;
    runButton.textContent = "Run Simulation";
  }
});

function renderOutput(output, algorithm, count) {
  outputSection.hidden = false;
  document.getElementById("algorithmLabel").textContent = `Algorithm: ${algorithm.toUpperCase()}`;
  document.getElementById("avgWaiting").textContent = Number(output.average_waiting).toFixed(2);
  document.getElementById("avgTurnaround").textContent = Number(output.average_turnaround).toFixed(2);
  document.getElementById("processCount").textContent = count;

  renderGantt(output.gantt_chart || []);

  const tbody = document.querySelector("#resultsTable tbody");
  tbody.innerHTML = "";
  (output.results || []).forEach(p => {
    const row = document.createElement("tr");
    [p.pid, p.arrival, p.burst, p.completion, p.turnaround, p.waiting]
      .forEach(value => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      });
    tbody.appendChild(row);
  });
}

function renderGantt(ganttData) {
  const container = document.getElementById("ganttChart");
  container.innerHTML = "";

  // Collapse consecutive identical time slots into readable execution segments.
  let i = 0;
  while (i < ganttData.length) {
    let j = i + 1;
    while (j < ganttData.length && ganttData[j] === ganttData[i]) j++;

    const segment = document.createElement("div");
    segment.className = `gantt-segment${ganttData[i] === "idle" ? " idle" : ""}`;
    segment.textContent = `${ganttData[i]} (${i}–${j})`;
    container.appendChild(segment);
    i = j;
  }
}
