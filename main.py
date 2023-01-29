from pymongo import MongoClient
import os
from random import randint, shuffle
from rich import print as rprint
import string


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

        letters = [string.ascii_letters[randint(0, len(string.ascii_letters)-1)] for _ in range(8)]
        symbols_raw = string.punctuation[:1] + string.punctuation[2:6] + string.punctuation[7:25]
        symbols = [symbols_raw[randint(0, len(symbols_raw)-1)] for _ in range(2)]
        numbers = [string.digits[randint(0, len(string.digits)-1)] for _ in range(3)]
        password_list = letters + symbols + numbers
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
