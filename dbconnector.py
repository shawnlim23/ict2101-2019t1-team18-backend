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
def register(user):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "INSERT INTO `user`(`email`, `password`, `salt`, `name`, `age`, `sex`, `commute_method`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            result = cursor.execute(
                sql,
                (
                    user.email,
                    user.password,
                    user.salt,
                    user.name,
                    user.age,
                    user.sex,
                    user.commute_method,
                ),
            )
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
                sql = "UPDATE user SET token = NULL WHERE userID = %s"
                cursor.execute(sql, (userID))  # set result to True
                conn.commit()
                result = True
        finally:
            conn.close()
    else:
        result = False
    return result


# ========== MISCELANEOUS ==========
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
            print("test")
            result = cursor.lastrowid
            print(result)
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
    finally:
        conn.close()
        return canvas


def get_canvases_by_landmark(placeID):
    try:
        conn = conn_open()
        canvases = []
        with conn.cursor() as cursor:
            sql = "SELECT canvasID FROM activeCanvases WHERE placeID = %s;"
            if cursor.execute(sql,(placeID)) != 0:
                result = cursor.fetchall()
                for row in result:
                    canvases.append(row["canvasID"])

    finally:
        conn.close()
        return canvases


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
    print(userID)
    print(token)
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT token FROM user WHERE userID = %s"
            # If uID exists -> get token of uID
            if cursor.execute(sql, (userID)) == 1:
                server_token = cursor.fetchone()
                print(server_token)
                # if token == server_token or NULL -> return True
                if token == server_token["token"] or server_token["token"] == None:
                    result = True
    finally:
        conn.close()
        return result


if __name__ == "__main__":
    pass
    #print(get_salt("weh"))
    #print(get_canvases_by_landmark(1))


    # print(get_users())
    # print(get_salt("uwu@owo.com"))
    # print(check_email("owo@uwu.com"))
    # user = classes.User("uwu@uwu.com", "owau")
    # register(user)
    # try:
    #    conn = conn_open()
    #    with conn.cursor() as cursor:
    #        sql = "SELECT * FROM activeUsers WHERE userID = %s;"
    #        cursor.execute(sql, (6))
    #        user = cursor.fetchone()
    # finally:
    #    conn.close()
    #    print(user)
