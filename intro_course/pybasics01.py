# variables
# variables are used to store data in a program.
# In Python, variables are created by assigning a value to a meaningful name.
# the value of a variable can be changed or updated throughtout the program.
# Variables contrain one type of data at a time, but the data type can change.
# Data types in Python include integers, floats, strings and booleans

''' #this commented out code
name = "Fred" # this variable contains a string (text)
age = 15 # this variable contrain an interger "int" which is a whole number
salary = 1000.50 # this variable contain a float "float", which is a decimal number
is_student = True # true or false statement
'''

name = input("Enter your name: ")
age = int(input("Enter your age: "))
salary = float(input("Enter your salary: "))
is_student = bool(input("Are you a student? (True or False):"))

print(type(name))
print(type(age))
print(type(salary))
print(type(is_student))
print("Name: ", name)
if is_student == True: #if statement, check if is_student is true and run the indent code
    student = "Yes"
else:
    student = "No"
# F-string
print(f"{name} is {age} years old and earns $ {salary} per month. Is he a student? {is_student}")
# Fred is 15 years old and earns $ 1000.5 per month. Is he a student? True
print(f"{name} is {age} years old and earns ${salary} per month. Is he a student? {student}")