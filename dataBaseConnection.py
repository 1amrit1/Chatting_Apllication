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
    # k = res[0]
    for i in res:
        k = i
        # print(i)
    return k
# print(findUser({'email': 'student@lambton.ca'}))
def findAllUsers():
    res = users.find()
    return res
def findMessage(query):
    res = messages.find(query)
    return res
def insertUser(newUser):
    users.insert_one(newUser)
def insertMessage(newMessage):
    messages.insert_one(newMessage)

def updateUser(emailEntered,passwordEntered):
    emailObj = {"email": emailEntered}
    passwordObj = {"$set": {"password": passwordEntered}}
    users.update(emailObj,passwordObj)

def updateUserAvatar(emailEntered,icon):
    print("in db:",emailEntered,":",icon)
    users.update({'email':emailEntered},{"$set": {"icon": icon}})
    
# icon = findUser({'email': "student4@lambton.ca"})['icon']
# print("before icon print---------------------------")
# print(icon)

# messages.delete_many( { } );
