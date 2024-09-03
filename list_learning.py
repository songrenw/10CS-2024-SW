add = "yes"
sport = []
while add == "yes":
    '''
    sport = ["Basketball"]
    print(sport)
    print(type(sport))
    print(len(sport))
    print(sport[0])
    print(sport[-1])
    print(sport[-2])
    print(sport[0:3])
    
    for sports in sport: #'sports' is a variable that can be change
        print(type(sports))
        print(sports)
    '''

    new_sport = input("Enter your favourite sport: ")
    if new_sport:
        sport.append(new_sport) # update list
        print("Updated sports list: ", sport)
    else:
        print("No new sport added.")
        print("Sports list:", sport)

    for i, sports in enumerate(sport): # lopp through the sports list with index
        print(f"Sport {i+1}: {sports}") # Print the index and sport

    add = input("Do you want to add another sport? (yes/no): ").lower().strip()
print("Thanks for using sports list")
