import socket
import threading

this_username=[]


def app():
    choice = int(input("1.friends 2.invite 3.invitations"))
    while choice < 1 or choice > 3:
        choice = input("Enter valid number")
    if choice == 1:
        s.send(("friends#" + this_username[0]).encode())


def print_friends(data):
    arr = data.split("#")
    friends = eval(arr[1])
    cnt = 1
    for i in friends:
        print(str(cnt) + ")"+str(i[0]))
        cnt += 1
    print(str(cnt)+")main menu")

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


def sign_in():
    username = input("Enter username:")
    this_username.append(username)
    password = input("Enter password:")
    s.send(("signin#" + str(username) + "#" + str(password)).encode())


def sign_up():
    fullname = input("Enter fullname:")
    username = input("Enter username:")
    password = input("Enter password:")
    email = input("Enter email:")
    phone = input("Enter phone:")
    while not (email.__contains__("@")):
        email = input("enter valid email!!!:")
    while not any(c.isalpha() for c in password):
        password = input("password should contain at least one character:")
    s.send(("signup#" + fullname + "#" + username + "#" + password + "#" + email + "#" + phone).encode())


def main_menu():
    sign = input("wanna 1.sign in or 2.sign up?")
    while not (sign == "1" or sign == "2"):
        sign = input("wanna 1.sign in or 2.sign up?")
    if sign == "1":
        sign_in()
    elif sign == "2":
        sign_up()


if __name__ == '__main__':
    s = socket.socket()
    port = 8585
    s.connect(('localhost', port))
    threading.Thread(target=receiver, args=(s,)).start()
    main_menu()
