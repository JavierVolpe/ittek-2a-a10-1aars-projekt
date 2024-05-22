# app.py
from flask import Flask, redirect, request, render_template
from auth import authenticate

app = Flask(__name__)
server_uri = "ldap://10.0.0.4:389"  # No TLS, standard LDAP port
domain = "A10.dk"

@app.route("/", methods=['POST', 'GET'])
def login():
    context = {}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            connection, groups = authenticate(server_uri, domain, username, password)
            context['groups'] = groups
            return render_template("loggedin.html", **context)
        except ValueError as err:
            context["error"] = str(err)

    return render_template("login.html", **context)

@app.route("/loggedin")
def loggedin():
    groups = request.args.get('groups', [])
    return render_template("loggedin.html", groups=groups)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
