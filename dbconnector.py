import os
import configparser
import pymysql.cursors
import logging
import classes

creds = {"host": "localhost", "user": "root", "password": "password", "db": "db"}
dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.isfile(dir_path + "\\creds.ini"):
    config = configparser.ConfigParser()
    config.read("creds.ini")
    creds = config["CREDENTIALS"]
else:
    logging.warning("No creds.ini detected. Using Default. (ask from Amin)")

# CONNECTION STUFF
def conn_open():
    connection = pymysql.connect(
        host=creds["host"],
        user=creds["user"],
        password=creds["password"],
        db=creds["db"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


# ========== AUTHENTICATION ==========
def register(user, verify_token):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "INSERT INTO `user`(`email`, `password`, `salt`, `name`, `birthdate`, `sex`, `commute_method`, `temp_token`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(
                sql,
                (
                    user.email,
                    user.password,
                    user.salt,
                    user.name,
                    user.birthdate,
                    user.sex,
                    user.commute_method,
                    verify_token,
                ),
            )
            result = cursor.lastrowid
    finally:
        conn.commit()
        conn.close()
        return result


def login(userID, token):
    try:
        user = {}
        if add_token(userID, token):
            user = get_user(userID)
    finally:
        return user


def logout(uidtoken):
    if check_token(uidtoken):
        try:

            userID = uidtoken.split("/")[0]
            conn = conn_open()
            with conn.cursor() as cursor:
                sql = "UPDATE user SET token = NULL WHERE userID = %s;"
                cursor.execute(sql, (userID))  # set result to True
                conn.commit()
                result = True
        finally:
            conn.close()
    else:
        result = False
    return result


# ========== LOGIN ==========
def check_email_exists(email):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT count(userID) AS count FROM user WHERE active = true AND email = %s"
            cursor.execute(sql, (email))
            result = cursor.fetchone()
            number = result["count"]
    finally:
        conn.close()
        return number


def get_salt(email):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT salt, password, userID FROM user WHERE email = %s AND active = 1;"
            cursor.execute(sql, (email))
            salt = cursor.fetchone()

    finally:
        conn.close()
        return salt


# ========== USERS ==========
def check_user_exists(userID):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT count(userID) AS count FROM activeUsers WHERE userID = %s"
            cursor.execute(sql, (userID))
            result = cursor.fetchone()
            number = result["count"]
    finally:
        conn.close()
        return number


def get_users():
    try:
        conn = conn_open()
        users = {}
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeUsers;"
            if cursor.execute(sql) != 0:
                users = cursor.fetchall()
    finally:
        conn.close()
        return users


def get_user(userID):
    try:
        conn = conn_open()
        user = {}
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeUsers WHERE userID = %s;"
            if cursor.execute(sql, (userID)) != 0:
                user = cursor.fetchone()
    finally:
        conn.close()
        return user


def get_user_by_email(email):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT userID FROM user WHERE email = %s AND active = 1;"
            cursor.execute(sql, (email))
            userID = cursor.fetchone()

    finally:
        conn.close()
        return userID


def update_user(user):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE `user` SET `birthdate` = %s, `commute_method` = %s, `name` = %s, `sex` = %s, `active` = %s WHERE `userID` = %s;"
            result = cursor.execute(
                sql,
                (
                    user["birthdate"],
                    user["commute_method"],
                    user["name"],
                    user["sex"],
                    user["active"],
                    user["userID"],
                ),
            )
    finally:
        conn.commit()
        conn.close()
        return result


def update_password(userID, password, salt):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE `user` SET `password` = %s, `salt` = %s, `temp_token` = NULL, WHERE `userID` = %s;"
            result = cursor.execute(sql, (password, salt, userID))
    finally:
        conn.commit()
        conn.close()
        return result


def check_verify_token(token):
    try:
        result = False
        userID, s_token = token.split("/")
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT count(userID) AS count FROM user WHERE userID = %s AND temp_token = %s;"
            cursor.execute(sql, (userID, s_token))
            count = cursor.fetchone()
            if count["count"] >= 0:
                result = True
    finally:
        conn.commit()
        conn.close()
        return result


def update_temp_token(userID, token):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE `user` SET `temp_token` = %s, WHERE `userID` = %s;"
            result = cursor.execute(sql, (token, userID))
    finally:
        conn.commit()
        conn.close()
        return result


def verify_user(userID):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE user SET temp_token = NULL, verified = 1 WHERE userID = %s"
            cursor.execute(sql, (userID))
    finally:
        conn.commit()
        conn.close()


def check_verified(userID):
    try:
        result = False
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT verified FROM user WHERE userID = %s"
            if cursor.execute(sql, (userID)) >= 0:
                result = True
    finally:
        conn.commit()
        conn.close()
        return result


# ========== LANDMARKS ==========
def check_landmark_exists(placeID):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = (
                "SELECT count(placeID) AS count FROM activeLandmarks WHERE placeID = %s"
            )
            cursor.execute(sql, (placeID))
            result = cursor.fetchone()
            number = result["count"]
    finally:
        conn.close()
        return number


def get_landmark(placeID):
    try:
        conn = conn_open()
        landmark = {}
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeLandmarks WHERE placeID = %s;"
            if cursor.execute(sql, (placeID)) != 0:
                landmark = cursor.fetchone()
    finally:
        conn.close()
        return landmark


def create_landmark(landmark):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "INSERT INTO `landmark`(`placeID`, `name`, `description`) VALUES (%s, %s, %s);"
            result = cursor.execute(
                sql, (landmark.placeID, landmark.name, landmark.description)
            )
    finally:
        conn.commit()
        conn.close()
        return result


# ========== CANVAS ==========
def check_canvas_exists(canvasID):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT count(canvasID) AS count FROM activeCanvases WHERE canvasID = %s"
            cursor.execute(sql, (canvasID))
            result = cursor.fetchone()
            number = result["count"]
    finally:
        conn.close()
        return number


def create_canvas(canvas):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "INSERT INTO `canvas`(`userID`, `placeID`, `title`, `description`, `editable`) VALUES (%s, %s, %s, %s, %s);"
            cursor.execute(
                sql,
                (
                    canvas.userID,
                    canvas.placeID,
                    canvas.title,
                    canvas.description,
                    canvas.editable,
                ),
            )
            result = cursor.lastrowid
    finally:
        conn.commit()
        conn.close()
        return result


def get_canvases():
    try:
        conn = conn_open()
        canvases = {}
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeCanvases;"
            if cursor.execute(sql) != 0:
                canvases = cursor.fetchall()
                for canvas in canvases:
                    canvas["rating"] = get_canvas_rating(canvas["canvasID"])["rating"]
    finally:
        conn.close()
        return canvases


def get_canvas(canvasID):
    try:
        conn = conn_open()
        canvas = {}
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeCanvases WHERE canvasID = %s;"
            if cursor.execute(sql, (canvasID)) != 0:
                canvas = cursor.fetchone()
                canvas["rating"] = get_canvas_rating(canvas["canvasID"])["rating"]
    finally:
        conn.close()
        return canvas


def get_canvases_by_landmark(placeID):
    try:
        conn = conn_open()
        canvases = []
        with conn.cursor() as cursor:
            sql = "SELECT canvasID FROM activeCanvases WHERE placeID = %s;"
            if cursor.execute(sql, (placeID)) != 0:
                result = cursor.fetchall()
                for row in result:
                    canvases.append(row["canvasID"])

    finally:
        conn.close()
        return canvases


def get_canvases_by_user(userID):
    try:
        conn = conn_open()
        canvases = []
        with conn.cursor() as cursor:
            sql = "SELECT canvasID FROM activeCanvases WHERE userID = %s;"
            if cursor.execute(sql, (userID)) != 0:
                result = cursor.fetchall()
                for row in result:
                    canvases.append(row["canvasID"])

    finally:
        conn.close()
        return canvases


def update_canvas(canvas):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE `canvas` SET `title` = %s, `description` = %s, `editable` = %s WHERE `canvasID` = %s;"
            result = cursor.execute(
                sql,
                (
                    canvas["title"],
                    canvas["description"],
                    canvas["editable"],
                    canvas["canvasID"],
                ),
            )
    finally:
        conn.commit()
        conn.close()
        return result


# ========== CANVAS RATING ==========
def get_canvas_rating(canvasID):
    try:
        result = -1
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT rating FROM countRating WHERE canvasID = %s;"
            if cursor.execute(sql, (canvasID)) != 0:
                result = cursor.fetchone()
    finally:
        conn.close()
        return result


def check_rated(canvasID, userID):
    try:
        conn = conn_open()
        result = -1
        with conn.cursor() as cursor:
            sql = "SELECT liked FROM canvas_rating WHERE canvasID = %s AND userID = %s;"
            if cursor.execute(sql, (canvasID, userID)) != 0:
                res = cursor.fetchone()
                result = res["liked"]
    finally:
        conn.close()
        return result


def rate(canvasID, userID):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            rated = check_rated(canvasID, userID)
            if rated == -1:
                sql = (
                    "INSERT INTO `canvas_rating`(`canvasID`, `userID`) VALUES (%s, %s);"
                )
                cursor.execute(sql, (canvasID, userID))

            else:
                if rated == 1:
                    sql = "UPDATE `canvas_rating` SET `liked` = %s WHERE `canvasID` = %s AND `userID` = %s"
                    cursor.execute(sql, (0, canvasID, userID))
                else:
                    sql = "UPDATE `canvas_rating` SET `liked` = %s WHERE `canvasID` = %s AND `userID` = %s"
                    cursor.execute(sql, (1, canvasID, userID))
    finally:
        conn.commit()
        conn.close()


# ========== COMMENTS ==========
def create_comment(comment):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "INSERT INTO `comment`(`userID`, `canvasID`, `text`, `timestamp`) VALUES (%s, %s, %s, %s);"
            cursor.execute(
                sql, (comment.userID, comment.canvasID, comment.text, comment.timestamp)
            )
            result = cursor.lastrowid
    finally:
        conn.commit()
        conn.close()
        return result


def get_comment(commentID):
    try:
        conn = conn_open()
        comment = {}
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeComments WHERE commentID = %s;"
            if cursor.execute(sql, (commentID)) != 0:
                comment = cursor.fetchone()
    finally:
        conn.close()
        return comment


def update_comment(comment):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE `comment` SET `text` = %s, `timestamp` = %s, `active` = %s WHERE `commentID` = %s;"
            result = cursor.execute(
                sql,
                (
                    comment["text"],
                    comment["timestamp"],
                    comment["active"],
                    comment["commentID"],
                ),
            )
    finally:
        conn.commit()
        conn.close()
        return result


# ========== TOKENS ==========
def add_token(userID, token):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "UPDATE user SET token = %s WHERE userID = %s"
            result = cursor.execute(sql, (token, userID))
            conn.commit()
    finally:
        conn.close()
        return result


def check_token(uidtoken):
    result = False
    userID, token = uidtoken.split("/")
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT token FROM user WHERE userID = %s"
            # If uID exists -> get token of uID
            if cursor.execute(sql, (userID)) == 1:
                server_token = cursor.fetchone()
                # if token == server_token or NULL -> return True
                if token == server_token["token"] or server_token["token"] == None:
                    result = True
    finally:
        conn.close()
        return result


if __name__ == "__main__":
    # print(get_canvas_rating(1))
    # rate(1, 1)
    # print(get_canvases())
    # print(check_rated(1,1))

    # canvas = get_canvas(1)
    # update_canvas(canvas)
    pass
