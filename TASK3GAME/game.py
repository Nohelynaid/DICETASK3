from tabulate import tabulate
import sys
import hmac
import hashlib
import secrets

def get_dice():
    args = sys.argv[1:]
    if len(args) < 3:
        print("Error: You must enter at least 3 dice.")
        print("Example: 1,2,3,4,5,6 2,2,2,5,5,5 6,6,6,1,1,1")
        sys.exit(1)
    dice = []
    for arg in args:
        faces = [int(x) for x in arg.split(',') if x.strip() != '']
        if len(faces) != 6:
            print("Error: Each dice must have exactly 6 values.")
            sys.exit(1)
        dice.append(faces)
    return dice

def commit_number(number):
    secret = secrets.token_bytes(32)  # 256 bits key
    h = hmac.new(secret, str(number).encode(), hashlib.sha3_256).hexdigest()
    return secret, h

def reveal_commit(name, number, secret):
    print(f"{name} reveals: number = {number}, secret = {secret.hex()}")
    h = hmac.new(secret, str(number).encode(), hashlib.sha3_256).hexdigest()
    print(f"{name} HMAC check: {h}\n")

def coin_toss():
    print("\n=== COIN TOSS ===")
    comp_number = secrets.randbelow(2)
    comp_secret, comp_hmac = commit_number(comp_number)
    print(f"Computer HMAC: {comp_hmac}")

    while True:
        user_input = input("Your coin toss guess (0 or 1): ").strip()
        if user_input in ('0', '1'):
            user_guess = int(user_input)
            break
        print("Invalid input. Please enter 0 or 1.")

    input("Press Enter to reveal Computer's choice...")
    reveal_commit("Computer", comp_number, comp_secret)

    if user_guess == comp_number:
        print("You start!\n")
        return 0  # user first
    else:
        print("Computer starts.\n")
        return 1  # computer first

def pick_dice(dice, user=True, forbidden=None):
    role = "Your" if user else "Computer's"
    if not user:
        options = [i for i in range(len(dice)) if i != forbidden]
        comp_choice = secrets.choice(options)
        comp_secret, comp_hmac = commit_number(comp_choice)
        print(f"Computer commitment to dice choice HMAC: {comp_hmac}")
        return comp_choice, comp_secret
    else:
        while True:
            print(f"{role} turn to pick a dice:")
            for i, d in enumerate(dice):
                if forbidden is not None and i == forbidden:
                    continue
                print(f"{i} - {d}")
            print("? - Show win probabilities")
            print("X - Exit")
            choice = input("Pick: ").strip().upper()

            if choice == 'X':
                sys.exit(0)
            elif choice == '?' and user:
                print_prob_table(dice)
                continue
            elif choice.isdigit():
                idx = int(choice)
                if 0 <= idx < len(dice):
                    if forbidden is not None and idx == forbidden:
                        print("You can't pick the opponent's die.")
                        continue
                    print(f"You chose dice {idx}: {dice[idx]}")
                    return idx
            print("Invalid input.")

def secure_computer_roll():
    comp_index = secrets.randbelow(6)
    comp_secret, comp_hmac = commit_number(comp_index)
    print(f"Computer roll commitment HMAC: {comp_hmac}")
    return comp_index, comp_secret

def calc_win_prob(d1, d2):
    wins = sum(1 for i in d1 for j in d2 if i > j)
    return wins / 36

def print_prob_table(dice):
    headers = ["Dice"] + [f"Dice {i+1}" for i in range(len(dice))]
    table = []
    for i, d1 in enumerate(dice):
        row = [f"Dice {i+1}"]
        for j, d2 in enumerate(dice):
            if i == j:
                row.append("-")
            else:
                row.append(f"{calc_win_prob(d1, d2):.2f}")
        table.append(row)
    print(tabulate(table, headers=headers, tablefmt="grid"))

def get_user_roll_index():
    while True:
        user_input = input("Enter your roll number (0-5): ").strip()
        if user_input.isdigit():
            idx = int(user_input)
            if 0 <= idx <= 5:
                return idx
        print("Invalid input. Please enter a number between 0 and 5.")

def play_game():
    dice = get_dice()
    first = coin_toss()

    user_value = None
    comp_value = None

    if first == 1:  # Computer starts
        comp_idx, comp_secret = pick_dice(dice, user=False)
        user_idx = pick_dice(dice, user=True, forbidden=comp_idx)

        input("Press Enter to reveal Computer's dice choice...")
        reveal_commit("Computer", comp_idx, comp_secret)

        user_roll_index = get_user_roll_index()
        user_value = dice[user_idx][user_roll_index]
        print(f"You rolled index {user_roll_index}: value {user_value}\n")

        comp_roll_index, comp_roll_secret = secure_computer_roll()

        input("Press Enter to reveal Computer's roll...")

        final_comp_index = (comp_roll_index + user_roll_index) % 6
        comp_value = dice[comp_idx][final_comp_index]

        reveal_commit("Computer", comp_roll_index, comp_roll_secret)
        print(f"Final computer roll index (combined): {final_comp_index}, value: {comp_value}")

    else:  # User starts
        user_idx = pick_dice(dice, user=True)
        comp_idx, comp_secret = pick_dice(dice, user=False, forbidden=user_idx)

        input("Press Enter to reveal Computer's dice choice...")
        reveal_commit("Computer", comp_idx, comp_secret)

        user_roll_index = get_user_roll_index()
        user_value = dice[user_idx][user_roll_index]
        print(f"You rolled index {user_roll_index}: value {user_value}\n")

        comp_roll_index, comp_roll_secret = secure_computer_roll()

        input("Press Enter to reveal Computer's roll...")

        final_comp_index = (comp_roll_index + user_roll_index) % 6
        comp_value = dice[comp_idx][final_comp_index]

        reveal_commit("Computer", comp_roll_index, comp_roll_secret)
        print(f"Final computer roll index (combined): {final_comp_index}, value: {comp_value}")

 
    if user_value is None or comp_value is None:
        print("Error: Some values are missing. Exiting.")
        sys.exit(1)

    print("=== FINAL RESULT ===")
    print(f"Your value: {user_value}")
    print(f"Computer value: {comp_value}")
    if user_value > comp_value:
        print("You win!")
    elif user_value < comp_value:
        print("Computer wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    play_game()
