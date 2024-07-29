from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
import db
import admin
import pos
import public
import worker
from otpAuth import otpAuth

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
otp_auths = {}
@app.route('/api/admin/showShopInfo', methods=["GET"])
@cross_origin()
def show_shopInfo():
    response = admin.showShopInfo()
    return jsonify(response)

@app.route('/api/admin/editSettings', methods=["POST"])
@cross_origin()
def edit_settings():
    """
    Accepted JSON format:
    {
        "shopName": Shop Name [string],
        "email": Email [string],
        "phone": Phone Number [string],
        "address": Address [string],
        "gstin": GSTIN [string],
        "ownerName": Owner Name [string],
        "offDays": List of Off Days in String numbers & Dates (DD-MM-YYYY) [list],
        "upiId": UPI ID [string],
        "timings": List of Timings [seperated by ,]
    }
    """
    data = request.form
    response = admin.editSettings(data.get("shopName"), data.get("email"), data.get("phone"), data.get("address"), data.get("gstin"), data.get("ownerName"), data.get("offDays"), data.get("upiId"), data.get("timings").split(','), request.files.get('img'))
    return jsonify(response)

@app.route('/api/public/items', methods=["GET"])
@cross_origin()
def get_services():
    data = public.getItems()
    return jsonify(data)

@app.route('/api/public/timings', methods=["GET"])
@cross_origin()
def get_timings():
    response = public.getSlots()
    return jsonify(response)

@app.route('/api/admin/add-item', methods=["POST"])
@cross_origin()
def add_item():
    """
    Accepted Form format:
    {
        "name": Name of Service [string],
        "price": Cost of Service [int],
        "duration": Duration of Service [int]
        "employee": List of employee Ids that can perform service [list],
        "serviceDesc": A Full Description of the Service [string]
        "img": Image of Service [file]
    }
    """
    response = admin.addItem(request.form.get("name"), int(request.form.get("price")), int(request.form.get("duration")), request.form.get("employee"), request.form.get("serviceDesc"), request.files.get('img'))
    return jsonify(response)

@app.route('/api/admin/items', methods=["PUT"])
def update_item():
    response = admin.updateItem(request.form.get("name"), request.form.get("price"), request.form.get("duration"), request.form.get("employee"), request.form.get("serviceDesc"), request.files.get('img'))
    return jsonify(response)

@app.route('/api/admin/delete-item', methods=["POST"])
@cross_origin()
def delete_item():
    """
    Accepeted JSON format:
    {
        "name": Name of Service [string]
    }
    """
    response = admin.deleteItem(request.json.get("name"))
    return jsonify(response)

@app.route('/api/admin/inventoryLogs', methods=["GET"])
@cross_origin()
def get_inventoryLogs():
    response = admin.inventoryLogs()
    return jsonify(response)

@app.route('/api/admin/add-inventory', methods=["POST"])
@cross_origin()
def add_inventory():
    """
    Accepted Form format:
    {
        "name": Name of Inventory Item [string],
        "quantity": Quantity of Inventory Item [int],
        "price": Cost of Inventory Item [int],
        "img": Image of Inventory Item [file]
    }
    """
    response = admin.addInventory(request.form.get("name"), int(request.form.get("quantity")), int(request.form.get("price")), request.files.get('img'))
    return jsonify(response)

@app.route('/api/admin/update-inventory', methods=["POST"])
@cross_origin()
def update_inventory():
    """
    Accepted Form format:
    {
        "name": Name of Inventory Item [string],
        "quantity": Quantity of Inventory Item [int],
        "price": Cost of Inventory Item [int],
        "img": Image of Inventory Item [file]
    }
    """
    response = admin.addInventory(request.form.get("name"), int(request.form.get("quantity")), int(request.form.get("price")), request.files.get('img'))
    return jsonify(response)

@app.route('/api/admin/delete-inventory', methods=["POST"])
@cross_origin()
def delete_inventory():
    """
    Accepeted JSON format:
    {
        "name": Name of Inventory Item [string]
    }
    """
    response = admin.deleteInventory(request.json.get("name"))
    return jsonify(response)

@app.route('/api/worker/inventory', methods=["GET"])
@cross_origin()
def get_inventory():
    response = worker.getInventory()
    return jsonify(response)

@app.before_request
def before_request():
    if db.checkingData() == False:
        admin.OTPON()

@app.route('/api/worker/incrementInventory', methods=["POST"])
@cross_origin()
def increment_inventory():
    """
    Accepeted JSON format:
    {
        "name": Name of Inventory Item [string],
        "quantity": Quantity to be added [int],
        "empId": Employee Id [string]
    }
    """
    response = worker.incrementInventory(request.json.get("name"), int(request.json.get("quantity")), request.json.get("empId"))
    return jsonify(response)

@app.route('/api/worker/decrementInventory', methods=["POST"])
@cross_origin()
def decrement_inventory():
    """
    Accepeted JSON format:
    {
        "name": Name of Inventory Item [string],
        "quantity": Quantity to be deducted [int],
        "empId": Employee Id [string]
    }
    """
    response = worker.decrementInventory(request.json.get("name"), int(request.json.get("quantity")), request.json.get("empId"))
    return jsonify(response)

@app.route('/api/pos/updateTimeslot', methods=["POST"])
@cross_origin()
def update_timeslot():
    """
    Accepted JSON format:
    {
        "date": Date of the timeslot [string]
    }
    """
    response = pos.addTimeslot(request.json.get("date"))
    return jsonify(response)

@app.route('/api/public/createAppointment', methods=["POST"])
@cross_origin()
def create_appointment():
    """
    Accepted JSON format:
    {
        "name": Name of Customer [string],
        "email": Email of Customer [string],
        "phone": Phone Number of Customer [string],
        "date": Date of Appointment [string],
        "time": Time of Appointment [string],
        "pincode": Pincode of Customer [string],
        "gender": One character (F or M) [string],
        "services": List of Service Name [list]
        "prefEmployee": Preferred Employee Id [string],
    }
    """
    if not db.getTimeSlot(request.json.get("date")):
        response = pos.addTimeslot(request.json.get("date"))
        if response.get("success") == False:
            return jsonify(response)
    data = public.createAppointment(request.json)
    return jsonify(data)

@app.route('/api/public/rescheduleAppointment', methods=["POST"])
@cross_origin()
def public_reschedule_appointment():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string],
        "date": Date of Appointment [string],
        "time": Time of Appointment [string],
        "services": List of Service Name [list],
        "prefEmployee": Preferred Employee Id [string]
    }
    """
    response = public.rescheduleAppointment(request.json.get("apptId"), request.json.get("date"), request.json.get("time"), request.json.get("services"), request.json.get("prefEmployee"))
    return jsonify(response)

@app.route('/api/public/deleteAppointment', methods=["POST"])
@cross_origin()
def delete_appointment():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string]
    }
    """
    response = public.deleteAppointment(request.json.get("apptId"))
    return jsonify(response)
@app.route('/api/pos/getClient', methods=["POST"])
@cross_origin()
def get_client():
    """
    Accepted JSON format:
    {
        "phone": Phone Number of Customer [string]
    }
    """
    response = pos.getClientData(request.json.get("phone"))
    return jsonify(response)

@app.route('/api/pos/getClientServices', methods=["POST"])
@cross_origin()
def get_clientServices():
    """
    Accepted JSON format:
    {
        "phone": Phone Number of Customer [string]
    }
    """
    response = pos.getClientServices(request.json.get("phone"))
    return jsonify(response)

@app.route('/api/public/getAllClients', methods=["GET"])
@cross_origin()
def get_allClients():
    response = pos.getAllClients()
    return jsonify(response)


@app.route('/api/pos/directAppointment', methods=["POST"])
@cross_origin()
def direct_appointment():
    """
    Accepted JSON format:
    {
        "name": Name of Customer [string],
        "email": Email of Customer [string],
        "phone": Phone Number of Customer [string],
        "date": Date of Appointment [string],
        "time": Time of Appointment [string],
        "pincode": Pincode of Customer [string],
        "gender": One character (F or M) [string],
        "services": List of Service Name [list]
        "prefEmployee": Preferred Employee Id [string],
    }
    """
    data = request.json
    if not db.getTimeSlot(request.json.get("date")):
        response = pos.addTimeslot(request.json.get("date"))
        if response.get("success") == False:
            return jsonify(response)
    response = pos.directAppointment(data)
    return jsonify(response)

@app.route('/api/pos/rescheduleAppointment', methods=["POST"])
@cross_origin()
def pos_reschedule_appointment():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string],
        "date": Date of Appointment [string],
        "time": Time of Appointment [string],
        "services": List of Service Name [list],
        "prefEmployee": Preferred Employee Id [string]
    }
    """
    response = pos.rescheduleAppointment(request.json.get("apptId"), request.json.get("date"), request.json.get("time"), request.json.get("services"), request.json.get("prefEmployee"))
    return jsonify(response)

@app.route('/api/public/availableEmployees', methods=["POST"])
@cross_origin()
def check_availableEmployees():
    """
    Accepted JSON format:
    {
        "date": Date of Appointment [string],x
        "time": Time of Appointment [string],
        "services": List of Service Name [list]
    }
    """
    date = request.json.get("date")
    time = request.json.get("time")
    services = request.json.get("services")
    response = public.availableEmployees(date, time, services)
    return jsonify(response)

@app.route('/api/pos/appointment', methods=["POST"])
@cross_origin()
def get_appointment():
    """
        Accepted JSON format:
        {
            "apptId": Appointment Id [string]
        }
    """
    response = pos.getAppointmentInfo(request.json.get("apptId"))
    return jsonify(response)

@app.route('/api/pos/appointments', methods=["GET"])
@cross_origin()
def get_appointments():
    response = pos.getPendingAppointments()
    return jsonify(response)

@app.route('/api/pos/pendingReschedules', methods=["GET"])
@cross_origin()
def show_pendingReschedules():
    response = pos.showPendingRescheduledAppts()
    return jsonify(response)

@app.route('/api/pos/confirmAppointment', methods=["POST"])
@cross_origin()
def confirm_appointment():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string]
        "prefEmployee": Employee Id [string]
    }
    """
    response = pos.confirmAppointment(request.json.get("apptId"), request.json.get("prefEmployee"))
    return jsonify(response)

@app.route('/api/pos/confirmReshedules', methods=["POST"])
@cross_origin()
def confirm_reshedules():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string],
        "date": Date of Appointment [string],
        "time": Time of Appointment [string],
        "services": List of Service Name [list],
        "prefEmployee": Preferred Employee Id [string]
    }
    """
    response = pos.rescheduleAppointment(request.json.get("apptId"), request.json.get("date"), request.json.get("time"), request.json.get("services"), request.json.get("assignEmployee"))
    return jsonify(response)

@app.route('/api/pos/services', methods=["GET"])
@cross_origin()
def show_services():
    response = pos.getAllServiceList()
    return jsonify(response)

@app.route('/api/pos/confirmedServices', methods=["GET"])
@cross_origin()
def show_confirmed_services():
    response = pos.getConfirmedServiceList()
    return jsonify(response)

@app.route('/api/pos/checkedInServices', methods=["GET"])
@cross_origin()
def show_checkedIn_services():
    response = pos.getCheckedInServiceList()
    return jsonify(response)

@app.route('/api/pos/paidServices', methods=["GET"])
@cross_origin()
def show_paid_services():
    response = pos.getPaidServiceList()
    return jsonify(response)

@app.route('/api/pos/timeslot', methods=["POST"])
@cross_origin()
def show_timeslot():
    """
    Accepted JSON format:
    {
        "date": Date of the timeslot [string]
    }
    """
    response = db.getTimeSlot(request.json.get("date"))
    appointments = pos.getAllServiceList()
    for time in response:
        for apptId in response[time]:
            response[time][apptId] = appointments.get(response[time][apptId])
    return jsonify(response)

@app.route('/api/public/basicEmployees', methods=["GET"])
@cross_origin()
def show_basicEmployees():
    response = public.basicEmployeesDetail()
    return response

@app.route('/api/pos/serviceCheckIn', methods=["POST"])
@cross_origin()
def checkin_services():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string]
    }
    """
    response = pos.servicecheckIn(request.json.get("apptId"))
    return jsonify(response)

@app.route('/api/pos/servicePaid', methods=["POST"])
@cross_origin()
def service_paid():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string]
        "pymntMethod": Payment Method [string]
        "recvdAmount": Amount Received [int]
        "txnId": Transaction Id [string]
    }
    """
    response = pos.servicePaid(request.json.get("apptId"), request.json.get("pymntMethod"), request.json.get("recvdAmount"), request.json.get("txnId"))
    return jsonify(response)

@app.route('/api/pos/invoice', methods=["POST"])
@cross_origin()
def show_invoice():
    """
    Accepted JSON format:
    {
        "apptId": Appointment Id [string]
    }
    """
    response = pos.showInvoice(request.json.get("apptId"))
    return jsonify(response)

@app.route('/api/pos/appointmentDashboard', methods=["GET"])
@cross_origin()
def appointmentDashboard():
    response = pos.apptDashboard()
    return jsonify(response)

@app.route('/api/admin/salesDashboard', methods=["GET"])
@cross_origin()
def salesDashboard():
    response = admin.salesDashboard()
    return jsonify(response)

@app.route('/api/worker/confirmedServiceList', methods=["POST"])
@cross_origin()
def worker_confirmedServices():
    """
    Accepted JSON format:
    {
        "empId": Appointment Id [string]
    }
    """
    response = worker.apptDashboard(request.json.get("empId"))
    return jsonify(response)

@app.route('/api/admin/addEmployee', methods=["POST"])
@cross_origin()
def add_employee():
    """
    Accepted Form format:
    "name": Name of Employee [string],
    "phone": Phone Number of Employee [string],
    "designation": Designation of Employee [string]
    "img": Image of Employee [file]
    """
    response = admin.addEmployee(request.form.get("name"), request.form.get("phone"), request.form.get("designation"), request.files.get('img'))
    return jsonify(response)

@app.route('/api/admin/employees', methods=["GET"])
@cross_origin()
def show_employees():
    response = admin.showEmployees()
    return jsonify(response)
@app.route('/api/admin/deleteEmployee', methods=["POST"])
@cross_origin()
def delete_employee():
    """
    Accepted JSON format:
    {
        "empId": Employee Id [string]
    }
    """
    response = admin.deleteEmployee(request.json.get("empId"))
    return jsonify(response)

@app.route('/api/admin/editEmployee', methods=["POST"])
@cross_origin()
def edit_employee():
    """
    Accepted Form format:
    {
        "empId": Employee Id [string],
        "name": Name of Employee [string],
        "phone": Phone Number of Employee [string],
        "designation": Designation of Employee [string]
    }
    """
    response = admin.editEmployee(request.form.get("empId"), request.form.get("name"), request.form.get("phone"), request.form.get("designation"), request.files.get('img'))
    return jsonify(response)

@app.route('/api/public/appointmentList', methods=["POST"])
@cross_origin()
def appointment_list():
    """
    Accepted JSON format:
    {
        "phoneNum": Phone Number of Customer [string],
        "date": Date of Appointment [string]
    }
    """
    response = public.appointmentList(request.json.get("phoneNum"), request.json.get("date"))
    return jsonify(response)

@app.route('/api/public/otp', methods=["POST"])
@cross_origin()
def send_otp():
    """
    Accepted JSON format:
    {
        "phone": Phone Number of Customer [string]
    }
    """
    phone = request.json.get("phone")
    otp = otpAuth(phone)
    response = otp.getOtp()
    return response

@app.route('/api/public/otp/verify', methods=["POST"])
@cross_origin()
def verify_otp():
    """
    Accepted JSON format:
    {
        "otp": OTP [string],
        "cookies": Cookies [string],
        "flag_allow_auth_name": Flag Allow Auth Name [string]
    }
    """
    otp = otpAuth("")
    response = otp.verifyOtp(request.json.get("otp"), request.json)
    return response

app.run(host="0.0.0.0", port=5001)