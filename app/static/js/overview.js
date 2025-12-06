// static/js/overview.js

let dfOvTrendChart = null;
let dfOvCategoryChart = null;

function dfOvFormatINR(value) {
  return (
    "₹ " +
    Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })
  );
}

function dfOvSetupTrendChart(labels, data) {
  const ctx = document.getElementById("df-ov-expense-trend");
  if (!ctx) return;

  if (dfOvTrendChart) {
    dfOvTrendChart.destroy();
  }

  // eslint-disable-next-line no-undef
  dfOvTrendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Total expenses",
          data,
          tension: 0.3,
          fill: true,
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
            label: (ctx) => dfOvFormatINR(ctx.parsed.y || 0),
          },
        },
      },
      scales: {
        x: {
          ticks: { color: "#9ca3af" },
          grid: { color: "rgba(55,65,81,0.4)" },
        },
        y: {
          ticks: {
            color: "#9ca3af",
            callback: (val) =>
              "₹ " +
              Number(val).toLocaleString("en-IN", {
                maximumFractionDigits: 0,
              }),
          },
          grid: { color: "rgba(55,65,81,0.4)" },
        },
      },
    },
  });
}

function dfOvSetupCategoryChart(labels, data) {
  const ctx = document.getElementById("df-ov-category-chart");
  if (!ctx) return;

  if (dfOvCategoryChart) {
    dfOvCategoryChart.destroy();
  }

  // eslint-disable-next-line no-undef
  dfOvCategoryChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data,
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#e5e7eb",
            font: { size: 11 },
            boxWidth: 10,
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) =>
              `${ctx.label}: ${dfOvFormatINR(ctx.parsed || 0)}`,
          },
        },
      },
      cutout: "60%",
    },
  });
}

async function dfOvFetchJSON(url) {
  const res = await fetch(url, { credentials: "same-origin" });
  if (!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}

async function dfOvLoadOverview() {
  // Only run on overview page
  const wrapper = document.querySelector(".df-ov-wrapper");
  if (!wrapper) return;

  try {
    // 1) Summary
    const summary = await dfOvFetchJSON("/dashboard/overview/summary");

    const monthEl = document.getElementById("df-ov-total-month");
    const dailyEl = document.getElementById("df-ov-daily-avg");
    const changeEl = document.getElementById("df-ov-month-change");
    const remCountEl = document.getElementById("df-ov-reminders-count");
    const nextRemEl = document.getElementById("df-ov-next-reminder");
    const topCatEl = document.getElementById("df-ov-top-category");
    const topCatAmtEl = document.getElementById(
      "df-ov-top-category-amount"
    );

    if (monthEl) monthEl.textContent = dfOvFormatINR(summary.total_month);
    if (dailyEl) dailyEl.textContent = dfOvFormatINR(summary.daily_average);

    if (changeEl) {
      if (summary.prev_month_total > 0) {
        const sign = summary.month_change >= 0 ? "+" : "";
        changeEl.textContent = `${sign}${summary.month_change.toFixed(
          1
        )}% vs last month`;
        changeEl.classList.toggle(
          "df-ov-stat-meta--positive",
          summary.month_change > 0
        );
        changeEl.classList.toggle(
          "df-ov-stat-meta--negative",
          summary.month_change < 0
        );
      } else {
        changeEl.textContent = "No data for previous month.";
      }
    }

    if (remCountEl) remCountEl.textContent = summary.upcoming_count || 0;
    if (nextRemEl) {
      if (summary.next_reminder) {
        nextRemEl.textContent = `${summary.next_reminder.title} – ${summary.next_reminder.when}`;
      } else {
        nextRemEl.textContent = "No upcoming reminders.";
      }
    }

    if (topCatEl) topCatEl.textContent = summary.top_category || "—";
    if (topCatAmtEl) {
      if (summary.top_category_amount > 0) {
        topCatAmtEl.textContent =
          dfOvFormatINR(summary.top_category_amount) +
          " this month";
      } else {
        topCatAmtEl.textContent = "No category data yet.";
      }
    }

    // 2) Trend chart
    const trend = await dfOvFetchJSON("/dashboard/overview/expense_trend");
    dfOvSetupTrendChart(trend.labels, trend.values);

    // 3) Category chart
    const cat = await dfOvFetchJSON(
      "/dashboard/overview/category_breakdown"
    );
    dfOvSetupCategoryChart(cat.labels, cat.values);

    // 4) Upcoming reminders list
    const remData = await dfOvFetchJSON(
      "/dashboard/overview/reminders_list"
    );
    const remList = document.getElementById("df-ov-rem-list");
    if (remList) {
      remList.innerHTML = "";
      if (!remData.items || remData.items.length === 0) {
        const li = document.createElement("li");
        li.classList.add("df-ov-rem-empty");
        li.textContent =
          "No upcoming reminders in the next 30 days.";
        remList.appendChild(li);
      } else {
        remData.items.forEach((item) => {
          const li = document.createElement("li");
          li.classList.add("df-ov-rem-item");
          li.innerHTML = `
            <div class="df-ov-rem-top">
              <span class="df-ov-rem-title">${item.title}</span>
              <span class="df-ov-rem-date">${item.when}</span>
            </div>
            ${
              item.description
                ? `<div class="df-ov-rem-desc">${item.description}</div>`
                : ""
            }
          `;
          remList.appendChild(li);
        });
      }
    }

    // 5) Recent expenses table
    const expData = await dfOvFetchJSON(
      "/dashboard/overview/recent_expenses"
    );
    const tbody = document.getElementById("df-ov-expense-rows");
    if (tbody) {
      tbody.innerHTML = "";
      if (!expData.items || expData.items.length === 0) {
        const tr = document.createElement("tr");
        tr.classList.add("df-ov-table-empty");
        tr.innerHTML =
          '<td colspan="4">No recent expenses found.</td>';
        tbody.appendChild(tr);
      } else {
        expData.items.forEach((row) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${row.date}</td>
            <td>${row.category || "—"}</td>
            <td>${row.title || ""}</td>
            <td class="text-end">${dfOvFormatINR(row.amount)}</td>
          `;
          tbody.appendChild(tr);
        });
      }
    }
  } catch (err) {
    console.error("Error loading overview data:", err);
  }
}

document.addEventListener("DOMContentLoaded", dfOvLoadOverview);
