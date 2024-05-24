from flask import Flask, redirect, request, render_template, url_for, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from auth import authenticate, User, get_user_groups
from news import get_latest_news, add_post_to_database

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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    group = db.Column(db.String(150), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@login_manager.user_loader
def load_user(username):
    user = User(username)
    user.groups = get_user_groups(username)
    return user

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        content = request.form['content']
        card = MessageCard(author=current_user.username, content=content, group="main")
        db.session.add(card)
        db.session.commit()
        return redirect(request.referrer)
    cards = MessageCard.query.filter_by(group="main").order_by(MessageCard.timestamp.desc()).all()
    return render_template("home.html", cards=cards, datetime=datetime)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = authenticate(server_uri, domain, username, password)
            login_user(user)
            return redirect("/")
        except ValueError as err:
            return render_template("login.html", error=str(err))
    return render_template("login.html")

@app.route("/loggedin")
@login_required
def loggedin():
    return render_template("loggedin.html", groups=current_user.groups, user=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user.username, groups=current_user.groups)

@app.route("/news", methods=["GET", "POST"])
@login_required
def news():
    news_items = get_latest_news(current_user.groups)
    return render_template("news.html", user=current_user.username, groups=current_user.groups, news_items=news_items)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = current_user.username
        # Fetch multiple permissions as a list
        permissions = request.form.getlist('permissions')
        print("Permissions:", permissions)  # Debugging line to check the fetched permissions
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_post_to_database(title, content, author, permissions, timestamp)
        return redirect("/news")
    return render_template('create_post.html', user=current_user.username, groups=current_user.groups)

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
        card = MessageCard(author=current_user.username, content=content, group=group)
        db.session.add(card)
        db.session.commit()
        return redirect(request.referrer)
    
    user_groups = current_user.groups
    cards = MessageCard.query.filter(MessageCard.group.in_(user_groups)).order_by(MessageCard.timestamp.desc()).all()
    return render_template("message_cards.html", cards=cards, datetime=datetime)

@app.route("/<group>-chat")
@login_required
def group_chat(group):
    if group not in current_user.groups:
        return "Access Denied", 403
    cards = MessageCard.query.filter_by(group=group).order_by(MessageCard.timestamp.desc()).all()
    return render_template("message_board.html", cards=cards, group=group, datetime=datetime)

@app.route("/admin-panel")
@login_required
def admin_panel():
    if 'Enterprise Admins' not in current_user.groups:
        return "Access Denied", 403

    all_posts = MessageCard.query.all()
    return render_template("admin_panel.html", all_posts=all_posts)

@app.route("/delete-post/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    if 'Enterprise Admins' not in current_user.groups:
        return "Access Denied", 403

    post = MessageCard.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('admin_panel'))


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room: {}".format(data['username'], data['message']))
    emit('receive_message', data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)