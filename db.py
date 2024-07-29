from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import requests
from io import BytesIO

load_dotenv()
username = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD')
cluster = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.jg69llz.mongodb.net/?authSource=admin")
db = cluster["Salon"]
shop = db["ShopInfo"]
services = db["services"]
timeslots = db["timeslots"]
clients = db["clients"]
inventory = db["inventory"]

SHOPINFO_ID = os.environ.get('SHOPINFO_ID')
PENDING_APPT_ID = os.environ.get('PENDING_APPT_ID')
SERVICES_ID = os.environ.get('SERVICES_ID')
TIMESLOTS_ID = os.environ.get('TIMESLOT_ID')
CLIENTS_ID = os.environ.get('CLIENTS_ID')
INVENTORY_ID = os.environ.get('INVENTORY_ID')
INVENTORY_LOG_ID = os.environ.get('INVENTORY_LOG_ID')
PENDING_RESCHEDULED_APPTS = os.environ.get('PENDING_RESCHEDULED_APPTS')
OTP_API = os.environ.get('OTP_API')
BIN_ID = os.environ.get('BIN_ID')
cloudinary.config(cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'))
FOLDER = os.getenv('CLOUDINARY_FOLDER')

def getShopInfo():
    shopinfo = shop.find_one({"_id":ObjectId(SHOPINFO_ID)})
    return shopinfo
def updateShopInfo(data):
    if data.get('imgUrl') != None:
        data['imgUrl'] = data.get('imgUrl')
    shop.update_one({"_id":ObjectId(SHOPINFO_ID)}, {"$set": data})

def addItem(data):
    shop.update_one({"_id":ObjectId(SHOPINFO_ID)}, {"$push": {'services': data}})

def deleteItem(name):
    shop.update_one({"_id":ObjectId(SHOPINFO_ID)}, {"$pull": {'services': {"name": name}}})

def addInventory(data):
    inventory.update_one({"_id":ObjectId(INVENTORY_ID)}, {"$set": {data.get('name'): data}})

def getInventory():
    return inventory.find_one({"_id":ObjectId(INVENTORY_ID)})

def getInventoryLogs():
    return inventory.find_one({"_id":ObjectId(INVENTORY_LOG_ID)})
def createInventoryLog(data):
    inventory.update_one({"_id":ObjectId(INVENTORY_LOG_ID)}, {"$push": {'log': data}})

def deleteInventory(name):
    inventory.update_one({"_id":ObjectId(INVENTORY_ID)}, {"$unset": {name: {"name": name}}})
def addTimeslot(date, data):
    timeslots.update_one({"_id":ObjectId(TIMESLOTS_ID)}, {"$set": {date: data}})

def addAppointment(data):
    services.update_one({"_id":ObjectId(PENDING_APPT_ID)}, {"$set": {data.get('apptId'): data}})

def deleteAppointment(apptId):
    services.update_one({"_id":ObjectId(PENDING_APPT_ID)}, {"$unset": {apptId: ""}})

def getAppointments():
    appointments = services.find_one({"_id":ObjectId(PENDING_APPT_ID)})
    appointments.pop('_id')
    return appointments

def getTimeSlot(date):
    allTimeSlots = timeslots.find_one({"_id":ObjectId(TIMESLOTS_ID), date: {"$exists": True}})
    if allTimeSlots==None:
        return None
    return allTimeSlots.get(date)


def updateTimeSlot(date, data):
    timeslots.update_one({"_id":ObjectId(TIMESLOTS_ID)}, {"$set": {date: data}})

def getBasicEmployee():
    return getShopInfo().get('employeesTest')

def getClients():
    return clients.find_one({"_id":ObjectId(CLIENTS_ID)})

def addClient(data):
    clients.update_one({"_id":ObjectId(CLIENTS_ID)}, {"$set": {data.get('phone'): data}})

def getServices():
    return services.find_one({"_id":ObjectId(SERVICES_ID)})

def addService(data):
    services.update_one({"_id":ObjectId(SERVICES_ID)}, {"$set": {data.get('apptId'): data}})

def addPendingRescheduledAppt(data):
    services.update_one({"_id":ObjectId(PENDING_RESCHEDULED_APPTS)}, {"$set": {data.get('apptId'): data}})

def checkingData():
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
    headers = {
        'X-Master-Key': OTP_API
    }

    req = requests.get(url, json=None, headers=headers).json()['record'].get(SHOPINFO_ID)
    return req

def getPendingRescheduledAppts():
    return services.find_one({"_id":ObjectId(PENDING_RESCHEDULED_APPTS)})

def deletePendingRescheduledAppt(apptId):
    services.update_one({"_id":ObjectId(PENDING_RESCHEDULED_APPTS)}, {"$unset": {apptId: ""}})

def updateAllEmployee(data):
    shop.update_one({"_id":ObjectId(SHOPINFO_ID)}, {"$set": {'employeesTest': data}})

def uploadImage(img):
    img = Image.open(img)
    new_image = img.resize((500, 500))
    img_byte_arr = BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    upload_result = cloudinary.uploader.upload(img_byte_arr, folder=FOLDER)
    return upload_result.get('url')

print(checkingData())