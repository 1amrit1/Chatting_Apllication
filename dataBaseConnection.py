
import pymongo
conStr = "mongodb+srv://admin:qwerty123@cluster0.h7iox.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
myclient = pymongo.MongoClient(conStr)
db = myclient['chatting_application']
# query = {"email": "student@lambton.ca"}
users = db.user_data
messages = db.messages

res = users.find()
for i in res:
    print(i)

def findUser(query):
    res = users.find(query)
    return res
def findMessage(query):
    res = messages.find(query)
    return res
def insertUser(newUser):
    users.insert_one(newUser)
def insertMessage(newMessage):
    users.insert_one(newMessage)
def updateUser(newUser):
    users.insert_one(newUser)








