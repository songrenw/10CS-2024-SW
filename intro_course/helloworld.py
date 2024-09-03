import random
import time

# Define Pokémon and moves
pokemon_list = [
    {'name': 'Bulbasaur', 'emoji': '🌱', 'moves': ['Tackle', 'Growl', 'Leech Seed', 'Vine Whip'], 'type': 'Grass'},
    {'name': 'Charmander', 'emoji': '🔥', 'moves': ['Scratch', 'Growl', 'Ember', 'Smokescreen'], 'type': 'Fire'},
    {'name': 'Squirtle', 'emoji': '💧', 'moves': ['Tackle', 'Tail Whip', 'Water Gun', 'Bubble'], 'type': 'Water'}
]

# Define moves and their damage
move_damage = {
    'Tackle': 10,
    'Scratch': 10,
    'Growl': 0,
    'Leech Seed': 0,
    'Vine Whip': 25,
    'Ember': 25,
    'Smokescreen': 0,
    'Tail Whip': 0,
    'Water Gun': 25,
    'Bubble': 10
}

# Define type effectiveness
type_effectiveness = {
    'Grass': {'Water': 2.0, 'Fire': 0.5, 'Grass': 1.0},
    'Fire': {'Grass': 2.0, 'Water': 0.5, 'Fire': 1.0},
    'Water': {'Fire': 2.0, 'Grass': 0.5, 'Water': 1.0}
}

# Function to simulate a battle
def battle(player_pokemon, opponent_pokemon):
    player_hp = 100
    opponent_hp = 100
    player_attack = 1.0
    player_defense = 1.0
    opponent_attack = 1.0
    opponent_defense = 1.0

    print(f"\nYou encountered a wild {opponent_pokemon['name']} {opponent_pokemon['emoji']}!")
    time.sleep(1)

    while player_hp > 0 and opponent_hp > 0:
        print(f"\nYour {player_pokemon['name']} {player_pokemon['emoji']}'s HP: {player_hp}")
        print(f"Wild {opponent_pokemon['name']} {opponent_pokemon['emoji']}'s HP: {opponent_hp}")

        print("\nChoose a move:")
        for i, move in enumerate(player_pokemon['moves']):
            print(f"{i + 1}. {move}")

        move_choice = int(input("\nEnter the number of your move: ")) - 1
        player_move = player_pokemon['moves'][move_choice]
        opponent_move = random.choice(opponent_pokemon['moves'])

        time.sleep(1)
        print(f"\n{player_pokemon['name']} {player_pokemon['emoji']} used {player_move}!")
        time.sleep(1)
        if move_damage[player_move] > 0:
            effectiveness = type_effectiveness[player_pokemon['type']][opponent_pokemon['type']]
            damage = move_damage[player_move] * effectiveness * player_attack / opponent_defense
            opponent_hp -= damage
            print(f"It dealt {damage:.2f} damage!")

        if player_move in ['Growl', 'Smokescreen', 'Tail Whip', 'Leech Seed']:
            opponent_attack = max(0.1, opponent_attack - 0.3)
            print(f"{opponent_pokemon['name']} {opponent_pokemon['emoji']}'s attack decreased!")

        if opponent_hp <= 0:
            print(f"The wild {opponent_pokemon['name']} {opponent_pokemon['emoji']} fainted!")
            return True

        time.sleep(1)
        print(f"The wild {opponent_pokemon['name']} {opponent_pokemon['emoji']} used {opponent_move}!")
        time.sleep(1)
        if move_damage[opponent_move] > 0:
            effectiveness = type_effectiveness[opponent_pokemon['type']][player_pokemon['type']]
            damage = move_damage[opponent_move] * effectiveness * opponent_attack / player_defense
            player_hp -= damage
            print(f"It dealt {damage:.2f} damage!")

        if opponent_move in ['Growl', 'Smokescreen', 'Tail Whip', 'Leech Seed']:
            player_attack = max(0.1, player_attack - 0.3)
            print(f"{player_pokemon['name']} {player_pokemon['emoji']}'s attack decreased!")

        if player_hp <= 0:
            print(f"Your {player_pokemon['name']} {player_pokemon['emoji']} fainted!")
            return False

# Main game loop
def play_game():
    while True:
        name = input("Enter Your name: ")
        print(f" {name}, Welcome to Pokémon! Choose your starter Pokémon:")
        for i, pokemon in enumerate(pokemon_list):
            print(f"{i + 1}. {pokemon['name']} {pokemon['emoji']}")

        starter_choice = int(input("\nEnter the number of your starter Pokémon: ")) - 1
        player_pokemon = pokemon_list[starter_choice]
        opponent_pokemon = random.choice(pokemon_list)

        won = battle(player_pokemon, opponent_pokemon)

        if won:
            print("\nCongratulations! You won the battle!")
        else:
            print("\nYou lost the battle. Better luck next time!")

        replay = input("\nDo you want to play again? (yes/no): ").lower()
        if replay != 'yes':
            break

# Start the game
play_game()

