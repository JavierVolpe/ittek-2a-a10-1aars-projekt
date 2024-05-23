from flask import Flask, redirect, request, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from auth import authenticate, User

app = Flask(__name__)
app.secret_key = 'your_secret_key_is_not_thisone'
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)

server_uri = "ldap://10.0.0.4:389"
domain = "A10.dk"

@login_manager.user_loader
def load_user(username):
    return User(username)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = authenticate(server_uri, domain, username, password)
            login_user(user)
            username = user.username
            groups_user = user.groups
            return render_template("loggedin.html", user=username, groups=groups_user)
        except ValueError as err:
            return render_template("login.html", error=str(err))
    return render_template("login.html")

@app.route("/loggedin")
@login_required
def loggedin():
    groups_user = current_user.groups
    logged_user = current_user.username
    return render_template("loggedin.html", groups=groups_user, user=logged_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/show")
@login_required
def show():
    groups_user = current_user.groups
    logged_user = current_user.username
    return render_template("show.html", groups=groups_user, user=logged_user)

@app.route("/it-chat", methods=["GET","POST"])
@login_required
def itchat():
    return render_template("it-chat.html", user=current_user.username)

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room: {}".format(data['username'], data['message']))
    emit('receive_message', data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
