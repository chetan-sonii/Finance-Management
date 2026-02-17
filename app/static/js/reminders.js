// static/js/reminders.js
// Handles all reminder interactions: add, edit, delete — all without page reload.

document.addEventListener("DOMContentLoaded", () => {
  let calendar = null;
  let editingId = null;

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const addForm       = document.getElementById("df-add-rem-form");
  const titleInput    = addForm && addForm.querySelector('input[name="title"]');
  const descInput     = addForm && addForm.querySelector('textarea[name="description"]');
  const dateInput     = addForm && addForm.querySelector('input[name="date"]');
  const hiddenIdInput = document.getElementById("df-reminder-id");
  const submitBtn     = document.getElementById("df-cal-submit-btn");
  const cancelEditBtn = document.getElementById("df-cal-cancel-edit");
  const formHelp      = document.getElementById("df-cal-form-help");
  const dayListDate   = document.getElementById("df-daylist-date");
  const dayListItems  = document.getElementById("df-daylist-items");

  // ── Helpers ───────────────────────────────────────────────────────────────
  function esc(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatForDateTimeLocal(d) {
    const dt = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
    return dt.toISOString().slice(0, 16);
  }

  // ── Form mode: add vs edit ────────────────────────────────────────────────
  function setEditMode(on) {
    if (!submitBtn || !cancelEditBtn || !formHelp) return;
    if (on) {
      submitBtn.textContent = "Update reminder";
      cancelEditBtn.classList.remove("d-none");
      formHelp.textContent  = "Editing an existing reminder. Make changes and click Update, or Cancel.";
    } else {
      submitBtn.textContent = "Save reminder";
      cancelEditBtn.classList.add("d-none");
      formHelp.textContent  = "Create a new reminder. Click an event or Edit to modify an existing one.";
    }
  }

  function clearForm() {
    if (!addForm) return;
    addForm.reset();
    editingId = null;
    if (hiddenIdInput) hiddenIdInput.value = "";
    setEditMode(false);
  }

  function startEditing(id, title, desc, dateObj) {
    editingId = id;
    if (hiddenIdInput) hiddenIdInput.value = id;
    if (titleInput)    titleInput.value  = title || "";
    if (descInput)     descInput.value   = desc  || "";
    if (dateInput && dateObj) {
      dateInput.value = formatForDateTimeLocal(new Date(dateObj));
    }
    setEditMode(true);
    if (titleInput) titleInput.focus();
    // Scroll form into view on mobile
    if (addForm) addForm.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // ── Day-list panel ────────────────────────────────────────────────────────
  function clearDayList(msg) {
    if (!dayListItems) return;
    dayListItems.innerHTML = "";
    const li = document.createElement("li");
    li.classList.add("df-cal-daylist-empty");
    li.textContent = msg || "Click a date or event to see reminders for that day.";
    dayListItems.appendChild(li);
    if (dayListDate) dayListDate.textContent = "None selected";
  }

  function updateDayListForDate(inputDate) {
    if (!calendar || !dayListItems) return;
    const target = new Date(inputDate);
    const y = target.getFullYear(), m = target.getMonth(), d = target.getDate();

    const matches = calendar.getEvents().filter(ev => {
      if (!ev.start) return false;
      const s = ev.start;
      return s.getFullYear() === y && s.getMonth() === m && s.getDate() === d;
    });

    dayListItems.innerHTML = "";

    if (matches.length === 0) {
      clearDayList("No reminders on this day yet.");
      if (dayListDate) {
        dayListDate.textContent = target.toLocaleDateString("en-IN", {
          day: "2-digit", month: "short", year: "numeric"
        });
      }
      return;
    }

    matches.sort((a, b) => (a.start || 0) - (b.start || 0)).forEach(ev => {
      const li       = document.createElement("li");
      li.classList.add("df-cal-daylist-item");
      const timeStr  = ev.start ? ev.start.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "";
      const desc     = ev.extendedProps.description || "";
      li.innerHTML   = `
        <div class="df-cal-daylist-item-top">
          <span class="df-cal-daylist-time">${esc(timeStr)}</span>
          <span class="df-cal-daylist-title">${esc(ev.title)}</span>
        </div>
        ${desc ? `<div class="df-cal-daylist-desc">${esc(desc)}</div>` : ""}
      `;
      dayListItems.appendChild(li);
    });

    if (dayListDate) {
      dayListDate.textContent = target.toLocaleDateString("en-IN", {
        day: "2-digit", month: "short", year: "numeric"
      });
    }
  }

  // ── Upcoming list helpers ─────────────────────────────────────────────────
  function getUpcomingList() {
    return document.querySelector(".df-rem-list");
  }

  function updateCountBadge(delta) {
    const badge = document.querySelector(".df-cal-side-count");
    if (!badge) return;
    const current = parseInt(badge.textContent) || 0;
    badge.textContent = `${Math.max(0, current + delta)} active`;
  }

  // Build a <li> for the upcoming list from a JSON reminder object
  function buildReminderLi(r) {
    const li = document.createElement("li");
    li.dataset.reminderId = r.id;

    li.innerHTML = `
      <div class="df-rem-row-top">
        <div>
          <div class="df-rem-title">${esc(r.title)}</div>
          <div class="df-rem-date">${esc(r.reminder_date_display)}</div>
        </div>
        <span class="df-rem-badge">${esc(r.reminder_date_badge)}</span>
      </div>
      ${r.description ? `<div class="df-rem-note">${esc(r.description)}</div>` : ""}
      <div class="df-rem-actions">
        <button type="button" class="btn btn-sm btn-outline-info df-edit-rem"
          data-id="${esc(r.id)}"
          data-title="${esc(r.title)}"
          data-desc="${esc(r.description)}"
          data-date="${esc(r.reminder_date_iso)}"
        >Edit</button>
        <button type="button" class="btn btn-sm btn-outline-danger df-del-rem"
          data-id="${esc(r.id)}"
        >Delete</button>
      </div>
    `;

    li.querySelector(".df-edit-rem").addEventListener("click", () => {
      startEditing(r.id, r.title, r.description, r.reminder_date_iso);
      updateDayListForDate(new Date(r.reminder_date_iso));
    });

    li.querySelector(".df-del-rem").addEventListener("click", () => {
      deleteReminder(r.id, li);
    });

    return li;
  }

  // Get or create the <ul.df-rem-list> inside .df-cal-upcoming
  function ensureReminderList() {
    let list = getUpcomingList();
    if (list) return list;

    const upcoming = document.querySelector(".df-cal-upcoming");
    if (!upcoming) return null;

    const emptyP = upcoming.querySelector(".df-empty");
    if (emptyP) emptyP.remove();

    list = document.createElement("ul");
    list.className = "df-rem-list";
    upcoming.appendChild(list);
    return list;
  }

  // Replace an existing <li> after an edit
  function replaceReminderLi(id, r) {
    const existing = document.querySelector(`li[data-reminder-id="${id}"]`);
    if (!existing) return;
    existing.replaceWith(buildReminderLi(r));
  }

  // ── Delete ────────────────────────────────────────────────────────────────
  async function deleteReminder(id, liEl) {
    try {
      const res  = await fetch(`/dashboard/calendar/delete/${id}`, { method: "POST" });
      const data = await res.json();
      if (data.status === "success") {
        if (liEl) liEl.remove();
        updateCountBadge(-1);

        const list = getUpcomingList();
        if (list && list.querySelectorAll("li").length === 0) {
          const emptyP = document.createElement("p");
          emptyP.className = "df-empty mb-0";
          emptyP.textContent = "No reminders added yet. Start by creating your first payment reminder.";
          list.replaceWith(emptyP);
        }

        if (calendar) calendar.refetchEvents();
      } else {
        alert(data.message || "Could not delete reminder.");
      }
    } catch (err) {
      console.error(err);
      alert("Error deleting reminder.");
    }
  }

  // Wire up server-rendered delete buttons
  document.querySelectorAll(".df-del-rem").forEach(btn => {
    btn.addEventListener("click", () => deleteReminder(btn.dataset.id, btn.closest("li")));
  });

  // Wire up server-rendered edit buttons
  document.querySelectorAll(".df-edit-rem").forEach(btn => {
    btn.addEventListener("click", () => {
      startEditing(btn.dataset.id, btn.dataset.title, btn.dataset.desc, btn.dataset.date);
      if (btn.dataset.date) updateDayListForDate(new Date(btn.dataset.date));
    });
  });

  // ── FullCalendar ──────────────────────────────────────────────────────────
  const calendarEl = document.getElementById("df-calendar");

  if (calendarEl && window.FullCalendar && FullCalendar.Calendar) {
    const eventsUrl = calendarEl.dataset.eventsUrl || "/dashboard/calendar/events";

    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView:  "dayGridMonth",
      height:       580,
      themeSystem:  "standard",
      headerToolbar: {
        left:   "prev,next today",
        center: "title",
        right:  ""
      },
      events: eventsUrl,

      dateClick: function(info) {
        if (dateInput) {
          const base = new Date(info.date);
          base.setHours(18, 0, 0, 0);
          dateInput.value = formatForDateTimeLocal(base);
          dateInput.focus();
        }
        updateDayListForDate(info.date);
      },

      eventClick: function(info) {
        startEditing(
          info.event.id,
          info.event.title,
          info.event.extendedProps.description || "",
          info.event.start
        );
        if (info.event.start) updateDayListForDate(info.event.start);
      }
    });

    calendar.render();
    clearDayList();

  } else if (calendarEl) {
    // FullCalendar not loaded yet — wait and retry once
    window.addEventListener("load", () => {
      if (window.FullCalendar && FullCalendar.Calendar) {
        location.reload();
      } else {
        calendarEl.innerHTML = '<p style="color:#9ca3af;padding:2rem;text-align:center;">Calendar failed to load. Please refresh the page.</p>';
      }
    });
  }

  // ── Add / Update form submit ──────────────────────────────────────────────
  if (addForm) {
    const addUrl   = addForm.dataset.addUrl || "/dashboard/calendar/add";
    const editBase = "/dashboard/calendar/edit";

    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!titleInput || !dateInput) return;

      const url      = editingId ? `${editBase}/${editingId}` : addUrl;
      const formData = new FormData(addForm);

      // Disable button to prevent double-submit
      if (submitBtn) submitBtn.disabled = true;

      try {
        const res  = await fetch(url, { method: "POST", body: formData });
        const data = await res.json();

        if (data.status !== "success") {
          alert(data.message || "Could not save reminder.");
          return;
        }

        if (calendar) calendar.refetchEvents();

        if (editingId) {
          if (data.reminder) replaceReminderLi(editingId, data.reminder);
        } else {
          if (data.reminder) {
            const list = ensureReminderList();
            if (list) list.appendChild(buildReminderLi(data.reminder));
            updateCountBadge(+1);
          }
        }

        clearForm();

      } catch (err) {
        console.error(err);
        alert("Error saving reminder. Check your connection and try again.");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // Cancel edit
  if (cancelEditBtn) {
    cancelEditBtn.addEventListener("click", clearForm);
  }

  // ── Quick date chips ──────────────────────────────────────────────────────
  document.querySelectorAll(".df-quick-date").forEach(btn => {
    btn.addEventListener("click", () => {
      if (!dateInput) return;
      const days = parseInt(btn.dataset.days || "0", 10);
      const base = new Date();
      base.setDate(base.getDate() + days);
      base.setHours(18, 0, 0, 0);
      dateInput.value = formatForDateTimeLocal(base);
      dateInput.focus();
      updateDayListForDate(base);
    });
  });
});
