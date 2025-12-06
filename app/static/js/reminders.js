// static/js/reminders.js

document.addEventListener("DOMContentLoaded", () => {
  let calendar = null;
  let editingId = null;

  // --------------------------
  // DOM elements
  // --------------------------
  const addForm = document.getElementById("df-add-rem-form");
  const titleInput =
    addForm && addForm.querySelector('input[name="title"]');
  const descInput =
    addForm && addForm.querySelector('textarea[name="description"]');
  const dateInput =
    addForm && addForm.querySelector('input[name="date"]');
  const hiddenIdInput = document.getElementById("df-reminder-id");
  const submitBtn = document.getElementById("df-cal-submit-btn");
  const cancelEditBtn = document.getElementById("df-cal-cancel-edit");
  const formHelp = document.getElementById("df-cal-form-help");

  // day list panel
  const dayListTitle = document.getElementById("df-daylist-title");
  const dayListDate = document.getElementById("df-daylist-date");
  const dayListItems = document.getElementById("df-daylist-items");

  // Helper: format Date -> "YYYY-MM-DDTHH:MM" for datetime-local
  function formatForDateTimeLocal(date) {
    const d = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return d.toISOString().slice(0, 16);
  }

  function setEditMode(on) {
    if (!submitBtn || !cancelEditBtn || !formHelp) return;

    if (on) {
      submitBtn.textContent = "Update reminder";
      cancelEditBtn.classList.remove("d-none");
      formHelp.textContent =
        "Editing an existing reminder. Make changes and click “Update reminder”, or Cancel.";
    } else {
      submitBtn.textContent = "Save reminder";
      cancelEditBtn.classList.add("d-none");
      formHelp.textContent =
        "Create a new reminder. Click an event or “Edit” to modify an existing one.";
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
    if (titleInput) titleInput.value = title || "";
    if (descInput) descInput.value = desc || "";
    if (dateInput && dateObj) {
      dateInput.value = formatForDateTimeLocal(new Date(dateObj));
    }
    setEditMode(true);
    if (titleInput) titleInput.focus();
  }

  // --------------------------
  // Day list panel (right card)
  // --------------------------
  function clearDayList(message) {
    if (!dayListItems) return;
    dayListItems.innerHTML = "";
    const li = document.createElement("li");
    li.classList.add("df-cal-daylist-empty");
    li.textContent =
      message || "Click a date or event to see reminders for that day.";
    dayListItems.appendChild(li);
    if (dayListDate) dayListDate.textContent = "None selected";
  }

  function updateDayListForDate(date) {
    if (!calendar || !dayListItems) return;

    const target = new Date(date);
    const y = target.getFullYear();
    const m = target.getMonth();
    const d = target.getDate();

    const events = calendar.getEvents();
    const matches = events.filter((ev) => {
      if (!ev.start) return false;
      const s = ev.start;
      return (
        s.getFullYear() === y &&
        s.getMonth() === m &&
        s.getDate() === d
      );
    });

    dayListItems.innerHTML = "";

    if (matches.length === 0) {
      clearDayList("No reminders on this day yet.");
      if (dayListDate) {
        dayListDate.textContent = target.toLocaleDateString("en-IN", {
          day: "2-digit",
          month: "short",
          year: "numeric"
        });
      }
      return;
    }

    matches
      .sort((a, b) => (a.start || 0) - (b.start || 0))
      .forEach((ev) => {
        const li = document.createElement("li");
        li.classList.add("df-cal-daylist-item");

        const timeStr = ev.start
          ? ev.start.toLocaleTimeString("en-IN", {
              hour: "2-digit",
              minute: "2-digit"
            })
          : "";

        const desc = ev.extendedProps.description || "";

        li.innerHTML = `
          <div class="df-cal-daylist-item-top">
            <span class="df-cal-daylist-time">${timeStr}</span>
            <span class="df-cal-daylist-title">${ev.title || ""}</span>
          </div>
          ${
            desc
              ? `<div class="df-cal-daylist-desc">${desc}</div>`
              : ""
          }
        `;

        dayListItems.appendChild(li);
      });

    if (dayListDate) {
      dayListDate.textContent = target.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      });
    }
  }

  // --------------------------
  // Calendar
  // --------------------------
  const calendarEl = document.getElementById("df-calendar");

  if (calendarEl && window.FullCalendar && FullCalendar.Calendar) {
    const eventsUrl =
      calendarEl.dataset.eventsUrl || "/dashboard/calendar/events";

    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      height: 580,
      themeSystem: "standard",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: ""
      },
      events: eventsUrl,

      // Click a day -> prefill date + show day list
      dateClick: function (info) {
        if (dateInput) {
          const base = new Date(info.date);
          base.setHours(18, 0, 0, 0); // default 6pm
          dateInput.value = formatForDateTimeLocal(base);
          dateInput.focus();
        }
        updateDayListForDate(info.date);
      },

      // Click an event -> edit it in the form + show day list
      eventClick: function (info) {
        const id = info.event.id;
        const title = info.event.title || "";
        const desc = info.event.extendedProps.description || "";
        const start = info.event.start;
        startEditing(id, title, desc, start);
        if (start) {
          updateDayListForDate(start);
        }
      }
    });

    calendar.render();

    // initial state of day list
    clearDayList();
  } else {
    console.warn(
      "FullCalendar not loaded or #df-calendar missing – calendar will not render."
    );
  }

  // --------------------------
  // Add / Update reminder (AJAX)
  // --------------------------
  if (addForm) {
    const addUrl =
      addForm.dataset.addUrl || "/dashboard/calendar/add";
    const editBaseUrl = "/dashboard/calendar/edit";

    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!titleInput || !dateInput) return;

      const formData = new FormData(addForm);

      let url;
      if (editingId) {
        // Update existing
        url = `${editBaseUrl}/${editingId}`;
      } else {
        // Create new
        url = addUrl;
      }

      try {
        const res = await fetch(url, {
          method: "POST",
          body: formData
        });
        const data = await res.json();

        if (data.status === "success") {
          if (calendar) calendar.refetchEvents();
//          window.location.reload();
        } else {
          alert(data.message || "Could not save reminder.");
        }
      } catch (err) {
        console.error(err);
        alert("Error saving reminder.");
      }
    });
  }

  // Cancel edit button
  if (cancelEditBtn) {
    cancelEditBtn.addEventListener("click", () => {
      clearForm();
    });
  }

  // --------------------------
  // Quick date chips
  // --------------------------
  document.querySelectorAll(".df-quick-date").forEach((btn) => {
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

  // --------------------------
  // Edit from Upcoming list
  // --------------------------
  document.querySelectorAll(".df-edit-rem").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      const title = btn.dataset.title || "";
      const desc = btn.dataset.desc || "";
      const dateStr = btn.dataset.date || "";

      startEditing(id, title, desc, dateStr);
      if (dateStr) {
        updateDayListForDate(new Date(dateStr));
      }
    });
  });

  // --------------------------
  // Delete reminder (no confirm popup)
  // --------------------------
  document.querySelectorAll(".df-del-rem").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const deleteUrl = `/dashboard/calendar/delete/${id}`;

      try {
        const res = await fetch(deleteUrl, {
          method: "POST"
        });
        const data = await res.json();
        if (data.status === "success") {
          if (calendar) calendar.refetchEvents();
//          window.location.reload();
        } else {
          alert(data.message || "Could not delete reminder.");
        }
      } catch (err) {
        console.error(err);
        alert("Error deleting reminder.");
      }
    });
  });
});
