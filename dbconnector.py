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


def check_email(email):
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeUsers WHERE email = %s;"
            number = cursor.execute(sql, (email))

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


def logout(uidtoken):
    if check_token(uidtoken):
        try:

            userID = uidtoken.split("/")[0]
            conn = conn_open()
            with conn.cursor() as cursor:
                sql = "UPDATE user SET token = NULL WHERE userID = %s"
                cursor.execute(sql, (userID))  # set result to True
                conn.commit()
                result = "Success"
        finally:
            conn.close()
    else:
        result = "Invalid Token"
    return result


def login(userID, token):
    try:
        user = {}
        if add_token(userID, token):
            user = get_user(userID)
    finally:
        return user


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


if __name__ == "__main__":
    # print(get_users())
    # print(get_salt("uwu@owo.com"))
    # print(check_email("owo@uwu.com"))
    # user = classes.User("uwu@uwu.com", "owau")
    # register(user)
    try:
        conn = conn_open()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM activeUsers WHERE userID = %s;"
            cursor.execute(sql, (6))
            user = cursor.fetchone()
    finally:
        conn.close()
        print(user)
