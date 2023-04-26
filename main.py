import os
from random import randint, shuffle
from rich import print as rprint
import string
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class PasswordEntry(Base):
    __tablename__ = 'password_entries'
    id = Column(Integer, Sequence('password_entry_id_seq'), primary_key=True)
    website = Column(String(100), nullable=False)
    email_username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)


class PasswordGenerator:
    def __init__(self):
        self.engine = create_engine("sqlite:///passwords.db")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.password = None
        self.password_generator_start()

    def password_generator_start(self):
        selection = input("To generate password press(1); to see all websites press(2); to delete an entry press(3): ")
        if selection == "1":
            self.generate_password()
            print(self.generate_password())
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
        elif selection == "3":
            self.search()
            delete_password = input("Enter the index for the website entry you want to delete or type 'exit': ").lower()
            if delete_password == "exit":
                print("Thank you, See you again soon!")
            else:
                self.delete_entry(delete_password)

    def generate_password(self):
        letters = [string.ascii_letters[randint(0, len(string.ascii_letters)-1)] for _ in range(8)]
        symbols_raw = string.punctuation[:1] + string.punctuation[2:6] + string.punctuation[7:25]
        symbols = [symbols_raw[randint(0, len(symbols_raw)-1)] for _ in range(4)]
        numbers = [string.digits[randint(0, len(string.digits)-1)] for _ in range(4)]
        password_list = letters + symbols + numbers
        shuffle(password_list)

        self.password = "".join(password_list)
        return self.password

    def save_to_db(self):
        website = input("Enter Website: ").lower()
        username_or_email = input("Username or email: ").lower()
        password = self.generate_password()
        new_entry = PasswordEntry(website=website, email_username=username_or_email, password=password)

        if len(website) == 0 or len(password) == 0:
            print("[italic blue]Oops\nPlease make sure that all fields are completed[/italic blue]")
        else:
            self.session.add(new_entry)
            self.session.commit()
            self.search()
            self.return_password(website)

    def search(self):
        website_results = self.session.query(PasswordEntry).all()
        for index, result in enumerate(website_results):
            rprint(f'[blue]{index}: {result.website}[/blue]')

    def return_password(self, selected_index):
        website_results = self.session.query(PasswordEntry).all()
        for index, result in enumerate(website_results):
            if str(index) == selected_index:
                rprint(result.website)
                rprint(result.email_username)
                rprint(f'[green]{result.password}[/green]')

    def delete_entry(self, selected_index):
        website_results = self.session.query(PasswordEntry).all()
        entry_to_delete = None
        for index, result in enumerate(website_results):
            if str(index) == selected_index:
                entry_to_delete = result
                break

        if entry_to_delete is not None:
            self.session.delete(entry_to_delete)
            self.session.commit()
            print(f"Entry for {entry_to_delete.website} has been deleted.")
        else:
            print("No entry found with the given index.")


if __name__ == "__main__":
    my_passwords = PasswordGenerator()

