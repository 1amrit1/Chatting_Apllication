from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from datetime import datetime

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app, manage_session=False)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    return render_template('signUp.html')

@app.route('/roomSelect', methods=['GET', 'POST'])
def index():
    if (request.method == 'POST'):
        emailEntered = request.form['email']
        passwordEntered = request.form['password']
        if(emailEntered == "student@lambton.ca" and passwordEntered == "password" ):
            return render_template('index.html')
        else:
            flash("wrong email or password",'error')
            return redirect(url_for('home'))

    else:


        return redirect(url_for('home'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        username = request.form['username']
        room = request.form['room']
        #Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session = session)
    else:
        if(session.get('username') is not None):
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ "+date+" -> "+hr+" : "+min+" ]"
    emit('status', {'msg':  session.get('username') + ' has entered the room at '+dtString}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    dt = datetime.now()
    date = (dt.strftime("%x"))
    hr = (dt.strftime("%H"))
    min = (dt.strftime("%M"))
    dtString = "[ " + date + " -> " + hr + " : " + min + " ]"
    emit('message', {'msg': session.get('username') + dtString+ ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app)