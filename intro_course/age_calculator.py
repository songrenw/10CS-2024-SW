import os #this provide function for interactive
import datetime
repeat = "yes"
while repeat == "yes":
    current_date = datetime.datetime.now()
    print(f"Today date is: {current_date.strftime('%a %Y/%m/%d')}")
    name = input("Enter your name: ").strip() # get user year
    birth_year = int(input("Enter your birth year: ").strip()) # get user birth_year
    birth_month = int(input("Enter your birth month: ").strip())
    birth_day = int(input("Enter your birth day: ").strip())
    age = current_date.year - birth_year - ((current_date.month, current_date.day) < (birth_month, birth_day))
    # add a python string method to convert the user's input to lowercase
    # https://www.w3schools.com/python/python_ref_string.asp
    # Hi name, you are age years old
    print(f"Hi {name}, you are {age} years old") # get user age by subtrating birth_year from 2024
    # ask if the user want to repeat
    repeat = input("Would you like to run the program again? (Yes/No): ").lower().strip()
    os.system('cls||clear')
# if repeat == "no": thank the user and exit program
print("Thank you for using the age calculator.")
