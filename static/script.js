/* ========================================================
   SECTION NAVIGATION
======================================================== */

function showSection(sectionId, button) {

    const sections =
        document.querySelectorAll(".section");

    sections.forEach(function(section) {
        section.classList.remove("active");
    });

    const selected =
        document.getElementById(sectionId);

    if (selected) {
        selected.classList.add("active");
    }

    const navItems =
        document.querySelectorAll(".nav-item");

    navItems.forEach(function(item) {
        item.classList.remove("active");
    });

    if (button) {
        button.classList.add("active");
    }

    const titles = {

        dashboard: "Admin Dashboard",

        students: "Student Management",

        parents: "Parent Management",

        drivers: "Driver Management",

        buses: "Bus Management",

        locations: "Live GPS Tracking",

        complaints: "Complaint Management",

        attendance: "QR Attendance"

    };

    const pageTitle =
        document.getElementById("pageTitle");

    if (pageTitle) {

        pageTitle.textContent =
            titles[sectionId] || "Admin Dashboard";

    }


    /* ====================================================
       CLOSE MOBILE SIDEBAR
    ==================================================== */

    const sidebar =
        document.getElementById("sidebar");

    const overlay =
        document.getElementById("overlay");

    if (sidebar) {
        sidebar.classList.remove("open");
    }

    if (overlay) {
        overlay.classList.remove("show");
    }


    /* ====================================================
       FIX LEAFLET MAP WHEN GPS SECTION OPENS
    ==================================================== */

    if (sectionId === "locations") {

        setTimeout(function() {

            if (map) {
                map.invalidateSize();
            }

        }, 300);

    }


    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}


/* ========================================================
   QUICK BUTTON
======================================================== */

function activateById(sectionId) {

    const button =
        document.querySelector(
            `.nav-item[onclick*="'${sectionId}'"]`
        );

    showSection(sectionId, button);

}


/* ========================================================
   ADD BUS
======================================================== */

function showAddBus() {

    const card =
        document.getElementById("addBusCard");

    if (card) {

        card.style.display = "block";

        card.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }

}


function hideAddBus() {

    const card =
        document.getElementById("addBusCard");

    if (card) {

        card.style.display = "none";

    }

}


/* ========================================================
   TABLE SEARCH
======================================================== */

function filterTable(input, tableId) {

    const filter =
        input.value.toLowerCase();

    const table =
        document.getElementById(tableId);

    if (!table) {

        return;

    }

    const rows =
        table.querySelectorAll("tbody tr");

    rows.forEach(function(row) {

        const text =
            row.textContent.toLowerCase();

        if (text.includes(filter)) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

}


/* ========================================================
   MOBILE SIDEBAR
======================================================== */

const menuBtn =
    document.getElementById("menuBtn");

const sidebar =
    document.getElementById("sidebar");

const overlay =
    document.getElementById("overlay");


if (menuBtn) {

    menuBtn.addEventListener(
        "click",
        function() {

            if (sidebar) {

                sidebar.classList.toggle("open");

            }

            if (overlay) {

                overlay.classList.toggle("show");

            }

        }
    );

}


if (overlay) {

    overlay.addEventListener(
        "click",
        function() {

            if (sidebar) {

                sidebar.classList.remove("open");

            }

            overlay.classList.remove("show");

        }
    );

}


/* ========================================================
   AUTO HIDE FLASH MESSAGE
======================================================== */

setTimeout(function() {

    const messages =
        document.querySelectorAll(".flash");

    messages.forEach(function(message) {

        message.style.transition = "0.5s";

        message.style.opacity = "0";

        setTimeout(function() {

            message.remove();

        }, 500);

    });

}, 4000);


/* ========================================================
   ADD STUDENT
======================================================== */

function showAddStudent() {

    const card =
        document.getElementById("addStudentCard");

    if (card) {

        card.style.display = "block";

        card.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }

}


function hideAddStudent() {

    const card =
        document.getElementById("addStudentCard");

    if (card) {

        card.style.display = "none";

    }

}


/* ========================================================
   ADD PARENT
======================================================== */

function showAddParent() {

    const card =
        document.getElementById("addParentCard");

    if (card) {

        card.style.display = "block";

        card.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }

}


function hideAddParent() {

    const card =
        document.getElementById("addParentCard");

    if (card) {

        card.style.display = "none";

    }

}


/* ========================================================
   ADD DRIVER
======================================================== */

function showAddDriver() {

    const card =
        document.getElementById("addDriverCard");

    if (card) {

        card.style.display = "block";

        card.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }

}


function hideAddDriver() {

    const card =
        document.getElementById("addDriverCard");

    if (card) {

        card.style.display = "none";

    }

}


/* ========================================================
   ADMIN LIVE GPS MAP
======================================================== */

let map = null;

let busMarker = null;


/* ========================================================
   INITIALIZE MAP
======================================================== */

function initMap() {

    const mapElement =
        document.getElementById("map");


    /* If page doesn't have map */

    if (!mapElement) {

        return;

    }


    /* Prevent map initialization twice */

    if (map !== null) {

        return;

    }


    /* Default location */

    let latitude = 11.0168;

    let longitude = 76.9558;


    /* Create Leaflet map */

    map = L.map("map").setView(

        [latitude, longitude],

        13

    );


    /* OpenStreetMap */

    L.tileLayer(

        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

        {

            attribution:
                "&copy; OpenStreetMap contributors"

        }

    ).addTo(map);


    /* Initial bus marker */

    busMarker = L.marker(

        [latitude, longitude]

    ).addTo(map);


    busMarker.bindPopup(

        "🚌 College Bus"

    );


    /* Get GPS location */

    updateBusLocation();

}


/* ========================================================
   GET ADMIN BUS LOCATION
======================================================== */

function updateBusLocation() {

    if (!map || !busMarker) {

        return;

    }


    fetch("/api/admin_bus_location")

        .then(function(response) {

            return response.json();

        })


        .then(function(data) {


            if (data.success) {


                let latitude =
                    parseFloat(data.latitude);


                let longitude =
                    parseFloat(data.longitude);


                /* Validate coordinates */

                if (
                    isNaN(latitude) ||
                    isNaN(longitude)
                ) {

                    return;

                }


                /* Move bus marker */

                busMarker.setLatLng([

                    latitude,

                    longitude

                ]);


                /* Move map */

                map.setView(

                    [latitude, longitude],

                    15

                );


                /* Popup */

                busMarker.setPopupContent(

                    "🚌 Bus: " +

                    (
                        data.bus_number ||
                        "Unknown Bus"
                    ) +

                    "<br>" +

                    "📍 Live GPS Location"

                );


                /* Status */

                const status =
                    document.getElementById(
                        "location-status"
                    );


                if (status) {

                    status.textContent =
                        "🟢 Live GPS location updated";

                }


            } else {


                const status =
                    document.getElementById(
                        "location-status"
                    );


                if (status) {

                    status.textContent =
                        "🟡 " +
                        (
                            data.message ||
                            "GPS location not available"
                        );

                }

            }

        })


        .catch(function(error) {

            console.error(
                "GPS Error:",
                error
            );


            const status =
                document.getElementById(
                    "location-status"
                );


            if (status) {

                status.textContent =
                    "🔴 Unable to get GPS location";

            }

        });

}


/* ========================================================
   START GPS MAP AFTER PAGE LOAD
======================================================== */

document.addEventListener(

    "DOMContentLoaded",

    function() {

        initMap();


        /* Update every 5 seconds */

        setInterval(

            updateBusLocation,

            5000

        );

    }

);
