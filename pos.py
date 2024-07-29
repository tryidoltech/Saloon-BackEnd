import admin
import db
import time
from datetime import datetime, timedelta
import public

def getTimeslot(date):
    timeslot = db.getTimeSlot(date)
    timeslot["sucess"] = True
    return timeslot

def addTimeslot(date):
    timingData = db.getShopInfo()
    startTime = timingData.get('timing').get('start')
    endTime = timingData.get('timing').get('end')
    offDays = timingData.get('offDays')
    if date in offDays or str(datetime.strptime(date, "%d-%m-%Y").weekday()) in offDays:
        return {"success": False, "msg": "Shop is closed on this day"}
    timeslot = {}
    while startTime != endTime:
        timeslot[startTime] = {}
        startTime = (datetime.strptime(startTime, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
    db.addTimeslot(date, timeslot)
    return {"success": True, "msg": "Timeslot added successfully"}

def getClientData(phone):
    client = db.getClients().get(phone)
    if client == None:
        return {"sucess": False, "msg": "Client not found"}
    client['sucess'] = True
    return client

def getClientServices(phone):
    client = db.getClients().get(phone)
    if client == None:
        return {"sucess": False, "msg": "Client not found"}
    services = getAllServiceList()
    clientServices = {}
    for service in client['services']:
        clientServices[service] = services.get(service)
    clientServices["sucess"] = True
    return clientServices

def getAllClients():
    clients = db.getClients()
    clients.pop('_id')
    clients["sucess"] = True
    return clients

def directAppointment(data):
    services = db.getShopInfo().get('services')
    client = db.getClients().get(data['phone'])
    apptId = f"{str(round(time.time() * 1000))}{data.get('name')[:2]}{data.get('pincode')}"
    data['apptId'] = apptId
    data['duration'] = sum(service['duration'] for service in services if service['name'] in data['services'])
    appointment = data
    if (datetime.strptime(appointment['time'], "%H:%M") + timedelta(minutes=appointment['duration'])).strftime("%H:%M")  not in db.getTimeSlot(data.get("date")):
        return {"sucess": False, "msg": "Invalid Time"}
    """UPDATING CLIENT"""
    if client == None:
        db.addClient({"name": appointment['name'], "email": appointment['email'], "phone": appointment['phone'],
                      "gender": appointment["gender"], "pincode": appointment["pincode"], "doc": datetime.now().strftime("%d-%m-%Y"),
                      "services": [appointment['apptId']]})
    else:
        client['services'].append(appointment['apptId'])
        db.addClient(client)

    """SERVICE CREATION"""
    appointment['recvdAmount'] = 0
    appointment['txnIds'] = []
    appointment['appointmentType'] = "offline"
    appointment['assignedEmployee'] = data.get("prefEmployee")
    appointment.pop('prefEmployee')
    appointment['discountCode'] = None
    appointment['status'] = "confirmed"
    appointment['totalBill'] = sum(
        service['price'] for service in services if service['name'] in appointment['services'])
    db.addService(appointment)
    db.deleteAppointment(appointment['apptId'])
    return {"sucess": True, "msg": "Appointment Confirmed", "serviceId": appointment['apptId']}

def confirmAppointment(apptId, prefEmployee):
    appointment = db.getAppointments().get(apptId)
    client = db.getClients().get(appointment['phone'])
    """UPDATING CLIENT"""
    if client == None:
        db.addClient({"name": appointment['name'], "email": appointment['email'], "phone": appointment['phone'],
                      "gender": appointment["gender"], "pincode": appointment["pincode"], "doc": datetime.now().strftime("%d-%m-%Y"),
                      "services": [appointment['apptId']]})
    else:
        client['services'].append(appointment['apptId'])
        db.addClient(client)
    services = []
    """SERVICE CREATION"""
    appointment.pop('prefEmployee')
    appointment['recvdAmount'] = 0
    appointment['txnIds'] = []
    appointment['appointmentType'] = "online"
    appointment['assignedEmployee'] = prefEmployee
    appointment['discountCode'] = None
    appointment['status'] = "confirmed"
    appointment['totalBill'] = sum(
        service['price'] for service in services if service['name'] in appointment['services'])
    db.addService(appointment)
    db.deleteAppointment(appointment['apptId'])
    return {"sucess": True, "msg": "Appointment Confirmed", "serviceId": appointment['apptId']}

def rescheduleAppointment(apptId, date, time, serviceList, preferredEmployee):
    apptData = db.getAppointments()
    allservices = db.getServices()
    services = db.getShopInfo().get('services')
    allservices.pop('_id')
    apptData.update(allservices)
    if apptId not in apptData.keys():
        return {"sucess": False, "msg": "Invalid Appointment ID"}
    apptData = apptData.get(apptId)
    if date==None:
        date = apptData.get('date')
    if time==None:
        time = apptData.get('time')
    if serviceList==None:
        serviceList = apptData.get('services')
    if preferredEmployee==None:
        preferredEmployee = apptData.get('assignedEmployee')
    response = public.availableEmployees(date, time, serviceList)
    newDuration = sum(service['duration'] for service in services if service['name'] in serviceList)
    if type(response) == dict:
        return response
    if (datetime.strptime(time, "%H:%M") + timedelta(minutes=newDuration)).strftime("%H:%M")  not in db.getTimeSlot(date):
        return {"sucess": False, "msg": "Invalid Time"}
    if apptData.get('status') == None:
        public.deleteAppointment(apptId)
        apptData['date'] = date
        apptData['time'] = time
        apptData['services'] = serviceList
        apptData['prefEmployee'] = preferredEmployee
        public.createAppointment(apptData)
    if apptData.get('status') == "confirmed":
        """REMOVING APPTS FROM TIMESLOT"""
        timeslot = db.getTimeSlot(apptData.get('date'))
        duration = apptData.get('duration') // 30
        for duration in range(duration):
            appointment_time = datetime.strptime(apptData['time'], "%H:%M")
            new_time = (appointment_time + timedelta(minutes=30 * duration)).strftime("%H:%M")
            del timeslot[new_time][apptData.get('assignedEmployee')]
        db.updateTimeSlot(apptData['date'], timeslot)

        """UPDATING SERVICE"""
        apptData['date'] = date
        apptData['time'] = time
        apptData['services'] = serviceList
        apptData['assignedEmployee'] = preferredEmployee
        apptData['totalBill'] = sum(service['price'] for service in services if service['name'] in serviceList)
        apptData['duration'] = newDuration
        db.addService(apptData)

    else:
        return {"sucess": False, "msg": "Invalid Appointment status"}
    return {"sucess": True, "msg": "Appointment rescheduled successfully"}
def getAppointmentInfo(apptId):
    service = db.getServices().get(apptId)
    if service == None:
        return {"sucess": False, "msg": "Appointment not found"}
    service['sucess'] = True
    return service

def getPendingAppointments():
    data = db.getAppointments()
    employees = db.getBasicEmployee()
    employees.pop('counter')
    services = db.getShopInfo().get('services')
    for x in data:
        appointment = data.get(x)
        timeslot = db.getTimeSlot(appointment['date'])
        duration = sum(service['duration'] for service in services if service['name'] in appointment['services'])
        duration = duration // 30
        busy_employees = timeslot.get(appointment['time'])
        for duration in range(duration):
            appointment_time = datetime.strptime(appointment['time'], "%H:%M")
            new_time = (appointment_time + timedelta(minutes=30 * duration)).strftime("%H:%M")
            busy_employees.update(timeslot.get(new_time))
        available_employees = set(employees.keys()) - set(busy_employees.keys())
        appointment['available_employees'] = list(available_employees)
    data["sucess"] = True
    return data

def showPendingRescheduledAppts():
    data = db.getPendingRescheduledAppts()
    data.pop('_id')
    employees = db.getBasicEmployee()
    services = db.getShopInfo().get('services')
    for x in data:
        appointment = data.get(x)
        timeslot = db.getTimeSlot(appointment['date'])
        duration = sum(service['duration'] for service in services if service['name'] in appointment['services'])
        duration = duration // 30
        busy_employees = timeslot.get(appointment['time'])
        for duration in range(duration):
            appointment_time = datetime.strptime(appointment['time'], "%H:%M")
            new_time = (appointment_time + timedelta(minutes=30 * duration)).strftime("%H:%M")
            busy_employees.update(timeslot.get(new_time))
        available_employees = set(employees.keys()) - set(busy_employees.keys())
        appointment['available_employees'] = list(available_employees)
    data["sucess"] = True
    return data

def deletePendingRescheduledAppt(apptId):
    db.deletePendingRescheduledAppt(apptId)
    return {"sucess": True, "msg": "Appointment deleted successfully"}

def getAllServiceList():
    data = db.getServices()
    data.pop('_id')
    data["sucess"] = True
    return data
def getConfirmedServiceList():
    services = db.getServices()
    services.pop('_id')
    mainData = {}
    for service in services:
        if services.get(service).get('status') == "confirmed":
            mainData[service] = services.get(service)
    mainData["sucess"] = True
    return mainData
def getPaidServiceList():
    services = db.getServices()
    services.pop('_id')
    mainData = {}
    for service in services:
        if services.get(service).get('status') == "paid":
            mainData[service] = services.get(service)
    mainData["sucess"] = True
    return mainData

def getCheckedInServiceList():
    services = db.getServices()
    services.pop('_id')
    mainData = {}
    for service in services:
        if services.get(service).get('status') == "checkedIn":
            mainData[service] = services.get(service)
    mainData["sucess"] = True
    return mainData

def servicecheckIn(apptId):
    service = db.getServices().get(apptId)
    if service == None:
        return {"sucess": False, "msg": "Service not found"}
    service['status'] = "checkedIn"
    db.addService(service)
    return {"sucess": True, "msg": "Checkin Successful"}

def servicePaid(apptId, pymntMethod, recvdAmount, txnId):
    service = db.getServices().get(apptId)
    if service == None:
        return {"sucess": False, "msg": "Service not found"}
    service['status'] = "paid"
    service['pymntMethod'] = pymntMethod
    service['recvdAmount'] = recvdAmount
    service['txnIds'].append(txnId)
    service['billedDate'] = datetime.now().strftime("%d-%m-%Y")
    db.addService(service)
    return {"sucess": True, "msg": "Paid Successful"}

def showInvoice(apptId):
    serviceInfo = getAppointmentInfo(apptId)
    if serviceInfo.get('sucess') == False:
        return serviceInfo
    if serviceInfo.get('status') not in ["paid", "checkedIn"]:
        return {"sucess": False, "msg": "Service not paid or checked in"}
    itemList = public.getItems()['services']
    shopInfo = admin.showShopInfo()
    invoiceInfo = {}
    invoiceInfo['shopName'] = shopInfo.get('shopName')
    invoiceInfo['shopLogo'] = shopInfo.get('imgUrl')
    invoiceInfo['shopAddress'] = shopInfo.get('address')
    invoiceInfo['ownerName'] = shopInfo.get('ownerName')
    invoiceInfo['shopPhone'] = shopInfo.get('phone')
    invoiceInfo['shopEmail'] = shopInfo.get('email')
    invoiceInfo['gstin'] = shopInfo.get('gstin')
    invoiceInfo['serviceId'] = apptId
    if serviceInfo.get('billedDate')==None:
        invoiceInfo['date'] = datetime.now().strftime("%d-%m-%Y")
    else:
        invoiceInfo['date'] = serviceInfo.get('billedDate')
    invoiceInfo['clientName'] = serviceInfo.get('name')
    invoiceInfo['clientPhone'] = serviceInfo.get('phone')
    invoiceInfo['clientEmail'] = serviceInfo.get('email')
    invoiceInfo['totalAmount'] = serviceInfo.get('totalBill')
    invoiceInfo['services'] = []
    for service in serviceInfo.get('services'):
        serviceData = {}
        serviceData['name'] = service
        serviceData['price'] = next((item['price'] for item in itemList if item.get('name') == service), 0)
        invoiceInfo['services'].append(serviceData)
    invoiceInfo['sucess'] = True
    return invoiceInfo


def apptDashboard():
    services = db.getServices()
    services.pop('_id')
    todays_services = []
    weekly_services = []
    pending_appointment = []
    confirmed_services = []
    checkedIn_services = []
    paid_services = []
    weeklyRecord = {}
    total_clients = []
    new_clients = []
    for i in range(7):
        weeklyRecord[(datetime.now() + timedelta(days=i)).strftime("%d-%m-%Y")] = {"online": [], "offline": []}
    for service in services:
        if services[service]['status'] == "confirmed" and services[service]['date'] == datetime.now().strftime("%d-%m-%Y"):
            todays_services.append(services[service])
        if datetime.strptime(services[service]['date'], "%d-%m-%Y") >= datetime.now() - timedelta(days=1) and datetime.strptime(services[service]['date'], "%d-%m-%Y") < datetime.now() + timedelta(days=6):
            weekly_services.append(services[service])
            if services[service]['appointmentType'] == "online":
                weeklyRecord[services[service]['date']]['online'].append(services[service])
            else:
                weeklyRecord[services[service]['date']]['offline'].append(services[service])
        if services[service]['status'] == "confirmed":
            confirmed_services.append(services[service])
        if services[service]['status'] == "checkedIn":
            checkedIn_services.append(services[service])
        if services[service]['status'] == "paid":
            paid_services.append(services[service])
    clients = db.getClients()
    clients.pop('_id')
    for appointment in db.getAppointments():
        pending_appointment.append(appointment)
    for client in clients:
        total_clients.append(clients[client])
        if datetime.strptime(clients[client]['doc'], "%d-%m-%Y") >= datetime.now() - timedelta(days=7):
            new_clients.append(clients[client])
    return {"todays_services": todays_services, "weekly_services": weekly_services, "pending_appointment": pending_appointment, "confirmed_services": confirmed_services, "checkedIn_services": checkedIn_services, "paid_services": paid_services, "weeklyRecord": weeklyRecord, "total_clients": total_clients, "new_clients": new_clients, "sucess": True}