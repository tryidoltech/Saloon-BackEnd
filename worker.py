import db
from datetime import datetime

def apptDashboard(empId):
    services = db.getServices()
    services.pop('_id')
    empAssignedServices = {}
    for service in services:
        if services[service]['assignedEmployee'] == empId and services[service]['status'] == "confirmed":
            empAssignedServices[service] = services[service]
    empAssignedServices['sucess'] = True
    return empAssignedServices

def getInventory():
    inventory = db.getInventory()
    inventory.pop('_id')
    return inventory

def chooseInventoryOperation(operation, name, quantity, empId):
    if operation == "add":
        return incrementInventory(name, quantity, empId)
    elif operation == "deduct":
        return decrementInventory(name, quantity, empId)
    else:
        return {"success": False, "msg": "Invalid operation"}

def incrementInventory(name, quantity, empId):
    inventory = db.getInventory()
    inventory.pop('_id')
    prevQty = int(inventory[name]['quantity'])
    inventory[name]['quantity'] = int(quantity) + prevQty
    db.addInventory(inventory[name])
    db.createInventoryLog({"empId": empId, "inventory_used": name, "quantity": quantity, "operation": "add", "time": datetime.now()})
    return {"sucess": True, "msg": "Inventory updated successfully"}

def decrementInventory(name, quantity, empId):
    inventory = db.getInventory()
    inventory.pop('_id')
    prevQty = int(inventory[name]['quantity'])
    inventory[name]['quantity'] = int(quantity) - prevQty
    db.addInventory(inventory[name])
    db.createInventoryLog({"empId": empId, "inventory_used": name, "quantity": quantity, "operation": "deduct", "time": datetime.now()})
    return {"sucess": True, "msg": "Inventory updated successfully"}