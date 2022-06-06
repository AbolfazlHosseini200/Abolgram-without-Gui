import socket
import threading

this_username = []


def app():
    choice = int(input("1.friends 2.invite 3.invitations 4.messages"))
    while choice < 1 or choice > 4:
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


def show_messages(data):
    arr = data.split("#")
    messages = eval(arr[1])
    cnt = 1
    for i in messages:
        print(str(cnt) + ")" + str(i[5]) + "--------" + str(i[2]) + ":" + str(i[1]))
        cnt += 1
    print(str(cnt) + ")main menu")
    n = int(input())
    if n == cnt:
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
        elif arr[0] == "sendinvitations":
            print_invitations(data)
        elif arr[0] == "showmessages":
            show_messages(data)
        elif arr[0] == "question":
            show_question(data)
        elif arr[0] == "showpass":
            show_pass(data)


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
    s.send((
                       "signup#" + fullname + "#" + username + "#" + password + "#" + email + "#" + phone + "#" + question + "#" + ans).encode())


def forgot_password():
    user = input("Enter Username:")
    s.send(("forget#" + user).encode())
    return


def main_menu():
    sign = input("wanna 1.sign in or 2.sign up or 3.forgot password?")
    while not (sign == "1" or sign == "2" or sign == "3"):
        sign = input("wanna 1.sign in or 2.sign up?")
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
