from flask import Flask, redirect, request, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_socketio import SocketIO, emit
from auth import authenticate, User, get_user_groups

app = Flask(__name__)
app.secret_key = 'your_secret_key_is_not_thisone'
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)

server_uri = "ldap://10.0.0.4:389"
domain = "A10.dk"

@login_manager.user_loader
def load_user(username):
    # Fetch user details and groups from a database or persistent store
    # Here, assuming a dummy implementation for illustration
    user = User(username)
    user.groups = get_user_groups(username)  # Implement this function to fetch groups
    return user

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = authenticate(server_uri, domain, username, password)
            user.groups = user.groups  # Ensure groups are assigned to the user object
            login_user(user)
            return render_template("home.html")
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

@app.route("/profile")
def profile():
    return render_template("profile.html", user=current_user.username, groups=current_user.groups)

@app.route("/show")
@login_required
def show():
    groups_user = current_user.groups
    logged_user = current_user.username
    return render_template("show.html", groups=groups_user, user=logged_user)

@app.route("/it-chat", methods=["GET", "POST"])
@login_required
def itchat():
    if 'IT' in current_user.groups:
        return render_template("it-chat.html", user=current_user.username, groups=current_user.groups)
    else:
        return redirect("/")

@app.route("/hr-chat", methods=["GET", "POST"])
@login_required
def hrchat():
    if 'HR' in current_user.groups:
        return render_template("hr-chat.html", user=current_user.username, groups=current_user.groups)
    else:
        return redirect("/")

@app.route("/manager-chat", methods=["GET", "POST"])
@login_required
def managerchat():
    if 'Manager' in current_user.groups:
        return render_template("manager-chat.html", user=current_user.username, groups=current_user.groups)
    else:
        return redirect("/")

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room: {}".format(data['username'], data['message']))
    emit('receive_message', data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
