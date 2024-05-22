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
            global user # TEST
            user = authenticate(server_uri, domain, username, password)
            login_user(user)
            username = user.username
            groups_user = user.groups
            # return redirect("/loggedin")
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



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
