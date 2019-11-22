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
    result = {"result": "error", "error": ""}
    if request.method == "POST":

        # ensure json has been posted
        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

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

        # Create User & add optional fields
        user = classes.User(email, password, salt)
        if "name" in jason:
            user.name = jason["name"]

        if "birthdate" in jason:
            user.birthdate = jason["birthdate"]

        if "sex" in jason:
            user.sex = jason["sex"]

        if "commute_method" in jason:
            user.commute_method = jason["commute_method"]

        # Register User & submit
        db.register(user)
        result = {"result": "success"}
        return jsonify(result)

    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


# Login
@app.route("/amble/auth/login", methods=["POST"])
def login():
    result = {"result": "error", "error": ""}
    # Require Post method
    if request.method == "POST":
        # Require json
        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        # Get email from
        if "email" not in jason:
            result["error"] = "no email in json"
            return jsonify(result)
        email = jason["email"]

        # password stuff
        if "password" not in jason:
            result["error"] = "no password in json"
            return jsonify(result)
        pwd = jason["password"]

        deets = db.get_salt(email)  # get user's details from email
        if deets == None:  # if returns None means no user exists
            result["error"] = "incorrect email/password"
            return jsonify(result)
        # convert password to hash
        password = hashlib.sha256((pwd + deets["salt"]).encode("utf-8")).hexdigest()

        # return if hashedpassword doesn't match stored hash
        if password != deets["password"]:
            result["error"] = "incorrect email/password"
            return jsonify(result)

        # generate token and return user w/ token
        token = hashlib.sha256(
            datetime.now().strftime("%Y-%b-%a %H:%M:%S").encode("utf-8")
        ).hexdigest()

        user = db.login(deets["userID"], token)
        user["token"] = str(deets["userID"]) + "/" + token
        return jsonify({"result": "success", "return": user})

    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


# logout
@app.route("/amble/auth/logout", methods=["POST"])
def logout():
    result = {"result": "error", "error": ""}
    if request.method == "POST":

        # return json error
        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        # return if json doesn't exist
        if "token" not in jason:
            result["error"] = "no token in json"
            return jsonify(result)
        token = jason["token"]
        # return result based on if token matches the stored token
        if db.logout(token):
            return jsonify({"result": "success"})
        else:
            result["error"] = "invalid token"
            return jsonify(result)
    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


# ========== USERS ==========

# get all users
@app.route("/amble/users")
def getUsers():
    return jsonify(db.get_users())


# get one user
@app.route("/amble/user/<string:uID>", methods=["GET", "PUT"])
def getUser(uID):
    result = {"result": "error", "error": ""}
    if request.method == "GET":
        return jsonify(db.get_user(uID))

    elif request.method == "PUT":
        user = db.get_user(uID)
        if user == {}:
            result["error"] = "invalid userID"
            return jsonify(result)

        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        # update the dict with latest information
        if "birthdate" in jason:
            user["birthdate"] = jason["birthdate"]

        if "commute_method" in jason:
            user["commute_method"] = jason["commute_method"]

        if "name" in jason:
            user["name"] = jason["name"]

        if "sex" in jason:
            user["sex"] = jason["sex"]
        # update the stored database with userdata
        db.update_user(user)
        return jsonify(db.get_user(uID))

    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


@app.route("/amble/user/<string:userID>/canvases", methods=["GET"])
def getUserCanvases(userID):
    return jsonify({"canvases": db.get_canvases_by_user(userID)})


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


@app.route("/amble/landmark/<string:placeID>/canvases")
def getLandmarkCanvases(placeID):
    return jsonify({"canvases": db.get_canvases_by_landmark(placeID)})


# ========== CANVASES ==========

# Create Canvas
@app.route("/amble/canvas/createCanvas", methods=["POST"])
def createCanvas():
    result = {"result": "error", "error": ""}
    if request.method == "POST":

        # ensure json has been posted
        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

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

        # check if file is in requests
        if "file" not in request.files:
            result["error"] = "invalid file"
            return jsonify(result)

        # create canvas and add optional args
        canvas = classes.Canvas(userID, placeID)
        if "title" in jason:
            canvas.title = jason["title"]

        if "description" in jason:
            canvas.description = jason["description"]

        if "editable" in jason:
            canvas.editable = jason["editable"]

        canvasID = db.create_canvas(canvas)
        file = request.files["file"]
        file.save(os.path.join("./static/images/canvas/", str(canvasID) + ".png"))

        return jsonify(db.get_canvas(str(canvasID)))
    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


# getAllCanvases
@app.route("/amble/canvases")
def getCanvases():
    return jsonify(db.get_canvases())


# get a single canvas
@app.route("/amble/canvas/<string:canvasID>", methods=["GET", "PUT"])
def getCanvas(canvasID):
    result = {"result": "error", "error": ""}
    if request.method == "GET":
        return jsonify(db.get_canvas(canvasID))
    elif request.method == "PUT":

        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        canvas = db.get_canvas(canvasID)

        if "title" in jason:
            canvas["title"] = jason["title"]

        if "description" in jason:
            canvas["description"] = jason["description"]

        if "editable" in jason:
            canvas["editable"] = jason["editable"]

    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


# get or update canvas image by put
@app.route("/amble/canvas/image/<string:canvasID>", methods=["GET", "PUT"])
def getCanvasImage(canvasID):
    result = {"result": "error", "error": ""}
    if request.method == "GET":
        render = render_template("image.html", name=(canvasID + ".png"))

        return render
    elif request.method == "PUT":
        file = request.files["file"]
        file.save(os.path.join("./static/images/canvas", canvasID + ".png"))
        return jsonify({"result": "success"})
    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


# ========== CANVAS RATING ==========
@app.route("/amble/canvas/rate", methods=["PUT"])
def rateCanvas():
    result = {"result": "error", "error": ""}
    if request.method == "PUT":
        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        if "canvasID" not in jason:
            result["error"] = "no canvasID in json"
            return jsonify(result)
        canvasID = jason["canvasID"]

        if "userID" not in jason:
            result["error"] = "no userID in json"
            return jsonify(result)
        userID = jason["userID"]

        db.rate(canvasID, userID)
        return {"result": "success"}
    else:
        jason["error"] = "invalid access method"
        return jsonify(result)


@app.route("/amble/canvas/<string:canvasID>/rating")
def getCanvasRating(canvasID):
    return jsonify(db.get_canvas_rating(canvasID))


@app.route("/amble/canvas/<string:canvasID>/<string:userID>")
def getCanvasUser(canvasID, userID):
    rated = db.check_rated(canvasID, userID)
    if rated == 1:
        return jsonify({"liked": True})
    else:
        return jsonify({"liked": False})
    return jsonify(db.get_canvas_rating(canvasID))


# ========== COMMENTS ==========
@app.route("/amble/comment/createComment", methods=["POST"])
def createComment():
    result = {"result": "error", "error": ""}
    if request.method == "POST":

        # ensure json has been posted
        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        # check if userID exists
        if not ("userID" in jason and db.check_user_exists(jason["userID"])):
            result["error"] = "invalid userID"
            return jsonify(result)
        userID = str(jason["userID"])

        # check if canvasID is in json and canvas exists
        if not ("canvasID" in jason and db.check_canvas_exists(jason["canvasID"])):
            result["error"] = "invalid canvasID"
            return jsonify(result)
        canvasID = jason["canvasID"]

        comment = classes.Comment(userID, canvasID)
        if "text" in jason:
            comment.text = jason["text"]

        if "timestamp" in jason:
            comment.timestamp = jason["timestamp"]

        commentID = db.create_comment(comment)

        return jsonify(db.get_comment(commentID))


@app.route("/amble/comment/<string:commentID>", methods=["GET", "PUT"])
def getComment(commentID):
    result = {"result": "error", "error": ""}
    if request.method == "GET":
        return jsonify(db.get_comment(commentID))

    elif request.method == "PUT":
        comment = db.get_comment(commentID)
        if comment == {}:
            result["error"] = "invalid commentID"
            return jsonify(result)

        if request.json is not None:
            jason = request.json
        elif "json" in request.form:
            jason = json.loads(request.form["json"])
        else:
            result["error"] = "no json in request"
            return jsonify(result)

        # update thr dict with latest information
        if "text" in jason:
            comment["text"] = jason["text"]

        if "timestamp" in jason:
            comment["timestamp"] = jason["timestamp"]

        comment["active"] = True
        if "active" in jason:
            comment["active"] = jason["active"]
        # update the stored database with commentdata
        db.update_comment(comment)
        return jsonify(db.get_comment(commentID))

    else:
        result["error"] = "incorrect request method"
        return jsonify(result)


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


@app.before_request
def before_req():
    if request.method == "POST" or request.method == "PUT":
        if request.json is not None:
            print(request.json)
        else:
            print(request.form)


# ========== STARTUP ==========
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

