import db
import time
from datetime import datetime, timedelta

import pos


def getItems():
    shopInfo = db.getShopInfo()
    return {"services": shopInfo.get('services'), "sucess": True}

def getSlots():
    timingData = db.getShopInfo()
    startTime = timingData.get('timing').get('start')
    endTime = timingData.get('timing').get('end')
    timeslot = {}
    while startTime != endTime:
        timeslot[startTime] = {}
        startTime = (datetime.strptime(startTime, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
    return list(timeslot.keys())
def createAppointment(data):
    apptId = f"{str(round(time.time() * 1000))}{data.get('name')[:2]}{data.get('pincode')}"
    services = db.getShopInfo().get('services')
    duration = sum(service['duration'] for service in services if service['name'] in data['services'])
    data['duration'] = duration
    data['apptId'] = apptId
    data['totalBill'] = sum(service['price'] for service in services if service['name'] in data['services'])
    if (datetime.strptime(data['time'], "%H:%M") + timedelta(minutes=data['duration'])).strftime("%H:%M")  not in db.getTimeSlot(data.get("date")):
        return {"sucess": False, "msg": "Invalid Time"}
    db.addAppointment(data)
    return {"sucess": True, "msg": "Appointment added successfully", "apptId": apptId}

def deleteAppointment(apptId):
    db.deleteAppointment(apptId)
    return {"sucess": True, "msg": "Appointment deleted successfully"}

def availableEmployees(date, time, serviceList):
    timeslot = db.getTimeSlot(date)
    if timeslot==None:
        response = pos.addTimeslot(date)
        if response['success']==False:
            return response
        timeslot = db.getTimeSlot(date)
    services = db.getShopInfo().get('services')
    employees = db.getBasicEmployee()
    duration = sum(service['duration'] for service in services if service['name'] in serviceList)
    duration = duration // 30
    busy_employees = timeslot.get(time)
    for duration in range(duration):
        appointment_time = datetime.strptime(time, "%H:%M")
        new_time = (appointment_time + timedelta(minutes=30 * duration)).strftime("%H:%M")
        busy_employees.update(timeslot.get(new_time))
    available_employees = set(employees.keys()) - set(busy_employees.keys())
    return list(available_employees)

def rescheduleAppointment(apptId, date, time, serviceList, preferredEmployee):
    checkAvailability = availableEmployees(date, time, serviceList)
    if type(checkAvailability) == dict:
        return checkAvailability
    db.addPendingRescheduledAppt({"apptId": apptId, "date": date, "time": time, "services": serviceList, "prefEmployee": preferredEmployee})
    return {"sucess": True, "msg": "Appointment rescheduled Request Sent successfully"}

def basicEmployeesDetail():
    data = db.getBasicEmployee()
    return data

def appointmentList(phoneNum, date):
    clientDetail = db.getClients()[phoneNum]
    appointments = db.getAppointments()
    services = db.getServices()
    clientAppointments = {}
    for appointment in appointments:
        if appointments[appointment]['phone'] == phoneNum and appointments[appointment]['date'] == date:
            clientAppointments[appointment] = appointments[appointment]
    for apptId in clientDetail['services']:
        if services[apptId]['date'] == date:
            clientAppointments[apptId] = services[apptId]
    clientAppointments['sucess'] = True
    return clientAppointments