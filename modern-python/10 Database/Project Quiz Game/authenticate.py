from account import *

def signup():
    print('========Choose Your Details=========')
    name=input("Choose Username: ")
    if isNameExist(name)== True:
        print("Username Exist")
        signup()
    pwd= input("Choose Password: ")
    if validPassword(pwd)== True:
        status= storeDetails(name,pwd)
        if status==True:
            print('Record Added Successfully')
        else:
            print('Error in Adding Record')
            signup()
    else:
        print('See password Instructions')
        signup()

def login():
    print('========Enter Your Details=========')
    name=input("Enter Username: ")
    if isNameExist(name)== True:
        pwd=input("Enter Password: ")
        if checkPassword(name,pwd)==True:
            return True
        else:
            print('Wrong password')
            login()
    else:
        print('Unknown Username')
        login()

    
