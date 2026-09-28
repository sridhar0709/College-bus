(() => {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  window.showSection = function(sectionId, button) {
    $$(".section").forEach(section => section.classList.remove("active"));
    const selected = document.getElementById(sectionId);
    if (selected) selected.classList.add("active");

    $$(".nav-item").forEach(item => item.classList.remove("active"));
    if (button) button.classList.add("active");

    const titles = {
      dashboard: "Admin Dashboard",
      students: "Student Management",
      parents: "Parent Management",
      drivers: "Driver Management",
      buses: "Bus Management",
      locations: "Live GPS Tracking",
      complaints: "Complaint Management",
      attendance: "QR Attendance",
      bus: "My Bus",
      profile: "Driver Profile",
      gps: "Live GPS",
    };
    const pageTitle = $("#pageTitle");
    if (pageTitle) pageTitle.textContent = titles[sectionId] || pageTitle.textContent;

    const sidebar = $("#sidebar");
    const overlay = $("#overlay");
    sidebar?.classList.remove("open");
    overlay?.classList.remove("show");

    if (sectionId === "locations" && window.map) {
      window.setTimeout(() => window.map.invalidateSize(), 250);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  window.activateById = id => {
    const button = document.querySelector('.nav-item[onclick*="' + id + '"]');
    window.showSection(id, button);
  };

  const toggleCard = (id, show) => {
    const card = document.getElementById(id);
    if (!card) return;
    card.style.display = show ? "block" : "none";
    if (show) card.scrollIntoView({behavior:"smooth", block:"start"});
  };
  window.showAddBus = () => toggleCard("addBusCard", true);
  window.hideAddBus = () => toggleCard("addBusCard", false);
  window.showAddStudent = () => toggleCard("addStudentCard", true);
  window.hideAddStudent = () => toggleCard("addStudentCard", false);
  window.showAddParent = () => toggleCard("addParentCard", true);
  window.hideAddParent = () => toggleCard("addParentCard", false);
  window.showAddDriver = () => toggleCard("addDriverCard", true);
  window.hideAddDriver = () => toggleCard("addDriverCard", false);

  window.filterTable = (input, tableId) => {
    const table = document.getElementById(tableId);
    if (!table) return;
    const filter = (input?.value || "").trim().toLowerCase();
    $$("tbody tr", table).forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(filter) ? "" : "none";
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    const menuBtn = $("#menuBtn"), sidebar = $("#sidebar"), overlay = $("#overlay");
    menuBtn?.addEventListener("click", () => {
      sidebar?.classList.toggle("open");
      overlay?.classList.toggle("show");
    });
    overlay?.addEventListener("click", () => {
      sidebar?.classList.remove("open");
      overlay?.classList.remove("show");
    });

    window.setTimeout(() => {
      $$(".flash").forEach(message => {
        message.style.transition = "opacity .4s ease, transform .4s ease";
        message.style.opacity = "0";
        message.style.transform = "translateY(-6px)";
        window.setTimeout(() => message.remove(), 450);
      });
    }, 4500);

    initMap();
    window.setInterval(updateBusLocation, 8000);
  });

  window.map = null;
  let busMarker = null;

  function initMap() {
    const mapElement = $("#map");
    if (!mapElement || typeof L === "undefined" || window.map) return;

    window.map = L.map("map", { zoomControl: true }).setView([11.0168, 76.9558], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(window.map);

    busMarker = L.marker([11.0168, 76.9558]).addTo(window.map).bindPopup("🚌 College Bus");
    updateBusLocation();
  }

  function updateBusLocation() {
    if (!window.map || !busMarker) return;

    fetch("/api/admin_bus_location", {headers: {"Accept":"application/json"}})
      .then(response => response.json().catch(() => ({})))
      .then(data => {
        const status = $("#location-status");
        if (data.success) {
          const latitude = Number(data.latitude);
          const longitude = Number(data.longitude);
          if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
            if (status) status.textContent = "🟡 GPS returned invalid coordinates.";
            return;
          }
          busMarker.setLatLng([latitude, longitude]);
          window.map.setView([latitude, longitude], 15);
          busMarker.setPopupContent("🚌 Bus: " + (data.bus_number || "Unknown Bus") + "<br>📍 Live GPS Location");
          if (status) status.textContent = "🟢 Live GPS location updated";
        } else if (status) {
          status.textContent = "🟡 " + (data.message || "GPS location not available");
        }
      })
      .catch(() => {
        const status = $("#location-status");
        if (status) status.textContent = "🔴 Unable to reach GPS service";
      });
  }

  window.updateBusLocation = updateBusLocation;
})();
