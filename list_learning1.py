import os

file_path = 'sports01.txt'

sports =[]
add = "yes"



def erase_sports(file_path):
    with open(file_path, 'w') as file:  # write the updated sport list back to the file
        file.write("")
def read_sports(file_path):# function
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return[]

def write_sports(file_path, sports):
    with open(file_path, 'w') as file:  # write the updated sport list back to the file
        for sport in sports:
            file.write(f"{sport}\n")

remove = input("Do you want to erase remove list? (yes/no): ").lower().strip()

if remove == "yes":
    erase_sports(file_path)
# 3 thing in function function, prenameter and intrucsion for the function a function consist a function and def name of a function, a function defeition always have a bracket so we can pass preminrter in to the function
while add == "yes":

    sports = read_sports(file_path)


    new_sport = input("Enter your favourite sport: ").capitalize().strip()

    if new_sport:
        if new_sport in sports: # nested if statment check if the sport entered by the user had already exist in the list
            print(f"{new_sport} is already in the list")
        else:
            sports.append(new_sport)  # update list
            print("Updated sports list: ", sports)
    else:
        print("No new sport added.")
        print("Sports list:", sports)

    write_sports(file_path, sports)

    for i, sport in enumerate(sports): # lopp through the sports list with index
        print(f"Sport {i+1}: {sport}") # Print the index and sport

    add = input("Do you want to add another sport? (yes/no): ").lower().strip()
print("Thanks for using sports list")