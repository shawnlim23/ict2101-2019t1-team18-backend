from flask import Flask, jsonify, request, render_template
import flask.json as fjson
import hashlib
from datetime import datetime
import classes
import dbconnector as db

# import flask_sqlalchemy

app = Flask(__name__)


@app.route("/amble")
def hello():
    return "Hello Amble!"


# ----------AUTHENTICATION----------
# Register
@app.route("/amble/auth/register", methods=["POST"])
def register():
    # requires POST method
    if request.method == "POST":
        # if email not in request return failure
        if "email" not in request.form:
            return "No email in Request"
        email = request.form["email"]
        if db.check_email(email) != 0:
            return "Email is already in use"

        # password stuff
        if "password" not in request.form:
            return "No password"

        pwd = request.form["password"]
        # create salt
        salt = datetime.now().strftime("%Y-%b-%a %H:%M:%S")
        # convert password to hash
        password = hashlib.sha256((pwd + salt).encode("utf-8")).hexdigest()

        name = ""
        if "name" in request.form:
            name = request.form["name"]

        age = -1
        if "age" in request.form:
            age = int(request.form["age"])

        sex = 0
        if "sex" in request.form:
            sex = int(request.form["sex"])

        commute_method = 0
        if "commuteMethod" in request.form:
            commute_method = int(request.form["commuteMethod"])

        user = classes.User(email, password, salt, name, age, sex, commute_method)
        db.register(user)
        return "success"


# Login
@app.route("/amble/auth/login", methods=["POST"])
def login():
    print("test")
    if request.method == "POST":
        if "email" not in request.form:
            return "No email in Request"
        email = request.form["email"]
        if db.check_email(email) == 0:
            return "User not found"

        # password stuff
        if "password" not in request.form:
            return "No password"
        pwd = request.form["password"]
        # convert password to hash
        deets = db.get_salt(email)
        password = hashlib.sha256((pwd + deets["salt"]).encode("utf-8")).hexdigest()

        # authentication
        if password == deets["password"]:
            # generate token and return user
            token = hashlib.sha256(
                datetime.now().strftime("%Y-%b-%a %H:%M:%S").encode("utf-8")
            ).hexdigest()
            user = db.login(deets["userID"], token)
            user["token"] = str(deets["userID"]) + "/" + token
            return jsonify(user)
        else:
            return "false"


# logout
@app.route("/amble/auth/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        if "token" in request.form:
            token = request.form["token"]
            result = db.logout(token)
            return result


# ----------USERS----------
# get all users
@app.route("/amble/users")
def getUsers():
    return jsonify(db.get_users())


# get one user
@app.route("/amble/users/<string:uID>")
def getUser(uID):
    return jsonify(db.get_user(uID))


# ----------LANDMARKS----------

# ----------CANVASES----------
# getAllCanvases
@app.route("/amble/canvas/<string:cID>", methods=["GET"])
def getCanvases():
    pass


@app.route("/amble/canvas/image/<string:ciID>")
def getCanvasImage(ciID):
    return render_template("image.html", name=(ciID))


# ----------COMMENTS----------


# ----------STARTUP----------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

