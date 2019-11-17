from flask import Flask, jsonify, request, render_template
import flask.json as fjson
import hashlib
from datetime import datetime
import classes
import dbconnector as db
import json
import misc
import os

# import flask_sqlalchemy
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./static/images"
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.route("/")
def index():
    return "Henlo!"

@app.route("/amble")
def hello():
    return jsonify({"result": "success", "return": "Hello Amble"})


@app.route("/amble/test/<string:imageName>", methods=["POST"])
def funcname(imageName):
    file = request.files["file"]
    file.save(os.path.join("./static/images/canvas", (imageName)))
    return render_template("image.html", name=(imageName))


# ========== AUTHENTICATION ==========

# Register
@app.route("/amble/auth/register", methods=["POST"])
def register():
    # requires POST method
    if request.method == "POST":
        result = {"result": "error", "error": ""}
        # print(request.form["json"])
        # ensure json has been posted
        if "json" not in request.form:
            result["error"] = "no json in request"
            return jsonify(result)
        jason = json.loads(request.form["json"])

        # if email not in request return failure
        if "email" not in jason:
            result["error"] = "no email in json"
            return jsonify(result)
        email = jason["email"]

        # if email is invalid return invalid email
        if not misc.regex_email(email):
            result["error"] = "invalid email"
            return jsonify(result)

        # check if email already exists in system
        if db.check_email_exists(email):
            result["error"] = "email already in use"
            return jsonify(result)

        # password stuff
        if "password" not in jason:
            result["error"] = "no password in json"
            return jsonify(result)

        pwd = jason["password"]
        # create salt
        salt = datetime.now().strftime("%Y-%b-%a %H:%M:%S")
        # convert password to hash
        password = hashlib.sha256((pwd + salt).encode("utf-8")).hexdigest()

        user = classes.User(email, password, salt)

        if "name" in jason:
            user.name = jason["name"]

        if "age" in jason:
            user.age = int(jason["age"])

        if "sex" in jason:
            user.sex = int(jason["sex"])

        if "commuteMethod" in jason:
            user.commute_method = int(jason["commuteMethod"])

        db.register(user)
        result = {"result": "success"}
        return jsonify(result)


# Login
@app.route("/amble/auth/login", methods=["POST"])
def login():
    # print("test")
    result = {"result": "error", "error": ""}

    if request.method == "POST":
        # convert json from form into dict
        if "json" not in request.form:
            result["error"] = "no json in request"
            return jsonify(result)
        jason = json.loads(request.form["json"])

        if "email" not in jason:
            result["error"] = "no email in json"
            return jsonify(result)
        email = jason["email"]

        # password stuff
        if "password" not in jason:
            result["error"] = "no password in json"
            return jsonify(result)
        pwd = jason["password"]

        # convert password to hash
        deets = db.get_salt(email)
        if deets == None:  # if returns None means no user exists
            result["error"] = "incorrect email/password"
            return jsonify(result)
        password = hashlib.sha256((pwd + deets["salt"]).encode("utf-8")).hexdigest()

        # authentication pw doesn't match and email exists
        if password != deets["password"]:
            result["error"] = "incorrect email/password"
            return jsonify(result)

        # generate token and return user
        token = hashlib.sha256(
            datetime.now().strftime("%Y-%b-%a %H:%M:%S").encode("utf-8")
        ).hexdigest()

        user = db.login(deets["userID"], token)
        user["token"] = str(deets["userID"]) + "/" + token
        return jsonify({"result": "success", "return": user})


# logout
@app.route("/amble/auth/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        result = {"result": "error", "error": ""}

        if "json" not in request.form:
            result["error"] = "no json in request"
            return jsonify(result)
        jason = json.loads(request.form["json"])

        if "token" not in jason:
            result["error"] = "no token in json"
            return jsonify(result)
        token = jason["token"]

        if db.logout(token):
            return jsonify({"result": "success"})
        else:
            result["error"] = "invalid token"
            return jsonify(result)


# ========== USERS ==========

# get all users
@app.route("/amble/users")
def getUsers():
    return jsonify(db.get_users())


# get one user
@app.route("/amble/user/<string:uID>")
def getUser(uID):
    return jsonify(db.get_user(uID))


# ========== LANDMARKS ==========

# get or create canvas
@app.route("/amble/landmark/<string:placeID>")
def getLandmark(placeID):
    landmark = db.get_landmark(placeID)
    if landmark == {}:
        landmarkObject = classes.Landmark(placeID)
        db.create_landmark(landmarkObject)
        landmark = db.get_landmark(placeID)

    canvases = db.get_canvases_by_landmark(placeID)
    landmark["canvases"] = canvases
    return jsonify(landmark)


# ========== CANVASES ==========

# Create Canvas
@app.route("/amble/canvas/createCanvas", methods=["POST"])
def createCanvas():
    if request.method == "POST":
        result = {"result": "error", "error": ""}
        # print(request.form["json"])
        # ensure json has been posted
        if "json" not in request.form:
            result["error"] = "no json in request"
            return jsonify(result)
        jason = json.loads(request.form["json"])

        # check if landmark is invalid
        if not ("userID" in jason and db.check_user_exists(jason["userID"])):
            result["error"] = "invalid userID"
            return jsonify(result)
        userID = str(jason["userID"])

        # check if place id is in json and landmark exists
        if not ("placeID" in jason and db.check_landmark_exists(jason["placeID"])):
            result["error"] = "invalid placeID"
            return jsonify(result)
        placeID = jason["placeID"]

        if "file" not in request.files:
            result["error"] = "invalid file"
            return jsonify(result)
        print("creating canvas")
        canvas = classes.Canvas(userID, placeID)
        if "title" in jason:
            canvas.title = jason["title"]

        if "description" in jason:
            canvas.description = jason["description"]

        if "editable" in jason:
            canvas.editable = jason["editable"]

        print("just about to create canvas")
        canvasID = db.create_canvas(canvas)
        file = request.files["file"]
        file.save(os.path.join("./static/images/canvas/", str(canvasID) + ".png"))

        return jsonify(db.get_canvas(str(canvasID)))
    else:
        return


# getAllCanvases
@app.route("/amble/canvases")
def getCanvases():
    return jsonify(db.get_canvases())


# get a single canvas
@app.route("/amble/canvas/<string:canvasID>", methods=["GET", "PUT"])
def getCanvas(canvasID):
    if request.method == "GET":
        return jsonify(db.get_canvas(canvasID))
    elif request.method == "PUT":
        jason = request.form["json"]


# get or update canvas image by put
@app.route("/amble/canvas/image/<string:canvasID>", methods=["GET", "PUT"])
def getCanvasImage(canvasID):
    if request.method == "GET":
        render = render_template("image.html", name=(canvasID + ".png"))

        return render
    elif request.method == "PUT":
        file = request.files["file"]
        file.save(os.path.join("./static/images/canvas", canvasID + ".png"))
        return jsonify({"result": "success"})


# ========== COMMENTS ==========

# ========== MISC ==========
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r


# ========== STARTUP ==========
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

