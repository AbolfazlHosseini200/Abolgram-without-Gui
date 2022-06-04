import random
import socket
import string
import threading
import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ABOlfazl8118",
    database="dbfinal"
)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def sign_up(data, con):
    arr = data.split("#")
    sql = "SELECT * FROM user WHERE username=%s"
    my_cursor.execute(sql, (arr[2],))
    res = my_cursor.fetchall()
    if not (len(res) == 0):
        con.send("signupfailed".encode())
        return
    else:
        con.send("signupsuccessful".encode())
    sql = "INSERT INTO user (fullname, username, password, email, phone, loggedin, active, date) VALUES (%s, %s, %s,%s, %s, %s, %s, %s); "
    my_cursor.execute(sql, (arr[1], arr[2], arr[3], arr[4], arr[5], 0, 1, str(datetime.now().date()),))
    mydb.commit()
    print("Done")


def sign_in(data, connection):
    arr = data.split("#")
    sql = "SELECT username FROM user WHERE username=%s AND password=%s"
    my_cursor.execute(sql, (arr[1], arr[2],))
    res = my_cursor.fetchall()
    if not (len(res) == 0):
        connection.send("signinsuccessful".encode())

    else:
        connection.send("signinfailed".encode())


def send_friends(data, connection):
    arr = data.split("#")
    sql = "SELECT user2 FROM friendship WHERE user1=%s"
    my_cursor.execute(sql, (arr[1],))
    friends = my_cursor.fetchall()
    sql = "SELECT user1 FROM friendship WHERE user2=%s"
    my_cursor.execute(sql, (arr[1],))
    friends2 = my_cursor.fetchall()
    friends3 = friends + friends2
    connection.send(("friends#" + str(friends3)).encode())


def send_message(data, connection):
    arr = data.split("#")
    sql = "INSERT INTO message (id, body, sender, receiver, likes, time) VALUES ( %s, %s, %s, %s, %s, %s); "
    my_cursor.execute(sql, (
        get_random_string(40), arr[3], arr[1], str(arr[2]), str(0), str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),))
    mydb.commit()


def handler(connection):
    while True:
        data = connection.recv(1024).decode()
        arr = data.split("#")
        if arr[0] == "signup":
            sign_up(data, connection)
        if arr[0] == "signin":
            sign_in(data, connection)
        if arr[0] == "friends":
            send_friends(data, connection)
        if arr[0] == "sendmessage":
            send_message(data, connection)


if __name__ == '__main__':
    my_cursor = mydb.cursor()
    s = socket.socket()
    print("Socket successfully created")
    port = 8585
    s.bind(('localhost', port))
    s.listen(5)
    print("socket is listening")
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        c.send('Thank you for connecting'.encode())
        threading.Thread(target=handler, args=(c,)).start()
