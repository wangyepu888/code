# 2020/9/29  Yepu Wang
'''
The account information of the three users is used as the data source, 
and the user information includes: ID, password, checking account 
and saving account. 
'''
bank_database= [
    {'id':'1000','user_password':'100001','checking_account': 1000, 'saving_account':1000},
    {'id':'2000','user_password':'200002','checking_account': 2000, 'saving_account':2000},
    {'id':'3000','user_password':'300003','checking_account': 3000, 'saving_account':3000}
    ]

#Function to verify login password matching
def login_user_check():
    global bank_database
    user_id=input('Please enter your id:')
    user_password=input('Please enter your passport:')
    for NewUser in range (len (bank_database)):
       if user_id== bank_database[NewUser]['id'] and user_password == bank_database[NewUser]['user_password']:
           print("You have logged in successfully.")
           return NewUser
       
    print('The password is wrong, please re-enter')
           

#Deposit function
def add_balance():
    global bank_database
    add_money=int(input('Please enter the deposit amount:'))
    bank_database[NewUser]['checking_account']+=add_money
    print('You have successfully deposited. Your current balance is: ')
    print(bank_database[NewUser]['checking_account'])

#Withdrawal function    
def draw_balance():
    global bank_database
    draw_money= int (input ('Please input the withdrawal amount：'))
    if bank_database[NewUser]['checking_account']>=draw_money:
        bank_database[NewUser]['checking_account']-=draw_money
        print('You have successfully withdrawn money. Your current balance is: ')
        print(bank_database[NewUser]['checking_account'])
    if bank_database[NewUser]['checking_account'] < draw_money:
        print('Your balance is not enough!')
      
#Transfer function     
def transfer():
    global bank_database
    Num=int(input('transfer money from checking account to saving account, press 1. Else please press 2.'))
    if Num==1:
        transfer_money=int(input('Please enter the transfer amount:'))
        bank_database[NewUser]['checking_account']-=transfer_money
        bank_database[NewUser]['saving_account']+=transfer_money
        print('Your checking_account is: ')
        print(bank_database[NewUser]['checking_account'])
        print('Your saving_account is:' )
        print(bank_database[NewUser]['saving_account'])
    elif Num==2:
        transfer_money=int(input('Please enter the transfer amount:'))
        bank_database[NewUser]['checking_account']+=transfer_money
        bank_database[NewUser]['saving_account']-=transfer_money
        print('Your checking_account is: ')
        print(bank_database[NewUser]['checking_account'])
        print('Your saving_account is:' )
        print(bank_database[NewUser]['saving_account'])
    else:
        print('You press a wrong number.')
       
#Exit the system        
def loginOut():
    user_choose=input('If you want to log out, please press 1.')
    while user_choose=='1':
        print('Successfully logged out. Please retrieve your card')
        break

#User interface function
def user_interface():
    print('1.deposit, 2.withdraw, 3.transfer, 4.quit')
    
while True:
    NewUser=login_user_check()
    if NewUser is None:
        continue
    while True:
        user_interface()
        user_key=input('Please press a number for the corresponding operation:')
        if user_key=='1':
            add_balance()
            print('Do you need to do additional transactions or not?')
        elif user_key=='2':
            draw_balance()
            print('Do you need to do additional transactions or not?')
        elif user_key=='3':
            transfer()
            print('Do you need to do additional transactions or not?')
        elif user_key=='4':
            loginOut()
            break
    break
        

    
    



    



        
      













   


   


