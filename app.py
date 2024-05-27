# -*- coding: utf-8 -*-
# Import necessary modules from Flask and other libraries
from flask import Flask, redirect, request, render_template, url_for, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from auth import authenticate, User, get_user_groups
from news import get_latest_news, add_post_to_database
from config import Config 

# Initialize the Flask application
app = Flask(__name__)

# Set the secret key for the application (used for session management)
app.secret_key = Config.SECRET_KEY

# Configure the database URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

# Initialize Flask-Login with the app
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize Flask-SocketIO with the app
socketio = SocketIO(app)

# Set the login view for Flask-Login
login_manager.login_view = "/login"

# Configuration for the LDAP server
server_uri = Config.LDAP_SERVER_URI
domain = Config.LDAP_DOMAIN

# Define the MessageCard model for the database
class MessageCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    author = db.Column(db.String(150), nullable=False)  # Author of the message
    content = db.Column(db.Text, nullable=False)  # Content of the message
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of the message
    group = db.Column(db.String(150), nullable=False)  # Group to which the message belongs

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Function to close the database connection after each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to load the user from the database
@login_manager.user_loader
def load_user(username):
    user = User(username)
    user.groups = get_user_groups(username)
    return user

# Definerer en rute for hjemmesiden, der accepterer både GET og POST anmodninger
@app.route("/", methods=["GET", "POST"])
def home():
    # Tjekker om anmodningen er en POST anmodning
    if request.method == "POST":
        # Henter indholdet fra formen i anmodningen
        content = request.form['content']
        # Opretter et nyt MessageCard objekt med brugerens navn, indholdet fra formen, og gruppen "main"
        card = MessageCard(author=current_user.username, content=content, group="main")
        # Tilføjer det nye MessageCard objekt til databasen session
        db.session.add(card)
        # Committer (gemmer) ændringerne i databasen session
        db.session.commit()
        # Omdirigerer brugeren tilbage til den side, de kom fra
        return redirect(request.referrer)
    # Hvis anmodningen ikke er en POST anmodning (dvs. det er en GET anmodning)
    # Henter alle MessageCard objekter fra gruppen "main", sorteret efter tidsstempel i faldende rækkefølge
    cards = MessageCard.query.filter_by(group="main").order_by(MessageCard.timestamp.desc()).all()
    # Returnerer hjemmesiden, og passerer MessageCard objekterne og datetime modulet til skabelonen
    return render_template("home.html", cards=cards, datetime=datetime)

# Route for the login page
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

# Route to display when the user is logged in
@app.route("/loggedin")
@login_required
def loggedin():
    return render_template("loggedin.html", groups=current_user.groups, user=current_user.username)

# Route for logging out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# Route for the user profile page
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user.username, groups=current_user.groups)

# Route for the news page with pagination
@app.route('/news')
@login_required
def show_news():
    page = request.args.get('page', 1, type=int)
    permissions = current_user.groups
    news_items = get_latest_news(permissions, page=page, page_size=5)
    return render_template('news.html', news_items=news_items, page=page)

# Route to create a new post
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = current_user.username
        permissions = request.form.getlist('permissions')
        print("Permissions:", permissions)  # Debugging line to check the fetched permissions
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_post_to_database(title, content, author, permissions, timestamp)
        return redirect("/news")
    return render_template('create_post.html', user=current_user.username, groups=current_user.groups)

# Route for the IT chat page
@app.route("/it-chat", methods=["GET", "POST"])
@login_required
def itchat():
    if 'IT' in current_user.groups:
        return render_template("it-chat.html", user=current_user.username, groups=current_user.groups)
    else:
        return redirect("/")

# Route for the HR chat page
@app.route("/hr-chat", methods=["GET", "POST"])
@login_required
def hrchat():
    if 'HR' in current_user.groups:
        return render_template("hr-chat.html", user=current_user.username, groups=current_user.groups)
    else:
        return redirect("/")

# Route for the manager chat page
@app.route("/manager-chat", methods=["GET", "POST"])
@login_required
def managerchat():
    if 'Manager' in current_user.groups:
        return render_template("manager-chat.html", user=current_user.username, groups=current_user.groups)
    else:
        return redirect("/")

# Route to handle message cards
@app.route("/message-poster", methods=["GET", "POST"])
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
    return render_template("message_poster.html", cards=cards, datetime=datetime)

# Route for group-specific chat pages
@app.route("/<group>-chat")
@login_required
def group_chat(group):
    if group not in current_user.groups:
        return "Access Denied", 403
    cards = MessageCard.query.filter_by(group=group).order_by(MessageCard.timestamp.desc()).all()
    return render_template("message_board.html", cards=cards, group=group, datetime=datetime)

# Route for the admin panel
@app.route("/admin-panel")
@login_required
def admin_panel():
    if 'Enterprise Admins' not in current_user.groups:
        return "Access Denied", 403

    all_posts = MessageCard.query.all().__reversed__()
    return render_template("admin_panel.html", all_posts=all_posts)

# Route to delete a post (admin only)
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

# Socket.IO event handler for sending messages
@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room: {}".format(data['username'], data['message']))
    emit('receive_message', data, broadcast=True)

# Main entry point for running the app
if __name__ == "__main__": 
    socketio.run(app, host="0.0.0.0", port=Config.SERVER_PORT, debug=True) 