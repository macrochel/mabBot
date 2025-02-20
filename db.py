from decouple import config
from pymongo.mongo_client import MongoClient
client = MongoClient(config("DB"))

def init():
    dbc = client["mabBot"]
    coll = dbc["users"]
    return dbc, coll

def initUser(coll, message):
    model = {
        "_id": message.chat.id, 
        "name": "", 
        "phone": "", 
        "education": "",  
        "hardSkills": "", 
        "softSkills": "", 
        "addInfo": "",
        "consultation": True
    }
    x =  coll.insert_one(model)
    return x.inserted_id

def findUser(coll, message):
    data = coll.find_one({ "_id": message.chat.id })
    return data

def setConsultation(coll, name, message):
    id = {"_id": message.chat.id}
    data = {"$set": {name: False}}
    x = coll.update_one(id, data)

def addColumn(coll, name, message):
    id = {"_id": message.chat.id}
    data = {"$set": {name: message.text}}
    x = coll.update_one(id, data)

def addColumnEmpty(coll, name, message):
    id = {"_id": message.chat.id}
    data = {"$set": {name: "Nothing"}}
    x = coll.update_one(id, data)