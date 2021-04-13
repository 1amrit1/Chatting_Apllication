from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from datetime import datetime
from dataBaseConnection import findUser, findMessage, insertUser, insertMessage, updateUser, updateUserAvatar

# if (emailEntered == userInDb['email'] and passwordEntered == userInDb['password']):
# KeyError: 'email'

# gp member

# session
users = []
app = Flask(__name__)
# mongoDB connection##########################################################################

app.debug = True
app.config['SECRET_KEY'] = 'secret'  # p.t.r
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app, manage_session=False)  # false since we will be using our own session (from flask)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/signUp', methods=['GET', 'POST'])  # Sign In Page
def signUp():
    return render_template('signUp.html')


@app.route('/roomSelect', methods=['GET', 'POST'])  # Room Selection for Chat
def index():
    if request.method == 'POST':
        emailEntered = request.form['email']  # {'email':'student@lambton.ca'}
        passwordEntered = request.form['password']
        userInDb = findUser({'email': emailEntered})

        if emailEntered == userInDb['email'] and passwordEntered == userInDb['password']:
            return render_template('index.html', userName=emailEntered)  # index is room select page
        else:
            flash("wrong email or password", 'error')
            return redirect(url_for('home'))

    else:

        return redirect(url_for('home'))


@app.route('/signUpNext', methods=['GET', 'POST'])  # Sign Up
def signUpNext():
    if request.method == 'POST':
        emailEntered = request.form['email']
        passwordEntered = request.form['password']
        confirmPasswordEntered = request.form['cPassword']
        securityQuestionEntered = request.form['security_question']
        securityAnswerEntered = request.form['security_answer']
        icon = request.form['avatar']
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
                       "security_answer": securityAnswerEntered, "icon": icon}
            insertUser(userObj)
            flash("Your Id Has been Created. Welcome!", 'error')
            return redirect(url_for('home'))

    else:

        return redirect(url_for('home'))  # sent to home page


@app.route('/forgotPasswordNext', methods=['GET', 'POST'])  # forget password
def forgotPasswordNext():
    if request.method == 'POST':
        emailEntered = request.form['email']
        securityQuestionEntered = request.form['security_question']
        securityAnswerEntered = request.form['security_answer']

        if (emailEntered == "" or securityQuestionEntered == "" or securityAnswerEntered == ""):
            flash("Please enter all fields!", 'error')
            return redirect(url_for('forgotPassword'))
        elif (findUser({'email': emailEntered, "security_question": securityQuestionEntered,
                        "security_answer": securityAnswerEntered}) != {}):
            flash("Your password will be reset!", 'error')
            return redirect(url_for('resetPassword'))
        else:
            return redirect(url_for('forgotPassword'))


@app.route('/resetPasswordNext', methods=['GET', 'POST'])  # reset password
def resetPasswordNext():
    if request.method == 'POST':
        emailEntered = request.form['email']
        passwordEntered = request.form['password']
        confirmPasswordEntered = request.form['confirm_password']

        if (emailEntered == "" or passwordEntered == "" or confirmPasswordEntered == ""):
            flash("Please enter all fields!", 'error')
            return redirect(url_for('forgotPassword'))
        elif (passwordEntered != confirmPasswordEntered):
            flash("Please enter same password in both fields", 'error')
            return redirect(url_for('forgotPassword'))
        elif (findUser({'email': emailEntered, "password": passwordEntered}) != {}):

            updateUser(emailEntered, passwordEntered)
            flash("Your password has been reset!", 'error')
            return redirect(url_for('home'))
        else:
            flash("Something went wrong.Please try again!")
            return redirect(url_for('resetPassword'))


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    print(session)

    if request.method == 'POST':
        username = request.form['username'].split("@")[0]
        room = request.form['room']
        # Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session=session, user=username)
    else:
        if session.get('username') is not None:
            return render_template('chat.html', session=session, user=session.get('username'))
        else:
            return redirect(url_for('index'))  # sent to room select


@socketio.on('join', namespace='/chat')  # listen
def join(message):
    room = session.get('room')
    join_room(room)  # join_room -> flask_socketio
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ " + date + " -> " + hr + " : " + min + " ]"
    users.append(session.get('username'))  # for gp members list box
    emit('status',
         {'msg': session.get('username') + ' has entered the room', 'users': users, 'user': session.get('username')},
         room=room)


@socketio.on('text', namespace='/chat')  # Start chatting
def text(message):
    room = session.get('room')
    dt = datetime.now()
    date = (dt.strftime("%d")) + "-" + (dt.strftime("%b"))
    time = (dt.strftime("%H")) + ":" + (dt.strftime("%M"))
    dtString = time + " , " + date
    print(dtString)
    if (message['msg'] == ""):
        return
    msg = session.get('username') + dtString + ' : ' + message['msg']

    msgObj = {'chat_room': room, 'message': message['msg'], 'username': message['user'], 'date': dtString}
    email = message['user'] + "@lambton.ca";
    print(email)
    icon = findUser({'email': email})['icon']
    print("before icon print---------------------------")
    print(icon)

    emit('message',
         {'msg': message['msg'], 'user': message['user'], 'date': dtString, 'icon': icon},
         room=room)
    insertMessage(msgObj)


@socketio.on('left', namespace='/chat')  # On leaving chat room
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    # session.clear()

    users.remove(message['user'])
    emit('status', {'msg': username + ' has left the room.', 'users': users}, room=room)


@app.route('/chatHistory', methods=['GET', 'POST'])  # Check on chat history
def chatHistory():
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ " + date + " -> " + hr + " : " + min + " ]"
    messages = list(findMessage({'chat_room': session.get('room')}))
    return render_template('oldMessages.html', session=session, msgs=messages)


@app.route('/userProfile', methods=['GET', 'POST'])  # profile
def userProfile():
    if request.method == 'POST':
        username = request.form['userName']
        icon = findUser({'email': username})['icon']
        print(username)

        return render_template('profile.html',username=username,icon=icon)

    else:
        if session.get('username') is not None:
            username = session.get('username')
            icon = findUser({'email': username})['icon']
            return render_template('profile.html',username=session.get('username'),icon=icon)
        else:
            return redirect(url_for('index'))  # sent to room select


@app.route('/avatarChangeFromProfile', methods=['GET', 'POST'])
def avatarChangeFromProfile():
    if request.method == 'POST':
        icon = request.form['avatar']
        username = request.form['userName']
        updateUserAvatar(username,icon)
        flash("Avatar Changed Successfully!", 'error')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))




if __name__ == '__main__':
    socketio.run(app)
