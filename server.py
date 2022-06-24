import random
import socket
import string
import threading
import mysql.connector
import datetime

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
    my_cursor.execute(sql, (arr[1], arr[2], arr[3], arr[4], arr[5], 0, 1, str(datetime.datetime.now().date()),))
    mydb.commit()
    sql = "INSERT INTO securityquestion (question, username, answer) VALUES (%s, %s, %s); "
    my_cursor.execute(sql, (arr[6], arr[2], arr[7],))
    sql = "INSERT INTO loginattempts (username) VALUES (%s);"
    my_cursor.execute(sql, (arr[2],))
    mydb.commit()
    print("Done")
    sql = "INSERT INTO log(body,dates) VALUES(%s,%s)"
    my_cursor.execute(sql, (arr[2] + " signed up", datetime.datetime.now()))
    mydb.commit()


def sign_in(data, connection):
    arr = data.split("#")
    sql = "SELECT username FROM user WHERE username=%s AND password=%s"
    my_cursor.execute(sql, (arr[1], arr[2],))
    res = my_cursor.fetchall()
    sql = "SELECT failedattempts FROM loginattempts WHERE username = %s"
    my_cursor.execute(sql, (arr[1],))
    x = my_cursor.fetchall()
    num = int(x[0][0]) + 1
    if num > 3:
        sql = "SELECT endate FROM loginattempts WHERE username=%s"
        my_cursor.execute(sql, (arr[1],))
        enddate = my_cursor.fetchall()

        if datetime.datetime.now() > datetime.datetime.now() - enddate[0][0] + datetime.timedelta(days=3):
            connection.send("signinsuccessful".encode())
            sql = "UPDATE loginattempts SET failedattempts=%s WHERE username = %s AND date"
            my_cursor.execute(sql, (0, arr[1]))
            sql = "INSERT INTO log(body,dates) VALUES(%s,%s)"
            my_cursor.execute(sql, (arr[1] + " signed in", datetime.datetime.now()))
            mydb.commit()
            return

        connection.send("penalty#".encode())
        return
    if not (len(res) == 0):
        connection.send("signinsuccessful".encode())
        sql = "UPDATE loginattempts SET failedattempts=%s WHERE username = %s"
        my_cursor.execute(sql, (0, arr[1]))
        sql = "INSERT INTO log(body,dates) VALUES(%s,%s)"
        my_cursor.execute(sql, (arr[1] + " signed in", datetime.datetime.now()))
        mydb.commit()

    else:
        connection.send("signinfailed".encode())
        sql = "SELECT failedattempts FROM loginattempts WHERE username = %s"
        my_cursor.execute(sql, (arr[1],))
        x = my_cursor.fetchall()
        num = int(x[0][0]) + 1
        if num == 3:
            sql = "UPDATE loginattempts SET failedattempts=%s WHERE username = %s"
            my_cursor.execute(sql, (num, arr[1]))
            mydb.commit()
            sql = "UPDATE loginattempts SET endate=%s WHERE username = %s"
            my_cursor.execute(sql, (str(datetime.datetime.now()), arr[1]))
            mydb.commit()
        sql = "UPDATE loginattempts SET failedattempts=%s WHERE username = %s"
        my_cursor.execute(sql, (num, arr[1]))
        mydb.commit()


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
        get_random_string(40), arr[3], arr[1], str(arr[2]), str(0),
        str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),))
    mydb.commit()
    sql = "INSERT INTO log(body,dates) VALUES(%s ,%s)"
    my_cursor.execute(sql, (arr[1] + " sent message to " + arr[2], datetime.datetime.now()))
    mydb.commit()


def invite(data, connection):
    arr = data.split("#")
    sql = "SELECT * FROM user WHERE username=%s"
    my_cursor.execute(sql, (arr[2],))
    res = my_cursor.fetchall()
    if not (len(res) == 0):
        sql = "INSERT INTO invitations (inviter, invited, success) VALUES ( %s, %s, %s); "
        my_cursor.execute(sql, (arr[1], arr[2], 0,))
        mydb.commit()
        connection.send(("inviteresult#invite sent!").encode())
        return
    connection.send(("inviteresult#theres no such username!").encode())
    sql = "INSERT INTO log(body,dates) VALUES(%s,%s)"
    my_cursor.execute(sql, (arr[1] + " sent invite to" + arr[2], datetime.datetime.now()))
    mydb.commit()


def send_invitations(data, connection):
    arr = data.split("#")
    sql = "SELECT inviter FROM invitations WHERE invited=%s"
    my_cursor.execute(sql, (arr[1],))
    invitations = my_cursor.fetchall()
    connection.send(("sendinvitations#" + str(invitations)).encode())


def show_messages(data, connection):
    arr = data.split("#")
    sql = "SELECT * FROM message WHERE receiver=%s or sender=%s "
    my_cursor.execute(sql, (arr[1], arr[1],))
    messages = my_cursor.fetchall()
    sql = "SELECT blocked FROM block"
    my_cursor.execute(sql, ())
    blocked = my_cursor.fetchall()
    for i in messages:
        for j in blocked:
            if i[2] == j[0]:
                messages.remove(i)
    sql = "UPDATE message SET seen=1 WHERE receiver=%s "
    my_cursor.execute(sql, (arr[1],))
    mydb.commit()

    connection.send(("showmessages#" + str(messages)).encode())


def forgot_password(data, connection):
    arr = data.split("#")
    sql = "SELECT question FROM securityquestion WHERE username=%s"
    my_cursor.execute(sql, (arr[1],))
    question = my_cursor.fetchall()
    connection.send(("question#" + str(question[0][0])).encode())
    data = connection.recv(1024).decode()
    sql = "SELECT question FROM securityquestion WHERE username=%s AND answer=%s"
    my_cursor.execute(sql, (arr[1], data,))
    res = my_cursor.fetchall()
    if not (len(res) == 0):
        sql = "SELECT password FROM user WHERE username=%s"
        my_cursor.execute(sql, (arr[1],))
        passs = my_cursor.fetchall()
        connection.send(("showpass#" + "password:" + str(passs[0][0])).encode())
    else:
        connection.send("showpass#Wrong".encode())


def accept_invite(data, connection):
    arr = data.split("#")
    sql = "INSERT INTO friendship (user1, user2) VALUES ( %s, %s);"
    my_cursor.execute(sql, (arr[1], arr[2],))
    mydb.commit()
    sql = "DELETE FROM invitations WHERE inviter=%s AND invited=%s;"
    my_cursor.execute(sql, (arr[1], arr[2],))
    mydb.commit()


def like_message(data, connection):
    arr = data.split("#")
    sql = "UPDATE message SET likes =1 WHERE id=%s;"
    my_cursor.execute(sql, (arr[1],))
    mydb.commit()


def block(data, connection):
    arr = data.split("#")
    sql = "SELECT * FROM block WHERE blocker=%s AND blocked=%s;"
    my_cursor.execute(sql, (arr[1], arr[2],))
    temp = my_cursor.fetchall()
    if len(temp) == 0:
        sql = "INSERT INTO block(blocked,blocker) VALUES(%s,%s);"
        my_cursor.execute(sql, (arr[2], arr[1],))
        mydb.commit()
        connection.send(("blocked#" + arr[2]).encode())
    else:
        sql = "DELETE FROM block WHERE blocked=%s AND blocker=%s"
        my_cursor.execute(sql, (arr[2], arr[1],))
        mydb.commit()
        connection.send(("unblocked#" + arr[2]).encode())


def search(data, connection):
    arr = data.split("#")
    sql = "SELECT username FROM user WHERE username LIKE '%%%s'"
    my_cursor.execute(sql, (arr[2],))
    res = my_cursor.fetchall()
    print(res)
    connection.send(("search#" + str(res)).encode())


def delete(data, connection):
    arr = data.split("#")
    sql = "DELETE FROM user WHERE username = %s"
    my_cursor.execute(sql, (arr[1],))
    mydb.commit()
    sql = "INSERT INTO log (body,dates) VALUES (%s,%s)"
    my_cursor.execute(sql, (arr[1] + " deleted account", datetime.datetime.now(),))
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
        if arr[0] == "invite":
            invite(data, connection)
        if arr[0] == "invitations":
            send_invitations(data, connection)
        if arr[0] == "messages":
            show_messages(data, connection)
        if arr[0] == "forget":
            forgot_password(data, connection)
        if arr[0] == "acceptinvite":
            accept_invite(data, connection)
        if arr[0] == "likemessage":
            like_message(data, connection)
        if arr[0] == "block":
            block(data, connection)
        if arr[0] == "search":
            search(data, connection)
        if arr[0] == "del":
            delete(data, connection)


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
