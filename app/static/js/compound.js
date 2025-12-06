// static/js/compound.js

let dfCompChart = null;
let dfCompLastSchedule = [];

/** Format number as Indian Rupee string */
function dfCompFormatINR(value) {
  return (
    "₹ " +
    Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })
  );
}

/**
 * Compute compound interest schedule.
 * Uses simple period iteration so we can support:
 * - arbitrary compounding frequency
 * - regular monthly contribution
 */
function dfCompComputeSchedule(
  principal,
  ratePct,
  years,
  freqPerYear,
  monthlyContrib
) {
  const r = (ratePct || 0) / 100;
  const n = freqPerYear || 1;
  const totalPeriods = Math.round(years * n);

  let balance = principal || 0;
  let invested = principal || 0;

  const labels = [];
  const balances = [];
  const schedule = [];

  // We treat contributions as monthly amounts, approximate by distributing
  // them across periods proportionally to months in a year.
  const periodsPerMonth = n / 12; // e.g. n=12 -> 1 period per month

  let currentYear = 0;
  let yearStartBalance = balance;
  let yearContrib = 0;

  for (let period = 1; period <= totalPeriods; period++) {
    // contribution this period
    let contribThisPeriod = 0;
    if (monthlyContrib > 0 && periodsPerMonth > 0) {
      contribThisPeriod = monthlyContrib / periodsPerMonth;
    }

    balance = balance * (1 + r / n) + contribThisPeriod;
    invested += contribThisPeriod;

    const timeYears = period / n;
    const yearIndex = Math.floor(timeYears);

    // if we crossed into a new year or reached end
    if (yearIndex > currentYear || period === totalPeriods) {
      const interestThisYear = balance - yearStartBalance - yearContrib;

      schedule.push({
        year: yearIndex,
        opening: yearStartBalance,
        interest: interestThisYear,
        closing: balance,
      });

      labels.push("Year " + yearIndex);
      balances.push(balance);

      currentYear = yearIndex;
      yearStartBalance = balance;
      yearContrib = 0;
    } else {
      yearContrib += contribThisPeriod;
    }
  }

  const maturity = balance;
  const interestEarned = maturity - invested;

  return { labels, balances, schedule, maturity, invested, interestEarned };
}

function dfCompRenderChart(labels, balances) {
  const ctx = document.getElementById("df-comp-chart");
  if (!ctx) return;

  if (dfCompChart) {
    dfCompChart.destroy();
  }

  // eslint-disable-next-line no-undef
  dfCompChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Portfolio value",
          data: balances,
          tension: 0.25,
          fill: false,
        },
      ],
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
              const value = context.parsed.y || 0;
              return dfCompFormatINR(value);
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
          ticks: {
            color: "#e5e7eb",
            callback: function (value) {
              return (
                "₹ " +
                Number(value).toLocaleString("en-IN", {
                  maximumFractionDigits: 0,
                })
              );
            },
          },
          grid: { color: "rgba(55,65,81,0.6)" },
        },
      },
    },
  });
}

function dfCompRenderTable(schedule) {
  const tbody = document.getElementById("df-comp-tbody");
  if (!tbody) return;

  tbody.innerHTML = "";

  schedule.forEach((row) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${row.year}</td>
      <td>${dfCompFormatINR(row.opening.toFixed(2))}</td>
      <td>${dfCompFormatINR(row.interest.toFixed(2))}</td>
      <td>${dfCompFormatINR(row.closing.toFixed(2))}</td>
    `;

    tbody.appendChild(tr);
  });
}

/** Export last computed schedule as CSV */
function dfCompExportCSV() {
  if (!dfCompLastSchedule || dfCompLastSchedule.length === 0) {
    alert("No data to export. Please run a calculation first.");
    return;
  }

  // Build CSV header
  let csv = "Year,Opening balance,Interest earned,Closing balance\n";

  dfCompLastSchedule.forEach((row) => {
    const year = row.year;
    const opening = Number(row.opening || 0).toFixed(2);
    const interest = Number(row.interest || 0).toFixed(2);
    const closing = Number(row.closing || 0).toFixed(2);

    csv += `${year},${opening},${interest},${closing}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  const now = new Date();
  const ts = now.toISOString().replace(/[:T]/g, "-").split(".")[0]; // YYYY-MM-DD-HH-MM-SS

  link.href = url;
  link.download = `compound_schedule_${ts}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function dfCompCalculateAndRender() {
  const principalInput = document.getElementById("df-comp-principal");
  const rateInput = document.getElementById("df-comp-rate");
  const yearsInput = document.getElementById("df-comp-years");
  const freqInput = document.getElementById("df-comp-frequency");
  const contribInput = document.getElementById("df-comp-contrib");

  if (
    !principalInput ||
    !rateInput ||
    !yearsInput ||
    !freqInput ||
    !contribInput
  ) {
    return;
  }

  const principal = parseFloat(principalInput.value || "0");
  const rate = parseFloat(rateInput.value || "0");
  const years = parseFloat(yearsInput.value || "0");
  const freq = parseInt(freqInput.value || "1", 10);
  const contrib = parseFloat(contribInput.value || "0");

  if (years <= 0 || rate < 0 || principal < 0 || contrib < 0) {
    return;
  }

  const result = dfCompComputeSchedule(principal, rate, years, freq, contrib);

  // Save schedule for export
  dfCompLastSchedule = result.schedule || [];

  // Update summary
  const maturityEl = document.getElementById("df-comp-maturity");
  const investedEl = document.getElementById("df-comp-invested");
  const interestEl = document.getElementById("df-comp-interest");

  if (maturityEl) maturityEl.textContent = dfCompFormatINR(result.maturity);
  if (investedEl) investedEl.textContent = dfCompFormatINR(result.invested);
  if (interestEl) interestEl.textContent = dfCompFormatINR(result.interestEarned);

  // Chart & table
  dfCompRenderChart(result.labels, result.balances);
  dfCompRenderTable(result.schedule);
}

function dfCompResetForm() {
  const form = document.getElementById("df-comp-form");
  if (!form) return;

  // Reset to some sensible defaults
  document.getElementById("df-comp-principal").value = "100000";
  document.getElementById("df-comp-rate").value = "10";
  document.getElementById("df-comp-years").value = "10";
  document.getElementById("df-comp-frequency").value = "12";
  document.getElementById("df-comp-contrib").value = "5000";

  dfCompCalculateAndRender();
}

function dfCompAttachEvents() {
  const calcBtn = document.querySelector(".df-comp-calc-btn");
  const resetBtn = document.querySelector(".df-comp-reset-btn");
  const exportBtn = document.querySelector(".df-comp-export-btn");
  const form = document.getElementById("df-comp-form");

  if (calcBtn) {
    calcBtn.addEventListener("click", dfCompCalculateAndRender);
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", dfCompResetForm);
  }

  if (exportBtn) {
    exportBtn.addEventListener("click", dfCompExportCSV);
  }

  // Small UX: recompute on input changes
  if (form) {
    form.addEventListener("input", (e) => {
      const target = e.target;
      if (target && target.classList.contains("df-comp-input")) {
        dfCompCalculateAndRender();
      }
    });
  }

  // Initial calculation with defaults
  dfCompCalculateAndRender();
}

document.addEventListener("DOMContentLoaded", dfCompAttachEvents);
