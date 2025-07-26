from tabulate import tabulate
import sys
import random
import secrets
import hmac
import hashlib

def get_dice():
    args = sys.argv[1:]
    if len(args) < 3:
        print("Error: You must enter at least 3 dice.\nExample: 1,2,3,4,5,6 2,2,2,5,5,5 6,6,6,1,1,1")
        sys.exit(1)
    dice = []
    for arg in args:
        try:
            faces = list(map(int, arg.split(',')))
        except ValueError:
            print("Error: Dice must be integers separated by commas.")
            sys.exit(1)
        if len(faces) != 6:
            print("Error: Each dice must have exactly 6 values.")
            sys.exit(1)
        dice.append(faces)
    return dice

def flip_coin():
    c = random.randint(0,1)
    s = str(random.randint(1,999999))
    commit = hashlib.sha256((s + str(c)).encode()).hexdigest()
    print(f"\n=== Coin toss to decide who starts ===")
    print(f"Commitment (SHA256): {commit}")
    input("Press Enter to reveal the result...")
    print(f"Secret revealed: {s}")
    print(f"Result: {'You start (0)' if c == 0 else 'Computer starts (1)'}")
    print("You can verify: SHA256(secret + result) == commitment\n")
    return c

def calc_win_prob(d1, d2):
    wins = 0
    total = 36
    for f1 in d1:
        for f2 in d2:
            if f1 > f2:
                wins += 1
    return wins / total

def print_prob_table(dice):
    n = len(dice)
    headers = ["Dice"] + [f"Dice {i+1}" for i in range(n)]
    table = []
    for i in range(n):
        row = [f"Dice {i+1}"]
        for j in range(n):
            if i == j:
                row.append("-")
            else:
                p = calc_win_prob(dice[i], dice[j])
                row.append(f"{p:.2f}")
        table.append(row)
    print("=== Winning Probability Table ===")
    print("Each cell shows the probability of the dice in the row vs the dice in the column.\n")
    print(tabulate(table, headers=headers, tablefmt="grid"))
    print()

def pick_dice(dice, user=True, forbidden=None):
    print(f"{'Your turn: Choose a dice' if user else 'Computer turn: choosing dice'}")
    while True:
        for i, d in enumerate(dice):
            print(f"{i} - {','.join(map(str,d))}")
        print("X - quit")
        print("? - help")

        ch = input("Your selection: ").strip().upper()
        if ch == 'X':
            print("Game finished")
            sys.exit(0)
        elif ch == '?':
            print_prob_table(dice)
            continue
        elif ch.isdigit():
            idx = int(ch)
            if 0 <= idx < len(dice):
                if forbidden is not None and idx == forbidden:
                    print("❗ You cannot choose your opponent's dice. Try again.")
                    continue
                print(f"{'You chose' if user else 'Computer chose'} Dice {idx}: {dice[idx]}")
                return idx
            else:
                print("Invalid choice. Try again.")
        else:
            print("Invalid input. Try again.")

def secure_roll(die):
    key = secrets.token_bytes(32)
    max_v = len(die)
    while True:
        rb = secrets.token_bytes(4)
        ri = int.from_bytes(rb, 'big')
        if ri < (2**32 // max_v) * max_v:
            num = ri % max_v
            break
    h = hmac.new(key, str(num).encode(), hashlib.sha3_256).hexdigest()

    print("\n--- Computer's secure roll ---")
    print(f"(Secret number hidden): {h}")
    print(f"Choose a number 0 to {max_v - 1} to add modulo {max_v} to computer's secret.")

    while True:
        ui = input(f"Choose number (0 to {max_v -1}): ").strip().upper()
        if ui == 'X':
            print("Game terminated.")
            sys.exit(0)
        elif ui == '?':
            print(f"Instruction: Pick integer between 0 and {max_v -1}.")
            continue
        elif ui.isdigit():
            un = int(ui)
            if 0 <= un < max_v:
                break
            else:
                print("Out of range. Try again.")
        else:
            print("Invalid input. Try again.")

    res = (un + num) % max_v

    print("\n--- Result revealed ---")
    print(f"Secret key (hex): {key.hex()}")
    print(f"Computer's secret number: {num}")
    print(f"Your chosen number: {un}")
    print(f"Final roll (mod {max_v}): {res}")
    print(f"Dice face value: {die[res]}")
    print("--------------------------------------\n")

    return res

def comp_turn(dice, forbidden):
    idx = random.choice([i for i in range(len(dice)) if i != forbidden])
    roll_idx = secure_roll(dice[idx])
    print(f"Computer chose Dice {idx} and rolled {dice[idx][roll_idx]}")
    return idx, roll_idx

def play_game():
    dice = get_dice()
    first = flip_coin()

    if first == 0:
        print("You start first.")
        user_idx = pick_dice(dice, user=True)
        user_roll_idx = secure_roll(dice[user_idx])
        user_roll_val = dice[user_idx][user_roll_idx]
        print(f"You rolled {user_roll_val}.")

        comp_idx, comp_roll_idx = comp_turn(dice, forbidden=user_idx)
        comp_roll_val = dice[comp_idx][comp_roll_idx]

    else:
        print("Computer starts first.")
        comp_idx = pick_dice(dice, user=False)
        comp_roll_idx = secure_roll(dice[comp_idx])
        comp_roll_val = dice[comp_idx][comp_roll_idx]
        print(f"Computer rolled {comp_roll_val}.")

        user_idx = pick_dice(dice, user=True, forbidden=comp_idx)
        user_roll_idx = secure_roll(dice[user_idx])
        user_roll_val = dice[user_idx][user_roll_idx]
        print(f"You rolled {user_roll_val}.")

    print("\n=== FINAL RESULT ===")
    print(f"You: {user_roll_val}  |  Computer: {comp_roll_val}")
    if user_roll_val > comp_roll_val:
        print("You win!")
    elif user_roll_val < comp_roll_val:
        print("Computer wins!")
    else:
        print("It's a tie!")


if __name__ == "__main__":
    play_game()
