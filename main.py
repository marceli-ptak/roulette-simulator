import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import random
import pickle
import gc

class RouletteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Roulette Simulator")

        # Initial balance
        self.initial_balance = 0
        self.balance = 0
        self.temporary_balance = 0
        self.buttons = {}
        self.selected_bets = []
        self.special_bets = {}

        # Set starting balance entry
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=10)

        self.starting_balance_label = tk.Label(self.controls_frame, text="Starting Balance:", font=("Arial", 12))
        self.starting_balance_label.grid(row=0, column=0, padx=5)

        self.starting_balance_entry = tk.Entry(self.controls_frame, font=("Arial", 12))
        self.starting_balance_entry.grid(row=0, column=1, padx=5)

        self.set_balance_button = tk.Button(self.controls_frame, text="Set Balance", command=self.set_starting_balance, font=("Arial", 12))
        self.set_balance_button.grid(row=0, column=2, padx=5)

        # Bet amount entry
        self.bet_label = tk.Label(self.controls_frame, text="Bet Amount:", font=("Arial", 12))
        self.bet_label.grid(row=0, column=3, padx=5)

        self.bet_entry = tk.Entry(self.controls_frame, font=("Arial", 12))
        self.bet_entry.grid(row=0, column=4, padx=5)

        # Spin button
        self.spin_button = tk.Button(self.controls_frame, text="SPIN", command=self.place_bet, font=("Arial", 12))
        self.spin_button.grid(row=0, column=5, padx=5)

        # Reset button
        self.reset_button = tk.Button(self.controls_frame, text="RESET", command=self.reset_bets, font=("Arial", 12))
        self.reset_button.grid(row=0, column=6, padx=5)

        # Current balance
        self.balance_label = tk.Label(root, text=f"Balance: {round(self.balance, 2)} $", font=("Arial", 14))
        self.balance_label.pack(pady=10)

        # Create roulette table
        self.table_frame = tk.Frame(root, bg="green")  # Green table background
        self.table_frame.pack(pady=20, padx=20)

        # Colors of roulette numbers
        self.colors = {
            0: "green",
            1: "red", 2: "black", 3: "red", 4: "black", 5: "red", 6: "black",
            7: "red", 8: "black", 9: "red", 10: "black", 11: "black", 12: "red",
            13: "black", 14: "red", 15: "black", 16: "red", 17: "black", 18: "red",
            19: "red", 20: "black", 21: "red", 22: "black", 23: "red", 24: "black",
            25: "red", 26: "black", 27: "red", 28: "black", 29: "black", 30: "red",
            31: "black", 32: "red", 33: "black", 34: "red", 35: "black", 36: "red"
        }

        self.create_table()
        self.create_special_bets()

        # Result label
        self.result_label = tk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

    def set_starting_balance(self, amount=None):
        try:
            self.initial_balance = amount if amount is not None else self.starting_balance_entry.get()
            if self.initial_balance <= 0:
                raise ValueError
            self.balance = self.initial_balance
            self.temporary_balance = self.balance
            self.update_balance_label()
            self.starting_balance_entry.config(state="disabled")
            self.set_balance_button.config(state="disabled")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid starting balance (a positive number).")

    def update_balance_label(self):
        self.balance_label.config(text=f"Balance: {round(self.temporary_balance, 2)} $")

    def create_table(self):
        # Add "0" on the side spanning 3 rows
        zero_frame = tk.Frame(self.table_frame, bg="white", padx=1, pady=1)
        zero_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        zero_image = self.create_rotated_text_image("0", (58, 44), "green", "white")
        zero_button = tk.Button(zero_frame, image=zero_image, bg="green", relief="flat",
                                command=lambda: self.toggle_bet(0))
        zero_button.image = zero_image
        zero_button.pack(fill="both", expand=True)
        self.buttons[0] = zero_button

        # Add numbers 1-36 in a horizontal layout without gaps
        for i in range(3):
            for j in range(12):
                number = j * 3 + (2 - i) + 1  # Reverse row order
                color = self.colors[number]
                number_frame = tk.Frame(self.table_frame, bg="white", padx=1, pady=1)
                number_frame.grid(row=i, column=j + 1, sticky="nsew")
                number_image = self.create_rotated_text_image(str(number), (58, 44), color, "white")
                button = tk.Button(number_frame, image=number_image, bg=color, relief="flat",
                                   command=lambda num=number: self.toggle_bet(num))
                button.image = number_image
                button.pack(fill="both", expand=True)
                self.buttons[number] = button

            # Add "2-1" button at the end of each row
            row_bet_frame = tk.Frame(self.table_frame, bg="white", padx=1, pady=1)
            row_bet_frame.grid(row=i, column=13, sticky="nsew")
            row_bet_image = self.create_rotated_text_image("2-1", (58, 44), "green", "white")
            row_bet_button = tk.Button(row_bet_frame, image=row_bet_image, bg="green", relief="flat",
                                       command=lambda r=i: self.toggle_bet(f"row{r + 1}"))
            row_bet_button.image = row_bet_image
            row_bet_button.pack(fill="both", expand=True)
            self.special_bets[f"row{i + 1}"] = row_bet_button

    def create_special_bets(self):
        # Add special betting areas below the numbers
        special_bets_frame = tk.Frame(self.table_frame, bg="green")
        special_bets_frame.grid(row=3, column=1, columnspan=12, sticky="nsew")

        row1_bets = ["1st 12", "2nd 12", "3rd 12"]

        # Arrange row1 bets
        for idx, label in enumerate(row1_bets):
            bet_frame = tk.Frame(special_bets_frame, bg="white", padx=1, pady=1)
            bet_frame.grid(row=0, column=idx * 4, columnspan=4, sticky="nsew")
            button = tk.Button(bet_frame, text=label, font=("Arial", 12), width=24, height=2, relief="flat", bg="green",
                               fg="white",
                               command=lambda lbl=label: self.toggle_bet(lbl))
            button.pack(fill="both", expand=True)
            self.special_bets[label] = button

        # Arrange row2 bets directly below their corresponding row1 bets
        row2_mapping = {
            "1-18": 0,
            "Even": 1,
            "Red": 2,
            "Black": 3,
            "Odd": 4,
            "19-36": 5
        }
        column_mapping = {
            "1-18": 0,
            "Even": 2,
            "Red": 4,
            "Black": 6,
            "Odd": 8,
            "19-36": 10
        }

        for label in row2_mapping.keys():
            color = "red" if label == "Red" else "black" if label == "Black" else "green"
            column = column_mapping[label]
            bet_frame = tk.Frame(special_bets_frame, bg="white", padx=1, pady=1)
            bet_frame.grid(row=1, column=column, columnspan=2, sticky="nsew")
            button = tk.Button(bet_frame, text=label, font=("Arial", 12), width=12, height=2, relief="flat", bg=color,
                               fg="white",
                               command=lambda lbl=label: self.toggle_bet(lbl))
            button.pack(fill="both", expand=True)
            self.special_bets[label] = button

    def create_rotated_text_image(self, text, size, bg_color, text_color):
        # Create an image with PIL
        image = Image.new("RGBA", size, bg_color)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Rotate the image
        rotated_image = image.rotate(90, expand=True)
        return ImageTk.PhotoImage(rotated_image)

    def toggle_bet(self, bet):
        bet_amount = self.get_bet_amount()
        try:
            bet_amount = float(bet_amount)  # Convert bet_amount to an integer
        except ValueError:
            messagebox.showwarning("Error", "Invalid bet amount!")
            return
        if self.temporary_balance < bet_amount:
            messagebox.showwarning("Error", "Insufficient balance for this bet!")
            return
        self.selected_bets.append((bet, bet_amount))
        self.temporary_balance -= bet_amount
        self.update_balance_label()

    def place_bet(self):
        if not self.selected_bets:
            messagebox.showwarning("Error", "You have not selected any bets!")
            return

        result = self.spin_roulette()
        self.balance = self.temporary_balance

        # Calculate winnings
        winnings = 0
        for bet, bet_amount in self.selected_bets:
            if isinstance(bet, int):  # Single number bet
                if bet == result:
                    winnings += bet_amount * 36  # Straight-up bet
            elif isinstance(bet, str):  # Special bets (labels)
                if bet in self.special_bets:
                    if bet == "1st 12" and result in range(1, 13):
                        winnings += bet_amount * 3
                    elif bet == "2nd 12" and result in range(13, 25):
                        winnings += bet_amount * 3
                    elif bet == "3rd 12" and result in range(25, 37):
                        winnings += bet_amount * 3
                    elif bet == "1-18" and result in range(1, 19):
                        winnings += bet_amount * 2
                    elif bet == "19-36" and result in range(19, 37):
                        winnings += bet_amount * 2
                    elif bet == "Even" and result % 2 == 0 and result != 0:
                        winnings += bet_amount * 2
                    elif bet == "Odd" and result % 2 != 0:
                        winnings += bet_amount * 2
                    elif bet == "Red" and self.colors[result] == "red":
                        winnings += bet_amount * 2
                    elif bet == "Black" and self.colors[result] == "black":
                        winnings += bet_amount * 2
                    elif bet == "row1" and result in range(3, 37, 3):
                        winnings += bet_amount * 3
                    elif bet == "row2" and result in range(2, 37, 3):
                        winnings += bet_amount * 3
                    elif bet == "row3" and result in range(1, 37, 3):
                        winnings += bet_amount * 3

        # Update balance
        if winnings > 0:
            self.balance += winnings
            self.result_label.config(
                text=f"You won! The result was {result}. Winnings: {round(winnings, 2)}$", fg="green")
        else:
            self.result_label.config(text=f"You lost! The result was {result}", fg="red")

        self.temporary_balance = self.balance
        self.update_balance_label()
        self.selected_bets.clear()

        # Check for bankruptcy
        # For simulation purposes, disable check for bankruptcy by commenting the following lines
        # if self.balance == 0:
        #     self.reset_game()
        #     self.show_bankrupt_message()

    def show_bankrupt_message(self):
        if messagebox.askyesno("Bankrupt", "You are bankrupt! Do you want to play again?"):
            self.reset_game()
        else:
            self.root.destroy()

    def reset_bets(self):
        self.temporary_balance = self.balance
        self.selected_bets.clear()
        self.update_balance_label()

    def reset_game(self):
        self.balance = self.initial_balance
        self.temporary_balance = self.initial_balance
        self.update_balance_label()
        self.starting_balance_entry.config(state="normal")
        self.set_balance_button.config(state="normal")
        self.selected_bets.clear()
        self.result_label.config(text="")

    def get_bet_amount(self, amount=None):
        try:
            if amount is None:
                return self.bet_entry.get()
            else:
                return amount
        except ValueError:
            return 0

    def spin_roulette(self):
        return random.randint(0, 36)

    def run_martingale_simulation(self):
        number_of_consecutive_losses = 7
        initial_balance = 2 ** number_of_consecutive_losses - 1
        bet_type = "Red"
        num_simulations = 10000
        initial_bet = 1

        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            amount = initial_bet

            while self.balance >= amount:
                self.bet_entry.delete(0, tk.END)  # Clear bet amount
                self.bet_entry.insert(0, str(amount))
                self.toggle_bet(bet_type)  # Set bet type
                previous_balance = self.balance
                self.place_bet()
                if self.balance > previous_balance:
                    amount = initial_bet  # Reset to initial amount after win
                else:
                    amount *= 2  # Double the amount after loss

                if self.balance < amount and self.balance > 0:
                    amount = self.balance  # Play the remaining balance after loss

                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()

        # Save the results to a file
        with open('results/martingale_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_paroli_simulation(self):
        initial_balance = 100
        bet_type = "Red"
        num_simulations = 10000
        initial_bet = 1

        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            amount = initial_bet
            counter = 0

            while self.balance >= amount:
                self.bet_entry.delete(0, tk.END)  # Clear bet amount
                self.bet_entry.insert(0, str(amount))
                self.toggle_bet(bet_type)  # Set bet type
                previous_balance = self.balance
                self.place_bet()
                if self.balance > previous_balance and counter < 3:
                    amount *= 2  # Double the amount after win
                    counter += 1

                else:
                    amount = initial_bet  # Reset to initial amount after a loss
                    counter = 0

                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()

        # Save the results to a file
        with open('results/paroli_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_fibonacci_simulation(self):
        initial_balance = 376 # Sum of the first 12 Fibonacci numbers
        bet_type = "Red"
        num_simulations = 10000
        save_interval = 1000  # Save results every 1000 simulations

        self.set_starting_balance(initial_balance)
        all_balances = []
        fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

        for sim in range(num_simulations):
            balances = [self.balance]
            i = 0
            amount = fibonacci_sequence[i]

            while self.balance >= amount:
                self.bet_entry.delete(0, tk.END)  # Clear bet amount
                self.bet_entry.insert(0, str(amount))
                self.toggle_bet(bet_type)  # Set bet type
                previous_balance = self.balance
                self.place_bet()
                if self.balance > previous_balance and i > 1:
                    i -= 2  # Move two steps back in the Fibonacci sequence after win
                    amount = fibonacci_sequence[i]
                elif i < len(fibonacci_sequence) - 1 and self.balance >= fibonacci_sequence[i+1]:
                    i += 1
                    amount = fibonacci_sequence[i]  # Move one step forward in the Fibonacci sequence after loss

                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()


        with open(f'results/fibonacci_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_holy_splits_simulation(self):
        initial_balance = 84
        bets = [
            (1, 1), (2, 1), (5, 1), (6, 1), (7, 1), (8, 1), (11, 1), (12, 1), (13, 1), (14, 1),
            (17, 1), (18, 1), (19, 1), (20, 1), (23, 1), (24, 1), (25, 1), (26, 1), (29, 1), (30, 1),
            (31, 1), (32, 1), (35, 1), (36, 1), ("row2", 4)
            ]
        num_simulations = 10000

        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            bet_amount = 28

            while self.balance >= 28:
                self.selected_bets = bets.copy()
                self.temporary_balance -= bet_amount
                self.place_bet()
                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()

        with open('results/holy_splits_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_ai_strategy_simulation(self):
        initial_balance = 20
        bet_type = ["1st 12", "Even", "2nd 12"]
        num_simulations = 10000
        initial_bet = 1

        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            amount = initial_bet

            while self.balance >= amount:
                self.bet_entry.delete(0, tk.END)  # Clear bet amount
                self.bet_entry.insert(0, str(amount))
                self.toggle_bet(bet_type[0])  # Set bet type
                previous_balance = self.balance
                self.place_bet()
                balances.append(self.balance)  # Append current balance to the list

                if self.balance > previous_balance:
                    amount *= 3  # bet all winnings from the 1st 12 bet
                    self.bet_entry.delete(0, tk.END)  # Clear bet amount
                    self.bet_entry.insert(0, str(amount))
                    self.toggle_bet(bet_type[1])  # Set bet type to Even
                    previous_balance = self.balance
                    self.place_bet()
                    balances.append(self.balance)

                if self.balance > previous_balance:
                    amount = amount * 2 - 1 # bet all winnings from the Even bet except initial_bet
                    self.bet_entry.delete(0, tk.END)  # Clear bet amount
                    self.bet_entry.insert(0, str(amount))
                    self.toggle_bet(bet_type[2])  # Set bet type to 2nd 12
                    previous_balance = self.balance
                    self.place_bet()
                    balances.append(self.balance)

                if self.balance > previous_balance:
                    initial_bet *= 2  # if all complete sucessfuly double the initial bet
                    amount = initial_bet

                else:
                    initial_bet = 1  # Reset initial bet after loss
                    amount = initial_bet

            all_balances.append(balances)
            self.reset_game()

        # Save the results to a file
        with open('results/ai_strategy_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_james_bond_simulation(self):
        original_unit = 20
        number_of_consecutive_losses = 7
        initial_balance = original_unit * (2 ** number_of_consecutive_losses - 1)
        num_simulations = 10000

        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            amount = original_unit

            while self.balance >= amount:
                unit = amount
                bets = [
                    (0, unit / 20),
                    (19, unit / 24), (20, unit / 24), (21, unit / 24),
                    (22, unit / 24), (23, unit / 24), (24, unit / 24),
                    ("1-18", unit * 7 / 10),
                ]
                self.selected_bets = bets.copy()
                self.temporary_balance -= amount
                previous_balance = self.balance
                self.place_bet()
                if self.balance > previous_balance:
                    amount = original_unit  # Reset to initial amount after win
                elif self.balance >= amount * 2:
                    amount *= 2  # Double the amount after loss

                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()

        # Save the results to a file
        with open('results/james_bond_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_dalembert_simulation(self):
        initial_bet = 2
        initial_balance = 9 # enough to cover 7 consecutive losses
        bet_type = "Red"
        num_simulations = 10000

        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            amount = initial_bet

            while self.balance >= amount:
                self.bet_entry.delete(0, tk.END)  # Clear bet amount
                self.bet_entry.insert(0, str(amount))
                self.toggle_bet(bet_type)  # Set bet type
                previous_balance = self.balance
                self.place_bet()
                if self.balance > previous_balance:
                    if amount < 3:
                        amount = 1 # Decrease the amount after win
                    else:
                        amount = initial_balance
                elif self.balance >= amount + 1:
                    amount += 1 # Increase the amount after loss
                else:
                    amount = self.balance # Go all in with the remaining balance

                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()

        # Save the results to a file
        with open('results/dalembert_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

    def run_ultimate_strategy_simulation(self):
        initial_balance = 1
        bet_type = "Red"
        num_simulations = 10000
        self.set_starting_balance(initial_balance)
        all_balances = []

        for _ in range(num_simulations):
            balances = [self.balance]
            amount = self.balance

            while self.balance >= amount:
                self.bet_entry.delete(0, tk.END)  # Clear bet amount
                self.bet_entry.insert(0, str(amount))
                self.toggle_bet(bet_type)  # Set bet type
                previous_balance = self.balance
                self.place_bet()
                if self.balance > previous_balance:
                    amount = self.balance  # Go all in after win
                balances.append(self.balance)  # Append current balance to the list

            all_balances.append(balances)
            self.reset_game()

        # Save the results to a file
        with open('results/ultimate_strategy_simulations.pkl', 'wb') as f:
            pickle.dump(all_balances, f)

if __name__ == "__main__":
    gc.collect()
    root = tk.Tk()
    app = RouletteGUI(root)
    #root.mainloop() # For simulation purposes, comment this line

    # app.run_martingale_simulation()
    # app.run_paroli_simulation()
    # app.run_fibonacci_simulation()
    # app.run_holy_splits_simulation()
    # app.run_ai_strategy_simulation()
    # app.run_james_bond_simulation()
    app.run_dalembert_simulation()
    # app.run_ultimate_strategy_simulation()







