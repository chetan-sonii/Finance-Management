// static/js/expenses.js

let dfExpensesChart = null;

function dfExpGetRows() {
  return Array.from(document.querySelectorAll(".df-exp-row"));
}

function dfExpGetSelectedChartType() {
  const activeBtn = document.querySelector(
    ".df-exp-chart-toggle .btn.active"
  );
  return activeBtn ? activeBtn.getAttribute("data-chart-type") : "pie";
}

function dfExpCalculate() {
  const rows = dfExpGetRows();

  const labels = [];
  const data = [];

  let total = 0;

  rows.forEach((row) => {
    const typeInput = row.querySelector(".df-exp-type");
    const amountInput = row.querySelector(".df-exp-amount");

    if (!typeInput || !amountInput) return;

    const label = (typeInput.value || "").trim();
    const amount = parseFloat(amountInput.value || "0");

    if (!label || isNaN(amount) || amount <= 0) return;

    labels.push(label);
    data.push(amount);
    total += amount;
  });

  // ---- Update summary ----
  const totalEl = document.getElementById("df-exp-total");
  const catsEl = document.getElementById("df-exp-categories");

  if (totalEl) {
    totalEl.textContent =
      "₹ " +
      total.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      });
  }

  if (catsEl) {
    catsEl.textContent = String(data.length);
  }

  // ---- Render chart ----
  dfExpRenderChart(labels, data);
}

function dfExpRenderChart(labels, data) {
  const ctx = document.getElementById("expensesChartMain");
  if (!ctx) return;

  const chartType = dfExpGetSelectedChartType();

  // Base dataset
  const dataset = {
    data,
    // Let Chart.js handle colors. No custom colors set per instructions.
  };

  // Prepare config depending on chart type
  let config;

  if (chartType === "bar") {
    config = {
      type: "bar",
      data: {
        labels,
        datasets: [dataset],
      },
      options: {
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (context) {
                const value = context.parsed.y || 0;
                return (
                  "₹ " +
                  value.toLocaleString("en-IN", {
                    maximumFractionDigits: 2,
                  })
                );
              },
            },
          },
        },
        scales: {
          x: {
            ticks: { color: "#e5e7eb" },
            grid: { color: "rgba(55,65,81,0.6)" },
          },
          y: {
            ticks: { color: "#e5e7eb" },
            grid: { color: "rgba(55,65,81,0.6)" },
          },
        },
      },
    };
  } else {
    // pie or doughnut
    config = {
      type: chartType,
      data: {
        labels,
        datasets: [dataset],
      },
      options: {
        plugins: {
          legend: {
            labels: {
              color: "#e5e7eb",
              font: { size: 11 },
            },
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.parsed || 0;
                return (
                  label +
                  ": ₹ " +
                  value.toLocaleString("en-IN", {
                    maximumFractionDigits: 2,
                  })
                );
              },
            },
          },
        },
      },
    };
  }

  // Destroy previous chart
  if (dfExpensesChart) {
    dfExpensesChart.destroy();
  }

  // eslint-disable-next-line no-undef
  dfExpensesChart = new Chart(ctx, config);
}

function dfExpAddRow() {
  const tbody = document.getElementById("df-exp-rows");
  if (!tbody) return;

  const tr = document.createElement("tr");
  tr.className = "df-exp-row";
  tr.innerHTML = `
    <td>
      <input type="text"
             class="form-control df-exp-type"
             name="types[]"
             placeholder="Category (e.g. Subscriptions)" />
    </td>
    <td>
      <input type="number"
             min="0"
             step="0.01"
             class="form-control df-exp-amount"
             name="amounts[]"
             value="" />
    </td>
    <td class="text-end">
      <button type="button"
              class="btn btn-sm btn-outline-secondary df-exp-remove-row">
        ✕
      </button>
    </td>
  `;
  tbody.appendChild(tr);

  const typeInput = tr.querySelector(".df-exp-type");
  if (typeInput) typeInput.focus();
}

function dfExpAttachEvents() {
  const addBtn = document.querySelector(".df-exp-add-row");
  const calcBtn = document.querySelector(".df-exp-calc");
  const tbody = document.getElementById("df-exp-rows");
  const chartToggle = document.querySelector(".df-exp-chart-toggle");

  if (addBtn) addBtn.addEventListener("click", dfExpAddRow);
  if (calcBtn) calcBtn.addEventListener("click", dfExpCalculate);

  if (tbody) {
    // Delete row
    tbody.addEventListener("click", (e) => {
      const target = e.target;
      if (target && target.classList.contains("df-exp-remove-row")) {
        const row = target.closest(".df-exp-row");
        if (row) {
          row.remove();
          dfExpCalculate();
        }
      }
    });

    // Recalculate when amounts change
    tbody.addEventListener("input", (e) => {
      if (e.target && e.target.classList.contains("df-exp-amount")) {
        dfExpCalculate();
      }
    });

    // Press Enter in last amount field to add a new row
    tbody.addEventListener("keydown", (e) => {
      if (
        e.key === "Enter" &&
        e.target &&
        e.target.classList.contains("df-exp-amount")
      ) {
        e.preventDefault();

        const rows = dfExpGetRows();
        const lastRow = rows[rows.length - 1];
        if (lastRow && lastRow.contains(e.target)) {
          dfExpAddRow();
        } else {
          dfExpCalculate();
        }
      }
    });
  }

  // Chart type toggle buttons
  if (chartToggle) {
    chartToggle.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-chart-type]");
      if (!btn) return;

      chartToggle
        .querySelectorAll("button")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      // Re-render chart with new type
      dfExpCalculate();
    });
  }

  // Initial calculation with default rows
  dfExpCalculate();
}

document.addEventListener("DOMContentLoaded", dfExpAttachEvents);
