from random import randint, shuffle
from rich import print as rprint
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt
import string
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import declarative_base, sessionmaker
import pyperclip as pc

Base = declarative_base()

custom_theme = Theme({
    "info": "bold cyan",
    "warning": "magenta",
    "danger": "bold red"
})
console = Console(theme=custom_theme)


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

    def password_generator_start(self) -> None:
        selection: str = Prompt.ask(
            "[bold light]What would you like to do?[/bold light]\n[bold cyan]Press(1) to generate a new "
            "password[/bold cyan]\n[bold magenta]Press(2) for the password list[/bold magenta]"
            "\n[bold red]Press(3) for deleting a password[/bold red] [bold blue]\nPress(4) to quit: [/bold blue]")
        if selection == "1":
            self.generate_password()
            save_password = "y"
            if save_password == "y":
                self.save_to_db()
        elif selection == "2":
            self.search()
            find_password = input("Enter the index for the website entry "
                                  "you want to find or type 'exit' to quit:").lower()
            if find_password == "exit":
                console.print("Thank you, See you again soon!", style="info")
            else:
                self.return_password(find_password)
        elif selection == "3":
            self.search()
            delete_password: str = input("Enter the index for the website entry "
                                         "you want to delete or type 'exit' to quit: ").lower()
            if delete_password == "exit":
                console.print("Thank you, See you again soon!", style="info")
            else:
                self.delete_entry(delete_password)
        else:
            console.print("Thank you, See you again soon!", style="info")

    def generate_password(self) -> str:
        letters: list = [string.ascii_letters[randint(0, len(string.ascii_letters) - 1)] for _ in range(10)]
        symbols_raw: str = string.punctuation[:1] + string.punctuation[2:6] + string.punctuation[7:25]
        symbols: list = [symbols_raw[randint(0, len(symbols_raw) - 1)] for _ in range(6)]
        numbers: list = [string.digits[randint(0, len(string.digits) - 1)] for _ in range(5)]
        password_list: list = letters + symbols + numbers
        shuffle(password_list)

        self.password = "".join(password_list)
        return self.password

    def save_to_db(self) -> None:
        website: str = input("Enter Website: ").lower()
        username_or_email: str = input("Username or email: ").lower()
        password: str = self.generate_password()
        new_entry: PasswordEntry = PasswordEntry(website=website, email_username=username_or_email, password=password)

        if len(website) == 0 or len(password) == 0:
            print("[italic blue]Oops\nPlease make sure that all fields are completed[/italic blue]")
        else:
            self.session.add(new_entry)
            self.session.commit()
            self.search()
            self.return_password(website)

    def search(self) -> None:
        website_results: list = self.session.query(PasswordEntry).all()
        for index, result in enumerate(website_results):
            rprint(f'[blue]{index}: {result.website}[/blue]')

    def return_password(self, selected_index: str) -> None:
        website_results: list = self.session.query(PasswordEntry).all()
        for index, result in enumerate(website_results):
            if str(index) == selected_index:
                console.print(result.website, style="info")
                console.print(result.email_username, style="warning")
                console.print(f'{result.password}', style="danger")
                pc.copy(result.password)

    def delete_entry(self, selected_index: str) -> None:
        website_results: list = self.session.query(PasswordEntry).all()
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
