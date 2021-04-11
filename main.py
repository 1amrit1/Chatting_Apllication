from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from datetime import datetime
from dataBaseConnection import findUser, findMessage, insertUser, insertMessage, updateUser

#if (emailEntered == userInDb['email'] and passwordEntered == userInDb['password']):
# KeyError: 'email'

#

#gp member

# session
users = []
app = Flask(__name__)
# mongoDB connection############################


##############################################
app.debug = True
app.config['SECRET_KEY'] = 'secret'#p.t.r
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app, manage_session=False)#false since we will be using our own session (from flask)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    return render_template('signUp.html')


@app.route('/roomSelect', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        emailEntered = request.form['email']#{'email':'student@lambton.ca'}
        passwordEntered = request.form['password']
        userInDb = findUser({'email': emailEntered})

        if emailEntered == userInDb['email'] and passwordEntered == userInDb['password']:
            return render_template('index.html')#index is room select page
        else:
            flash("wrong email or password", 'error')
            return redirect(url_for('home'))

    else:

        return redirect(url_for('home'))


@app.route('/signUpNext', methods=['GET', 'POST'])
def signUpNext():
    if request.method == 'POST':
        emailEntered = request.form['email']
        passwordEntered = request.form['password']
        confirmPasswordEntered = request.form['cPassword']
        securityQuestionEntered = request.form['security_question']
        securityAnswerEntered = request.form['security_answer']
        if passwordEntered != confirmPasswordEntered:
            flash("password and confirm password doesn't match!", 'error')
            return redirect(url_for('signUp'))
        elif (
                emailEntered == "" or passwordEntered == "" or confirmPasswordEntered == "" or securityQuestionEntered == "" or securityAnswerEntered == ""):
            flash("Fields cannot be empty!", 'error')
            return redirect(url_for('signUp'))
        elif (findUser({'email': emailEntered}) != {}):
            flash("Email already exsists!", 'error')
            return redirect(url_for('signUp'))
        else:
            userObj = {"email": emailEntered, "password": passwordEntered, "security_question": securityQuestionEntered,
                       "security_answer": securityAnswerEntered}
            insertUser(userObj)
            flash("Your Id Has been Created. Welcome!", 'error')
            return redirect(url_for('home'))

    else:

        return redirect(url_for('home'))#sent to home page


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    print(session)

    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        # Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session=session,user = session['username'])
    else:
        if session.get('username') is not None:
            return render_template('chat.html', session=session)
        else:
            return redirect(url_for('index'))#sent to room select


@socketio.on('join', namespace='/chat')#listen
def join(message):
    room = session.get('room')
    join_room(room)#join_room -> flask_socketio
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ " + date + " -> " + hr + " : " + min + " ]"
    users.append(session.get('username'))#for gp members list box
    emit('status', {'msg': session.get('username') + ' has entered the room at ' + dtString, 'users': users,'user' : session.get('username')}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ " + date + " -> " + hr + " : " + min + " ]"
    if (message['msg'] == ""):
        return
    msg = session.get('username') + dtString + ' : ' + message['msg']

    msgObj = {'chat_room': room, 'message': message['msg'], 'username': message['user'],'date': datetime.now()}

    emit('message',
         {'msg': message['user'] + dtString + ' : ' + message['msg'],'user': message['user']},
         room=room)
    insertMessage(msgObj)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    # session.clear()

    # users.remove(username)
    emit('status', {'msg': username + ' has left the room.', 'users': users}, room=room)

@app.route('/chatHistory', methods=['GET', 'POST'])
def chatHistory():
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ " + date + " -> " + hr + " : " + min + " ]"
    messages = list(findMessage({'chat_room' :session.get('room') }))
    return render_template('oldMessages.html', session=session,msgs = messages)



if __name__ == '__main__':
    socketio.run(app)

