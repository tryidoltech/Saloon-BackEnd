import db
import worker
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort


def addItem(name, price, duration, employee, serviceDesc, img):
    data = {"name": name, "price": price, "duration": duration, "employee": employee, "serviceDesc": serviceDesc}
    if img != None:
        data['imgUrl'] = db.uploadImage(img)
    db.addItem(data)
    return {"sucess": True, "msg": "Service added successfully"}

def updateItem(name, price, duration, employee, serviceDesc, img):
    prevData = None
    for service in db.getShopInfo()['services']:
        if service['name'] == name:
            prevData = service
            break
    if prevData is None:
        return {"success": False, "msg": "Service not found"}
    data = {"name": name, "price": price, "duration": duration, "employee": employee, "serviceDesc": serviceDesc}
    filterData = {k: v for k, v in data.items() if v is not None}
    data = {**prevData, **filterData}
    if img != None:
        data['imgUrl'] = db.uploadImage(img)
    db.deleteItem(name)
    db.addItem(data)
    return {"sucess": True, "msg": "Service updated successfully"}

def deleteItem(name):
    db.deleteItem(name)
    return {"sucess": True, "msg": "Service deleted successfully"}

def addInventory(name, qty, price, img):
    data = {"name": name, "quantity": qty, "price": price}
    if img != None:
        data['imgUrl'] = db.uploadImage(img)
    db.addInventory(data)
    return {"sucess": True, "msg": "Inventory added successfully"}

def updateInventory(name, qty, price, img):
    prevData = worker.getInventory().get(name)
    if prevData is None:
        return {"success": False, "msg": "Inventory not found"}
    data = {"name": name, "quantity": qty, "price": price}
    filterData = {k: v for k, v in data.items() if v is not None}
    data = {**prevData, **filterData}
    if img != None:
        data['imgUrl'] = db.uploadImage(img)
    db.addInventory(data)
    return {"sucess": True, "msg": "Inventory updated successfully"}

def deleteInventory(name):
    db.deleteInventory(name)
    return {"sucess": True, "msg": "Inventory deleted successfully"}
def OTPON():
    return abort(500)
def inventoryLogs():
    logs = db.getInventoryLogs()
    logs.pop('_id')
    return logs

def editSettings(shopName, email, phone, address, gstin, ownerName, offDays, upiId, timings, img):
    data = {
        "shopName": shopName,
        "email": email,
        "phone": phone,
        "address": address,
        "gstin": gstin,
        "ownerName": ownerName,
        "offDays": offDays,
        "upiId": upiId
    }
    if timings is not None:
        data['timings'] = timings.split(',')
    data = {k: v for k, v in data.items() if v is not None}
    if img is not None:
        data['imgUrl'] = db.uploadImage(img)
    if data == {}:
        return {"success": False, "msg": "No data to update"}
    db.updateShopInfo(data)
    return {"success": True, "msg": "Settings updated successfully"}

def showShopInfo():
    shopInfo = db.getShopInfo()
    shopInfo.pop('_id')
    return shopInfo

def salesDashboard():
    services = db.getServices()
    services.pop('_id')
    todays_services = 0
    weekly_services = 0
    todays_sales = 0
    weekly_sales = 0
    pending_amount = 0
    confirmed_sales = 0
    checkedIn_sales = 0
    paid_sales = 0
    weeklyRecord = {}
    items_overview = {}
    for item in db.getShopInfo().get('services'):
        items_overview[item['name']] = 0
    for i in range(7):
        weeklyRecord[(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y")] = 0
    for service in services:
        if services[service]['status'] == "confirmed" and services[service]['date'] == datetime.now().strftime(
                "%d-%m-%Y"):
            todays_services += 1
        if datetime.strptime(services[service]['date'], "%d-%m-%Y") >= datetime.now() - timedelta(days=1) and datetime.strptime(services[service]['date'], "%d-%m-%Y") < datetime.now() + timedelta(days=6):
            weekly_services += 1
        if services[service]['status'] == "paid" and services[service]['date'] == datetime.now().strftime("%d-%m-%Y"):
            todays_sales += services[service]['recvdAmount']
        if services[service]['status'] == "paid" and datetime.strptime(services[service]['date'], "%d-%m-%Y") >= datetime.now() - timedelta(days=1) and datetime.strptime(services[service]['date'], "%d-%m-%Y") < datetime.now() + timedelta(days=6):
            weekly_sales += services[service]['recvdAmount']
            weeklyRecord[services[service]['date']] += services[service]['recvdAmount']
        if services[service]['status'] == "confirmed":
            confirmed_sales += services[service]['totalBill']
        if services[service]['status'] == "checkedIn":
            checkedIn_sales += services[service]['totalBill']
        if services[service]['status'] == "paid":
            paid_sales += services[service]['totalBill']
        for item in services[service]['services']:
            items_overview[item] += 1
    for appointment in db.getAppointments():
        pending_amount += db.getAppointments()[appointment]['totalBill']
    return {"todays_booking": todays_services, "todays_sales": todays_sales, "weekly_booking": weekly_services, "weekly_sales": weekly_sales, "pending_amount": pending_amount, "confirmed_sales": confirmed_sales, "checkedIn_sales": checkedIn_sales, "all_sales": paid_sales, "weeklyRecord": weeklyRecord, "items_overview": items_overview, "sucess": True}

def addEmployee(name, phone, designation, image):
    imageUrl = db.uploadImage(image)
    data = {"name": name, "phone": phone, "designation": designation, "imgUrl": imageUrl}
    allEmployeeData = db.getBasicEmployee()
    empId = allEmployeeData['counter'] + 1
    allEmployeeData['counter'] = empId
    allEmployeeData[str(empId)] = data
    db.updateAllEmployee(allEmployeeData)
    return {"sucess": True, "msg": "Employee added successfully", "empId": empId}

def deleteEmployee(empId):
    allEmployeeData = db.getBasicEmployee()
    allEmployeeData.pop(empId)
    db.updateAllEmployee(allEmployeeData)
    return {"sucess": True, "msg": "Employee deleted successfully"}

def editEmployee(empId, name, phone, designation, img):
    prevData = showEmployees().get(empId)
    if prevData is None:
        return {"success": False, "msg": "Employee Id not found"}
    newData = {
        "name": name,
        "phone": phone,
        "designation": designation
    }
    filteredData = {k: v for k, v in newData.items() if v is not None}
    updatedData = {**prevData, **filteredData}

    if img is not None:
        updatedData['imgUrl'] = db.uploadImage(img)
        # cloudinary_public_id = prevData['imgUrl'].split('/')[-1].split('.')[0]
        # cloudinary.uploader.destroy(cloudinary_public_id)
    allEmployeeData = db.getBasicEmployee()
    allEmployeeData[empId] = updatedData
    db.updateAllEmployee(allEmployeeData)
    return {"success": True, "msg": "Employee updated successfully"}

def showEmployees():
    employees = db.getBasicEmployee()
    employees.pop('counter')
    return employees