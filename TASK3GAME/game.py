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

def commit_number(name):
    number = secrets.randbelow(2)
    secret = secrets.token_bytes(16)
    h = hmac.new(secret, str(number).encode(), hashlib.sha3_256).hexdigest()
    print(f"{name} HMAC: {h}")
    return number, secret, h

def reveal_number(name, number, secret):
    print(f"{name} reveals: number = {number}, secret = {secret.hex()}")
    h = hmac.new(secret, str(number).encode(), hashlib.sha3_256).hexdigest()
    print(f"{name} HMAC check: {h}")
    return number

def coin_toss():
    print("\n=== COIN TOSS ===")
    user_num, user_sec, _ = commit_number("User")
    comp_num, comp_sec, _ = commit_number("Computer")

    input("Press Enter to reveal both secrets...")
    user_choice = reveal_number("User", user_num, user_sec)
    comp_choice = reveal_number("Computer", comp_num, comp_sec)

    result = (user_choice + comp_choice) % 2
    print(f"Result: {'User' if result == 0 else 'Computer'} starts\n")
    return result

def pick_dice(dice, user=True, forbidden=None):
    role = "Your" if user else "Computer's"
    while True:
        print(f"{role} turn to pick a die:")
        for i, d in enumerate(dice):
            print(f"{i} - {d}")
        print("? - Show win probabilities")
        print("X - Exit")
        choice = input("Pick: ").strip().upper() if user else str(secrets.randbelow(len(dice)))
        if choice == 'X':
            sys.exit(0)
        elif choice == '?':
            print_prob_table(dice)
            continue
        elif choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(dice):
                if forbidden is not None and idx == forbidden:
                    print("You can't pick the opponent's die.")
                    continue
                print(f"{role} chose die {idx}: {dice[idx]}")
                return idx
        if user:
            print("Invalid input.")

def secure_roll(name, dice):
    index = secrets.randbelow(len(dice))
    secret = secrets.token_bytes(16)
    h = hmac.new(secret, str(index).encode(), hashlib.sha3_256).hexdigest()
    print(f"{name} roll HMAC: {h}")
    input(f"Press Enter to reveal {name}'s roll...")
    print(f"{name} roll index: {index}, value: {dice[index]}, secret: {secret.hex()}")
    verify = hmac.new(secret, str(index).encode(), hashlib.sha3_256).hexdigest()
    print(f"{name} HMAC check: {verify}\n")
    return index, dice[index]

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

def play_game():
    dice = get_dice()
    first = coin_toss()

    if first == 1:
        comp_idx = pick_dice(dice, user=False)
        
        comp_roll_index = secrets.randbelow(6)
        comp_secret = secrets.token_bytes(16)
        comp_hmac = hmac.new(comp_secret, str(comp_roll_index).encode(), hashlib.sha3_256).hexdigest()
        print(f"Computer roll HMAC: {comp_hmac}\n")

        user_idx = pick_dice(dice, user=True, forbidden=comp_idx)
        user_roll_index, user_value = secure_roll("User", dice[user_idx])

        input("Press Enter to reveal Computer's roll...")
        print(f"Computer roll index: {comp_roll_index}, value: {dice[comp_idx][comp_roll_index]}, secret: {comp_secret.hex()}")
        check = hmac.new(comp_secret, str(comp_roll_index).encode(), hashlib.sha3_256).hexdigest()
        print(f"Computer HMAC check: {check}\n")
        comp_value = dice[comp_idx][comp_roll_index]

    else:
        user_idx = pick_dice(dice, user=True)
       
        user_roll_index = secrets.randbelow(6)
        user_secret = secrets.token_bytes(16)
        user_hmac = hmac.new(user_secret, str(user_roll_index).encode(), hashlib.sha3_256).hexdigest()
        print(f"User roll HMAC: {user_hmac}\n")

        comp_idx = pick_dice(dice, user=False, forbidden=user_idx)
        comp_roll_index, comp_value = secure_roll("Computer", dice[comp_idx])

        input("Press Enter to reveal User's roll...")
        print(f"User roll index: {user_roll_index}, value: {dice[user_idx][user_roll_index]}, secret: {user_secret.hex()}")
        check = hmac.new(user_secret, str(user_roll_index).encode(), hashlib.sha3_256).hexdigest()
        print(f"User HMAC check: {check}\n")
        user_value = dice[user_idx][user_roll_index]

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
