import pymongo
conStr = "mongodb+srv://admin:qwerty123@cluster0.h7iox.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
myclient = pymongo.MongoClient(conStr)  # this gives the cluster
db = myclient['chatting_application']  # p.t.r #this gives the collection
# query = {"email": "student@lambton.ca"}
users = db.user_data
messages = db.messages

# res = users.find()
# for i in res:
#     print(i)

def findUser(query):  #authentication
    res = users.find(query)
    # print(res)
    k = {}
    for i in res:
        k = i
        # print(i)
    return k
# print(findUser({'email': 'student@lambton.ca'}))

def findMessage(query):
    res = messages.find(query)
    return res
def insertUser(newUser):
    users.insert_one(newUser)
def insertMessage(newMessage):
    messages.insert_one(newMessage)
def updateUser(newUser):
    users.insert_one(newUser)
    
icon = findUser({'email': "student4@lambton.ca"})['icon']
print("before icon print---------------------------")
print(icon)
