import json
import hashlib as h
import random as r
import secrets as s

def Auth(UserID,Password):
    # we get userID and password as STRINGS
    Success=False
    SessionID='11-22-33-44'
    UserID=UserID.lower()
    
    with open("Users.json",'r') as U:
        DB=json.load(U)
    DB=DB["users"]
    if UserID not in DB:
        SessionID='Failed, User not in DB'
    else:
        passkey=DB[str(UserID)] 
        Salt=passkey['salt']
        salted=str(Salt+Password)
        salted=salted.encode()
        ActualP=h.sha256(salted).hexdigest()
        
        if passkey['hashed_password'] ==ActualP :
            Success=True
            SessionID=str(r.randint(10,99))+'-'+str(r.randint(10,99))+'-'+str(r.randint(10,99))+'-'+str(r.randint(10,99))
        else:
            Success=False
            SessionID='password Failed'


    return Success,SessionID


def Signup():
    salt=s.token_hex(8)
    with open("Users.json","r") as U:
        DB=json.load(U)
    DB=DB["users"]
    Username=input("Please Enter your desired username: ")
    while Username in DB:
        print("Sorry that username is taken \n Please select other username")
        Username=input("Please Enter your desired username: ")
    print("please enter your desired password")
    Password=input("The password should be 9 or more characters long and have atleast 1 Uppercase character,1 Number and 1 Special character ")
    

    c=4
    valid=False
    while c>0 :
        if (any(char.isupper() for char in Password)) and (any(char.isdigit() for char in Password)) and (any(not char.isalnum() for char in Password)) and (len(Password)>=9):
            valid=True
            break
        else:
            print("Please try again. {c} attempts remaining.")
            
            c-=1
            if c>0:
                Password= input("Try again)")
    if valid:
        Password=(salt+Password)
        Password=Password.encode()
        Password=h.sha256(Password).hexdigest()
        DB[str(Username)]={"salt":str(salt),"hashed_password":str(Password)}
        with open("Users.json","w") as U:
            master_dict = {"users": DB}
            json.dump(master_dict, U, indent=4)
    elif c==0:
        print("Please refresh and try again.")
    else:
        print("how u seing this bruh")


def Login():
    username=input("Please Enter your Username: ")
    Password=input("Please ender your Password: ")
    Reply=Auth(username,Password)
    if Reply[0] :
        print("Here is your Session ID: ",Reply[1])
    elif Reply[1]=='password Failed':
        print("Wrong Password")
    else:
        print("Couldnt find your UserName, Please Sign up")


def main():
    print(" Greetings, Please select Login or Signup \n 1)Login \n 2)Signup")
    choice = input("> ") # Get input as a string
    
    if choice == "1":
        Login()
    elif choice == "2":
        Signup()
    else:
        print("Invalid selection. Please run the program again.")
main()
    