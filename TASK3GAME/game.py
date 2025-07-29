from tabulate import tabulate
import sys
import hmac
import hashlib
import secrets


def get_dice():
    args = sys.argv[1:]
    if len(args) < 3:
        print("Error: You must enter at leats 3 dice.")
        print("Example: 1,2,3,4,5,6 2,2,2,5,5,5 6,6,6,1,1,1")
        sys.exit(1)

    dice = []
    for i, arg in enumerate(args):
        parts = [p.strip() for p in arg.strip().split(',') if p.strip()]
        if len(parts) != 6:
            print(f"Error: DIce {i+1} must have exactly 6 faces.")
            sys.exit(1)
        try:
            faces = []
            for face in parts:
                if not face.isdigit() or not (0 <= int(face) <= 9):
                    raise ValueError
                faces.append(int(face))
            dice.append(faces)
        except ValueError:
            print(f"Error: Dice {i+1} has invalid faces. Only digits from 0 to 9 are allowed.")
            sys.exit(1)
    return dice


def commit_value(value):
    key = secrets.token_bytes(32)
    h = hmac.new(key, str(value).encode(), hashlib.sha3_256).hexdigest()
    return key, h

def reveal_commit(name, value, key):
    print(f"{name} reveals: number = {value}, secret = {key.hex()}")
    check = hmac.new(key, str(value).encode(), hashlib.sha3_256).hexdigest()
    print(f"{name} HMAC check: {check}\n")


def coin_toss():
    print("=== COIN TOSS ===")
    comp_choice = secrets.randbelow(2)
    key, hmac_val = commit_value(comp_choice)
    print(f"Computer HMAC: {hmac_val}")

    while True:
        user_input = input("Your guess (0 or 1): ").strip()
        if user_input in ('0', '1'):
            user_guess = int(user_input)
            break
        print("Invalid input.")

    input("Press Enter to reveal...")
    reveal_commit("Computer", comp_choice, key)

    if user_guess == comp_choice:
        print("You start!\n")
        return 0
    else:
        print("Computer starts.\n")
        return 1


def pick_dice(dice, user=True, forbidden=None):
    if not user:
        options = [i for i in range(len(dice)) if i != forbidden]
        choice = secrets.choice(options)
        key, hmac_val = commit_value(choice)
        print(f"Computer dice choice HMAC: {hmac_val}")
        return choice, key
    else:
        while True:
            print("Pick your dice:")
            for i, d in enumerate(dice):
                if i == forbidden:
                    continue
                print(f"{i} - {d}")
            print("? - Show win probabilities\nX - Exit")
            choice = input("Choice: ").strip().upper()
            if choice == 'X':
                sys.exit(0)
            elif choice == '?':
                show_prob_table(dice)
            elif choice.isdigit():
                idx = int(choice)
                if idx == forbidden:
                    print("Error: You can't pick the opponent's dice. Please choose another.")
                    continue
                if 0 <= idx < len(dice):
                    print(f"You chose: {dice[idx]}")
                    return idx
            else:
                print("Invalid option.")



def get_user_roll():
    while True:
        choice = input("Enter your roll (0–5): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx <= 5:
                return idx
        print("Invalid input.")

def secure_computer_roll():
    index = secrets.randbelow(6)
    key, hmac_val = commit_value(index)
    print(f"Computer roll HMAC: {hmac_val}")
    return index, key


def show_prob_table(dice):
    headers = ["Dice"] + [f"Dice {i+1}" for i in range(len(dice))]
    table = []
    for i, d1 in enumerate(dice):
        row = [f"Dice {i+1}"]
        for j, d2 in enumerate(dice):
            if i == j:
                row.append("-")
            else:
                win = sum(1 for x in d1 for y in d2 if x > y)
                row.append(f"{win / 36:.2f}")
        table.append(row)
    print(tabulate(table, headers=headers, tablefmt="grid"))


def play_game():
    dice = get_dice()
    turn = coin_toss()

    if turn == 0:
        user_idx = pick_dice(dice)
        comp_idx, comp_key = pick_dice(dice, user=False, forbidden=user_idx)
    else:
        comp_idx, comp_key = pick_dice(dice, user=False)
        user_idx = pick_dice(dice, forbidden=comp_idx)

    input("Press Enter to reveal computer dice choice...")
    reveal_commit("Computer", comp_idx, comp_key)

    user_roll = get_user_roll()
    user_val = dice[user_idx][user_roll]
    print(f"You rolled index {user_roll} value: {user_val}")

    comp_roll, comp_roll_key = secure_computer_roll()
    input("Press Enter to reveal computer roll...")
    reveal_commit("Computer", comp_roll, comp_roll_key)

    final_comp_index = (comp_roll + user_roll) % 6
    comp_val = dice[comp_idx][final_comp_index]
    print("\n--- Combined Roll Details ---")
    print(f"Your roll index: {user_roll}")
    print(f"Computer original roll index: {comp_roll}")
    print(f"Combined index: ({comp_roll} + {user_roll}) % 6 = {final_comp_index}")
    print(f"Computer final value (from dice): {comp_val}")

    print("\n=== RESULT ===")
    print(f"Your value: {user_val}")
    print(f"Computer value: {comp_val}")
    if user_val > comp_val:
        print("You win!")
    elif user_val < comp_val:
        print("Computer wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    play_game()
