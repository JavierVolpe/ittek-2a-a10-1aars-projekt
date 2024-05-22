from flask import Flask, redirect, request, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # Add current_user here
from auth import authenticate, User



app = Flask(__name__)
app.secret_key = 'your_secret_key_is_not_thisone'  # Change this to a random secret key
login_manager = LoginManager()
login_manager.init_app(app)

server_uri = "ldap://10.0.0.4:389"  # No TLS, standard LDAP port
domain = "A10.dk"

@login_manager.user_loader
def load_user(username):
    # This callback is used to reload the user object from the user ID stored in the session
    return User(username)

@app.route("/", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = authenticate(server_uri, domain, username, password)
            login_user(user)
            return redirect("/loggedin")
        except ValueError as err:
            return render_template("login.html", error=str(err))

    return render_template("login.html")

@app.route("/loggedin")
@login_required
def loggedin():
    groups = current_user.groups
    logged_user = current_user.username
    return render_template("loggedin.html", groups=groups, user=logged_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
