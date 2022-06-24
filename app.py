import datetime
import socket
import threading

this_username = []


def app():
    choice = int(input("1.friends 2.invite 3.invitations 4.messages 5.block 6.search 7.del account"))
    while choice < 1 or choice > 7:
        choice = input("Enter valid number")
    if choice == 1:
        s.send(("friends#" + this_username[0]).encode())
        return
    if choice == 2:
        invited = input("Enter username:")
        s.send(("invite#" + this_username[0] + "#" + invited).encode())
        return
    if choice == 3:
        s.send(("invitations#" + this_username[0]).encode())
        return
    if choice == 4:
        s.send(("messages#" + this_username[0]).encode())
        return
    if choice == 5:
        blocked = input("Enter Who U Wanna Block")
        s.send(("block#" + this_username[0] + "#" + blocked).encode())
        return
    if choice == 6:
        search = input("Enter Who U Wanna search")
        s.send(("search#" + this_username[0] + "#" + search).encode())
        return
    if choice == 7:
        s.send(("del#"+this_username[0]).encode())
        exit()


def print_friends(data):
    arr = data.split("#")
    friends = eval(arr[1])
    cnt = 1
    for i in friends:
        print(str(cnt) + ")" + str(i[0]))
        cnt += 1
    print(str(cnt) + ")main menu")
    n = int(input())
    if n == cnt:
        app()
        return
    msg = input("write your message for " + friends[n - 1][0] + ":")
    s.send(("sendmessage#" + this_username[0] + "#" + friends[n - 1][0] + "#" + msg).encode())
    app()

def print_invitations(data):
    arr = data.split("#")
    invitations = eval(arr[1])
    cnt = 1
    for i in invitations:
        print(str(cnt) + ")" + str(i[0]))
        cnt += 1
    print(str(cnt) + ")main menu")
    n = int(input())
    if n == cnt:
        app()
        return
    s.send(("acceptinvite#"+invitations[n-1][0]+"#"+this_username[0]).encode())
    app()


def show_messages(data):
    arr = data.split("#")
    messages = eval(arr[1])
    cnt = 1
    for i in messages:
        if i[4] == "0":
            if i[6] == 1:
                print(str(cnt) + ")" + str(i[5]) + "--------" + str(i[2]) +" to "+ str(i[3])+ ":" + str(i[1])+" (seen)")
                cnt += 1
            else:
                print(str(cnt) + ")" + str(i[5]) + "--------" + str(i[2]) + " to " + str(i[3]) + ":" + str(
                    i[1]))
                cnt += 1
        else:
            if not i[6] == 1:
                print(str(cnt) + ")" + str(i[5]) + "--------" + str(i[2]) +" to "+ str(i[3])+ ":" + str(i[1])+"(liked)")
                cnt += 1
            else:
                print(str(cnt) + ")" + str(i[5]) + "--------" + str(i[2]) + " to " + str(i[3]) + ":" + str(
                    i[1]) + "(liked)(seen)")
                cnt += 1
    print(str(cnt) + ")main menu")
    n = int(input())

    if n == cnt:
        app()
    else:
        if messages[n-1][2] != this_username[0]:
            s.send(("likemessage#"+str(messages[n-1][0])).encode())
        app()
        return


def show_question(data):
    arr = data.split("#")
    answer = input(arr[1])
    s.send(answer.encode())
    return


def show_pass(data):
    arr = data.split("#")
    print(arr[1])
    main_menu()
    return


def penalty():
    print("3 failed attempts \n you can login in 3 days after "+str(datetime.datetime.now()))


def print_block(data):
    arr = data.split("#")
    print("user "+arr[1]+" blocked")
    app()
    return

def print_unblock(data):
    arr = data.split("#")
    print("user "+arr[1]+" unblocked")
    app()
    return


def search(data):
    arr = data.split("#")
    res = eval(arr[1])
    for i in res:
        print(i[0])
    app()
    return

def receiver(connection):
    while True:
        data = connection.recv(1024).decode()
        arr = data.split("#")
        if arr[0] == "signupfailed":
            print("choose unique username")
            sign_up()
        elif arr[0] == "signupsuccessful":
            print("sign up successful!")
            main_menu()
        elif arr[0] == "signinsuccessful":
            print("sign in successful!")
            app()
        elif arr[0] == "signinfailed":
            print("sign in failed!")
            main_menu()
        elif arr[0] == "friends":
            print_friends(data)
        elif arr[0] == "inviteresult":
            print(arr[1])
            app()
        elif arr[0] == "sendinvitations":
            print_invitations(data)
        elif arr[0] == "showmessages":
            show_messages(data)
        elif arr[0] == "question":
            show_question(data)
        elif arr[0] == "showpass":
            show_pass(data)
        elif arr[0] == "penalty":
            penalty()
        elif arr[0] == "blocked":
            print_block(data)
        elif arr[0] == "unblocked":
            print_unblock(data)
        elif arr[0] == "search":
            search(data)

def sign_in():
    username = input("Enter username:")
    if len(this_username) == 0:
        this_username.append(username)
    else:
        this_username[0] = username
    password = input("Enter password:")
    s.send(("signin#" + str(username) + "#" + str(password)).encode())


def sign_up():
    fullname = input("Enter fullname:")
    username = input("Enter username:")
    password = input("Enter password:")
    email = input("Enter email:")
    phone = input("Enter phone:")
    question = input("Enter security question:")
    ans = input("Enter its answer:")
    while not (email.__contains__("@")):
        email = input("enter valid email!!!:")
    while not any(c.isalpha() for c in password):
        password = input("password should contain at least one character:")
    while not phone.isnumeric():
        phone = input("Enter valid phone number")
    s.send((
                       "signup#" + fullname + "#" + username + "#" + password + "#" + email + "#" + phone + "#" + question + "#" + ans).encode())


def forgot_password():
    user = input("Enter Username:")
    s.send(("forget#" + user).encode())
    return


def main_menu():
    sign = input("wanna 1.sign in or 2.sign up or 3.forgot password?")
    while not (sign == "1" or sign == "2" or sign == "3"):
        sign = input("wanna 1.sign in or 2.sign up or 3.forgot password?")
    if sign == "1":
        sign_in()
    elif sign == "2":
        sign_up()
    elif sign == "3":
        forgot_password()


if __name__ == '__main__':
    s = socket.socket()
    port = 8585
    s.connect(('localhost', port))
    threading.Thread(target=receiver, args=(s,)).start()
    main_menu()
