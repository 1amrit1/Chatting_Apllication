from flask import render_template, Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/login')
def show_login():
    return render_template('login.html')

if __name__ == '__main__':
   app.run(port=5000)

print("hello all")
