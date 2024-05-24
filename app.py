from flask import Flask, redirect, request, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from auth import authenticate, User, get_user_groups

app = Flask(__name__)
app.secret_key = 'your_secret_key_is_not_thisone'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)
login_manager.login_view = "/login"

server_uri = "ldap://10.0.0.4:389"
domain = "A10.dk"

class MessageCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.UTC))
    group = db.Column(db.String(50), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(username):
    user = User(username)
    user.groups = get_user_groups(username)
    return user

@app.route("/")
def home():
    cards = MessageCard.query.filter_by(group="main").order_by(MessageCard.timestamp.desc()).all()
    return render_template("home.html", cards=cards)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = authenticate(server_uri, domain, username, password)
            user.groups = user.groups
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
@login_required
def profile():
    return render_template("profile.html", user=current_user.username, groups=current_user.groups)

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

@app.route("/message-cards", methods=["GET", "POST"])
@login_required
def message_cards():
    if request.method == "POST":
        content = request.form['content']
        group = request.form['group']
        if group not in current_user.groups and group != "main":
            return redirect("/message-cards")

        new_card = MessageCard(author=current_user.username, content=content, group=group)
        db.session.add(new_card)
        db.session.commit()
        return redirect(f"/message-cards/{group}")
    
    user_groups = current_user.groups
    cards = MessageCard.query.filter(MessageCard.group.in_(user_groups)).order_by(MessageCard.timestamp.desc()).all()
    return render_template("message_cards.html", cards=cards, groups=user_groups)

@app.route("/message-cards/<group>", methods=["GET"])
@login_required
def message_board(group):
    if group not in current_user.groups and group != "main":
        return redirect("/message-cards")

    cards = MessageCard.query.filter_by(group=group).order_by(MessageCard.timestamp.desc()).all()
    return render_template("message_board.html", cards=cards, group=group)

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room: {}".format(data['username'], data['message']))
    emit('receive_message', data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
