from pymongo import MongoClient
import os
from random import choice, randint, shuffle
import itertools
from rich import print as rprint


class PasswordGenerator:
    def __init__(self):
        self.cluster = os.environ.get("my_cluster_db")
        self.client = MongoClient(self.cluster)
        self.db = self.client.pass_access
        self.records = self.db.my_pass_access
        self.password = None
        self.password_generator_start()

    def password_generator_start(self):
        selection = input("To generate password press(1); to see all websites press(2): ")
        if selection == "1":
            self.generate_password()
            save_password = input("Would you like to save it? y/n: ").lower()
            if save_password == "y":
                self.save_to_db()
        elif selection == "2":
            self.search()
            find_password = input("Enter the index for website you are looking for as listed above: ").lower()
            if find_password == "exit":
                print("Thank you, See you again soon!")
            else:
                self.return_password(find_password)

    def generate_password(self):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                   'u',
                   'v',
                   'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                   'Q',
                   'R',
                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

        password_letters = [choice(letters) for _ in range(randint(8, 10))]
        password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
        password_numbers = [choice(numbers) for _ in range(randint(2, 4))]
        password_list = list(itertools.chain(password_letters, password_symbols, password_numbers))
        shuffle(password_list)

        self.password = "".join(password_list)
        return self.password

    def save_to_db(self):
        website = input("Enter Website: ").lower()
        username_or_email = input("Username or email: ").lower()
        password = self.generate_password()
        new_entry = {
            "websites": {
                "website": website,
                "email_username": username_or_email,
                "password": password
            }
        }

        if len(website) == 0 or len(password) == 0:
            print("[italic blue]Oops\nPlease make sure that all fields are completed[/italic blue]")
        else:
            result = self.records.insert_one(new_entry)
            self.search()
            self.return_password(website)

    def search(self):
        website_result = self.records.find({})
        for index, result in enumerate(website_result):
            rprint(f'[blue]{index}: {result["websites"]["website"]}[/blue]')

    def return_password(self, selected_index):
        website_result = self.records.find({})
        for index, result in enumerate(website_result):
            if str(index) == selected_index:
                rprint(result["websites"]["website"])
                rprint(result["websites"]["email_username"])
                rprint(f'[green]{result["websites"]["password"]}[/green]')


if __name__ == "__main__":
    my_passwords = PasswordGenerator()
