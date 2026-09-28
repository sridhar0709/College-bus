from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from config import Config
from bson.objectid import ObjectId
from datetime import datetime
import random

app = Flask(__name__)
app.config.from_object(Config)


# ==========================================
# MONGODB ATLAS CONNECTION
# ==========================================
try:
    client = MongoClient(
        app.config["MONGO_URI"],
        serverSelectionTimeoutMS=5000
    )

    # Test connection
    client.admin.command("ping")

    # Select database
    db = client[app.config["DATABASE_NAME"]]

    # ==========================================
    # COLLECTIONS
    # ==========================================

    admins = db["admins"]
    students = db["students"]
    parents = db["parents"]
    drivers = db["drivers"]
    buses = db["buses"]
    routes = db["routes"]
    complaints = db["complaints"]

    # GPS locations
    gps_locations = db["gps_locations"]

    # QR attendance
    qr_attendance_collection = db["qr_attendance"]

    print("MongoDB Atlas connected successfully.")

except Exception as e:

    print("MongoDB connection failed:")
    print(e)

    client = None
    db = None

    admins = None
    students = None
    parents = None
    drivers = None
    buses = None
    routes = None
    complaints = None
    gps_locations = None
    qr_attendance_collection = None

# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================================
# ADMIN LOGIN
# ==========================================================

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin = admins.find_one({
            "username": username,
            "password": password
        })

        if admin:

            session.clear()

            session["role"] = "admin"
            session["admin"] = username

            return redirect(
                url_for("admin_dashboard")
            )

        flash("Invalid username or password.")

    return render_template("admin_login.html")







@app.route("/admin_dashboard")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    student_count = students.count_documents({})
    parent_count = parents.count_documents({})
    driver_count = drivers.count_documents({})
    bus_count = buses.count_documents({})

    attendance_count = qr_attendance_collection.count_documents({})

    complaint_count = complaints.count_documents({})

    student_list = list(students.find().sort("_id", -1))
    parent_list = list(parents.find().sort("_id", -1))
    driver_list = list(drivers.find().sort("_id", -1))
    bus_list = list(buses.find().sort("_id", -1))

    location_list = list(
        gps_locations.find()
        .sort("_id", -1)
        .limit(50)
    )

    complaint_list = list(
        complaints.find().sort("_id", -1)
    )

    attendance_list = list(
        qr_attendance_collection.find()
        .sort("_id", -1)
    )

    return render_template(
        "admin_dashboard.html",
        student_count=student_count,
        parent_count=parent_count,
        driver_count=driver_count,
        bus_count=bus_count,
        attendance_count=attendance_count,
        complaint_count=complaint_count,
        students=student_list,
        parents=parent_list,
        drivers=driver_list,
        buses=bus_list,
        locations=location_list,
        complaints=complaint_list,
        attendance=attendance_list
    )


# ==========================================================
# ADD BUS DETAILS
# ==========================================================

@app.route("/add_bus", methods=["GET", "POST"])
def add_bus():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        bus_number = request.form.get("bus_number", "").strip()
        bus_name = request.form.get("bus_name", "").strip()
        driver_name = request.form.get("driver_name", "").strip()
        driver_phone = request.form.get("driver_phone", "").strip()
        capacity = request.form.get("capacity", "").strip()
        route = request.form.get("route", "").strip()

        # Check duplicate bus
        existing_bus = buses.find_one({
            "bus_number": bus_number
        })

        if existing_bus:
            flash("Bus number already exists.")
            return redirect(url_for("admin_dashboard"))

        bus_data = {
            "bus_number": bus_number,
            "bus_name": bus_name,
            "driver_name": driver_name,
            "driver_phone": driver_phone,
            "capacity": capacity,
            "route": route
        }

        buses.insert_one(bus_data)

        flash("Bus details added successfully.")

        return redirect(url_for("admin_dashboard"))

    return render_template("add_bus.html")


# ==========================================================
# ADD STUDENT DETAILS
# ==========================================================

@app.route("/add_student", methods=["POST"])
def add_student():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    register_no = request.form.get(
        "register_no", ""
    ).strip()

    name = request.form.get(
        "name", ""
    ).strip()

    department = request.form.get(
        "department", ""
    ).strip()

    year = request.form.get(
        "year", ""
    ).strip()

    phone = request.form.get(
        "phone", ""
    ).strip()

    email = request.form.get(
        "email", ""
    ).strip()

    password = request.form.get(
        "password", ""
    ).strip()

    bus_number = request.form.get(
        "bus_number", ""
    ).strip()

    route = request.form.get(
        "route", ""
    ).strip()


    # Check duplicate register number

    existing_student = students.find_one({
        "register_no": register_no
    })

    if existing_student:

        flash(
            "Register number already exists."
        )

        return redirect(
            url_for("admin_dashboard")
        )


    student_data = {

        "register_no": register_no,

        "name": name,

        "department": department,

        "year": year,

        "phone": phone,

        "email": email,

        "password": password,

        "bus_number": bus_number,

        "route": route
    }


    students.insert_one(student_data)


    flash(
        "Student details added successfully."
    )


    return redirect(
        url_for("admin_dashboard")
    )



# ==========================================================
# DELETE STUDENT
# ==========================================================

@app.route("/delete_student/<student_id>")
def delete_student(student_id):

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    try:

        result = students.delete_one({
            "_id": ObjectId(student_id)
        })

        if result.deleted_count > 0:

            flash("Student deleted successfully.")

        else:

            flash("Student not found.")

    except Exception as e:

        print("Delete student error:", e)

        flash("Unable to delete student.")

    return redirect(
        url_for("admin_dashboard")
    )



# ==========================================================
# ADD PARENT
# ==========================================================

@app.route("/add_parent", methods=["POST"])
def add_parent():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    phone_number = request.form.get("phone_number", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    student_register_no = request.form.get("student_register_no", "").strip()
    relationship = request.form.get("relationship", "").strip()
    address = request.form.get("address", "").strip()

    existing_parent = parents.find_one({
        "phone_number": phone_number
    })

    if existing_parent:

        flash("Parent phone number already exists.")

        return redirect(
            url_for("admin_dashboard")
        )

    parent_data = {

        "name": name,
        "phone_number": phone_number,
        "email": email,
        "password": password,
        "student_register_no": student_register_no,
        "relationship": relationship,
        "address": address
    }

    parents.insert_one(parent_data)

    flash("Parent details added successfully.")

    return redirect(
        url_for("admin_dashboard")
    )

# ==========================================================
# DELETE PARENT
# ==========================================================

@app.route("/delete_parent/<parent_id>")
def delete_parent(parent_id):

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    try:

        result = parents.delete_one({
            "_id": ObjectId(parent_id)
        })

        if result.deleted_count > 0:

            flash("Parent deleted successfully.")

        else:

            flash("Parent not found.")

    except Exception as e:

        print("Delete parent error:", e)

        flash("Unable to delete parent.")

    return redirect(
        url_for("admin_dashboard")
    )



# ==========================================================
# ADD DRIVER
# ==========================================================

@app.route("/add_driver", methods=["POST"])
def add_driver():

    # Only admin can add driver
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    # Get form values
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    license_number = request.form.get("license", "").strip()
    bus_number = request.form.get("bus_number", "").strip()
    experience = request.form.get("experience", "").strip()
    password = request.form.get("password", "").strip()

    # Check required fields
    if not name or not phone or not license_number or not password:
        flash("Please fill all required driver details.")
        return redirect(url_for("admin_dashboard"))

    # Check duplicate phone number
    existing_driver = drivers.find_one({
        "phone": phone
    })

    if existing_driver:
        flash("Driver phone number already exists.")
        return redirect(url_for("admin_dashboard"))

    # Check duplicate license
    existing_license = drivers.find_one({
        "license": license_number
    })

    if existing_license:
        flash("License number already exists.")
        return redirect(url_for("admin_dashboard"))

    # ==========================================
    # GENERATE DRIVER ID
    # ==========================================

    driver_id = "DRV" + str(random.randint(1000, 9999))

    # Make sure Driver ID is unique
    while drivers.find_one({"driver_id": driver_id}):
        driver_id = "DRV" + str(random.randint(1000, 9999))

    # ==========================================
    # DRIVER DATA
    # ==========================================

    driver_data = {
        "driver_id": driver_id,
        "name": name,
        "phone": phone,
        "license": license_number,
        "bus_number": bus_number,
        "experience": experience,
        "password": password
    }

    # Insert into MongoDB
    drivers.insert_one(driver_data)

    flash(
        f"Driver details added successfully. Driver ID: {driver_id}"
    )

    return redirect(
        url_for("admin_dashboard")
    )

# ==========================================================
# DELETE DRIVER
# ==========================================================

@app.route("/delete_driver/<driver_id>")
def delete_driver(driver_id):

    # Only admin can delete driver
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    try:

        result = drivers.delete_one({
            "_id": ObjectId(driver_id)
        })

        if result.deleted_count > 0:

            flash("Driver deleted successfully.")

        else:

            flash("Driver not found.")

    except Exception as e:

        print("Delete driver error:", e)

        flash("Unable to delete driver.")

    return redirect(
        url_for("admin_dashboard")
    )




# ==========================================================
# DELETE BUS
# ==========================================================

@app.route("/delete_bus/<bus_id>")
def delete_bus(bus_id):

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    try:
        result = buses.delete_one({
            "_id": ObjectId(bus_id)
        })

        if result.deleted_count > 0:
            flash("Bus deleted successfully.")
        else:
            flash("Bus not found.")

    except Exception as e:
        print("Delete bus error:", e)
        flash("Unable to delete bus.")

    return redirect(url_for("admin_buses"))


# ==========================================================
# LIVE GPS LOCATION
# ==========================================================

@app.route("/admin_live_location")
def admin_live_location():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    locations = list(
        gps_locations.find().sort("_id", -1).limit(50)
    )

    return render_template(
        "admin_live_location.html",
        locations=locations
    )


# ==========================================================
# VIEW COMPLAINTS
# ==========================================================

@app.route("/admin_complaints")
def admin_complaints():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    complaint_list = list(
        complaints.find().sort("_id", -1)
    )

    return render_template(
        "admin_complaints.html",
        complaints=complaint_list
    )


# ==========================================================
# UPDATE COMPLAINT STATUS
# ==========================================================

@app.route(
    "/update_complaint/<complaint_id>",
    methods=["POST"]
)
def update_complaint(complaint_id):

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    status = request.form.get(
        "status", "Pending"
    )

    try:

        complaints.update_one(
            {
                "_id": ObjectId(complaint_id)
            },
            {
                "$set": {
                    "status": status
                }
            }
        )

        flash(
            "Complaint status updated."
        )

    except Exception:

        flash(
            "Unable to update complaint."
        )

    return redirect(
        url_for("admin_complaints")
    )


# ==========================================================
# VIEW ATTENDANCE
# ==========================================================

@app.route("/admin_attendance")
def admin_attendance():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    attendance_list = list(
    qr_attendance_collection.find().sort("_id", -1)
)

    return render_template(
        "admin_attendance.html",
        attendance=attendance_list
    )



# ==========================================================
# ADMIN LIVE GPS PAGE
# ==========================================================

@app.route("/admin_bus_tracking")
def admin_bus_tracking():

    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    location_list = list(
        gps_locations.find().sort("_id", -1).limit(50)
    )

    return render_template(
        "admin_bus_tracking.html",
        location_list=location_list
    )


# ==========================================================
# ADMIN BUS LOCATION API
# ==========================================================

@app.route("/api/admin_bus_location")
def admin_bus_location():

    if session.get("role") != "admin":

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    location = gps_locations.find_one(
        {},
        sort=[("_id", -1)]
    )


    if not location:

        return jsonify({
            "success": False,
            "message": "GPS location not available"
        })


    return jsonify({

        "success": True,

        "bus_number":
            location.get("bus_number"),

        "latitude":
            location.get("latitude"),

        "longitude":
            location.get("longitude")

    })


# ==========================================
# STUDENT LOGIN
# ==========================================

@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        register_no = request.form.get("register_no", "").strip()
        password = request.form.get("password", "").strip()

        if db is None:
            flash("Database connection failed.")
            return redirect(url_for("student_login"))

        student = students.find_one({
            "register_no": register_no,
            "password": password
        })

        if student:

            session.clear()

            session["student"] = register_no
            session["role"] = "student"

            return redirect(url_for("student_dashboard"))

        flash("Invalid Register Number or Password.")

    return render_template("student_login.html")


# ==========================================
# STUDENT DASHBOARD
# ==========================================

@app.route("/student_dashboard")
def student_dashboard():

    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    student = students.find_one({
        "register_no": session["student"]
    })

    return render_template(
        "student_dashboard.html",
        student=student
    )


# ==========================================
# BUS DETAILS
# ==========================================

@app.route("/bus_details")
def bus_details():

    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    student = students.find_one({
        "register_no": session["student"]
    })

    return render_template(
        "bus_details.html",
        student=student
    )


# ==========================================
# QR ATTENDANCE
# ==========================================

@app.route("/qr_attendance")
def qr_attendance():

    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    student = students.find_one({
        "register_no": session["student"]
    })

    return render_template(
        "qr_attendance.html",
        student=student
    )


# ==========================================
# ROUTE INFORMATION
# ==========================================

@app.route("/route_information")
def route_information():

    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    student = students.find_one({
        "register_no": session["student"]
    })

    return render_template(
        "route_information.html",
        student=student
    )


# ==========================================
# STUDENT COMPLAINT
# ==========================================

@app.route("/student_complaint", methods=["GET", "POST"])
def student_complaint():

    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    if request.method == "POST":

        complaint = {
            "register_no": session["student"],
            "message": request.form.get("message", "").strip(),
            "status": "Pending"
        }

        complaints.insert_one(complaint)

        flash("Complaint submitted successfully.")

# ==========================================
# STUDENT BUS TRACKING
# ==========================================

@app.route("/bus_tracking")
def bus_tracking():

    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    locations = list(
        gps_locations.find()
        .sort("_id", -1)
        .limit(20)
    )

    return render_template(
        "bus_tracking.html",
        locations=locations
    )

# ==========================================
# PARENT LOGIN
# ==========================================

@app.route("/parent_login", methods=["GET", "POST"])
def parent_login():

    if request.method == "POST":

        phone_no = request.form.get("phone_no", "").strip()
        password = request.form.get("password", "").strip()

        parent = parents.find_one({
            "phone_number": phone_no,
            "password": password
        })

        if parent:

            session.clear()

            session["role"] = "parent"
            session["parent"] = phone_no

            return redirect(
                url_for("parent_dashboard")
            )

        flash("Invalid Phone Number or Password.")

    return render_template("parent_login.html")



# ==========================================================
# PARENT DASHBOARD
# ==========================================================
@app.route("/parent_dashboard")
def parent_dashboard():

    if session.get("role") != "parent":
        return redirect(url_for("parent_login"))

    parent = parents.find_one({
        "phone_number": session.get("parent")
    })

    return render_template(
        "parent_dashboard.html",
        parent=parent
    )

# ==========================================================
# PARENT BUS ROUTE
# ==========================================================

@app.route("/parent_bus_route")
def parent_bus_route():

    if session.get("role") != "parent":
        return redirect(url_for("parent_login"))

    parent = parents.find_one({
        "phone_number": session.get("parent")
    })

    bus = None

    if parent and parent.get("bus_number"):

        bus = buses.find_one({
            "bus_number": parent.get("bus_number")
        })

    return render_template(
        "parent_bus_route.html",
        parent=parent,
        bus=bus
    )


# ==========================================================
# PARENT ETA
# ==========================================================

@app.route("/parent_eta")
def parent_eta():

    if session.get("role") != "parent":
        return redirect(url_for("parent_login"))

    parent = parents.find_one({
        "phone_number": session.get("parent")
    })

    return render_template(
        "parent_eta.html",
        parent=parent,
        eta="15 minutes"
    )




@app.route("/parent_bus_tracking")
def parent_bus_tracking():

    if session.get("role") != "parent":
        return redirect(url_for("parent_login"))

    parent = parents.find_one({
        "phone_number": session.get("parent")
    })

    if not parent:
        flash("Parent details not found.")
        return redirect(url_for("parent_login"))

    student_register_no = parent.get("student_register_no")

    student = None

    if student_register_no:
        student = students.find_one({
            "register_no": student_register_no
        })

    bus = None

    if student:
        bus_number = student.get("bus_number")

        if bus_number:
            bus = buses.find_one({
                "bus_number": bus_number
            })

    location = None

    if bus:
        bus_number = bus.get("bus_number")

        location = gps_locations.find_one(
            {"bus_number": bus_number},
            sort=[("_id", -1)]
        )

    return render_template(
        "parent_bus_tracking.html",
        parent=parent,
        student=student,
        bus=bus,
        location=location
    )

# ==========================================
# DRIVER LOGIN
# ==========================================

@app.route("/driver_login", methods=["GET", "POST"])
def driver_login():

    if request.method == "POST":

        driver_id = request.form.get("driver_id")
        password = request.form.get("password")

        if db is None:
            flash("Database connection failed.")
            return redirect(url_for("driver_login"))

        driver = drivers.find_one({
            "driver_id": driver_id,
            "password": password
        })

        if driver:

            session.clear()

            session["driver"] = driver_id
            session["role"] = "driver"

            return redirect(url_for("driver_dashboard"))

        flash("Invalid Driver ID or Password.")

    return render_template("driver_login.html")


# ==========================================
# DRIVER DASHBOARD
# ==========================================

@app.route("/driver_dashboard")
def driver_dashboard():

    if session.get("role") != "driver":
        return redirect(url_for("driver_login"))

    driver = drivers.find_one({
        "driver_id": session["driver"]
    })

    return render_template(
        "driver_dashboard.html",
        driver=driver
    )

@app.route("/api/update_location", methods=["POST"])
def update_location():

    if session.get("role") != "driver":
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = request.get_json()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "success": False,
            "message": "Latitude and longitude are required"
        }), 400

    driver_id = session.get("driver")

    driver = drivers.find_one({
        "driver_id": driver_id
    })

    if not driver:
        return jsonify({
            "success": False,
            "message": "Driver not found"
        }), 404

    bus_number = driver.get("bus_number")

    if not bus_number:
        return jsonify({
            "success": False,
            "message": "No bus assigned to this driver"
        }), 400

    gps_locations.insert_one({
        "driver_id": driver_id,
        "bus_number": bus_number,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "timestamp": datetime.now()
    })

    return jsonify({
        "success": True,
        "message": "Location updated successfully"
    })


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)