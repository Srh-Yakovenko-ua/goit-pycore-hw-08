from collections import UserDict
from datetime import datetime
import pickle
from typing import List, Optional, Union


class Field:
    def __init__(self, value: str):
        """Base class for record fields."""
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        """Class for storing a contact name. Name must be at least 3 characters long."""
        if len(value) < 3:
            raise ValueError(
                f"Name '{value}' was not added. It must be at least 3 characters long."
            )
        super().__init__(value)


class Phone(Field):
    def __init__(self, value: str):
        """Class for storing a phone number. Phone number must be 10 digits long."""
        if not (value.isdigit() and len(value) == 10):
            raise ValueError(
                f"Phone number {value} was not added. It must be 10 digits"
            )
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        """Class for storing a birthday. Expected format: DD.MM.YYYY"""
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(parsed_date)

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str) -> None:
        """Class for storing contact information, including name, phones, and birthday."""
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def __str__(self) -> str:
        """Format record as a string for display."""
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

    def add_phone(self, contact_number: str) -> None:
        """Add a phone number to the contact."""
        self.phones.append(Phone(contact_number))

    def edit_phone(self, old_number: str, new_number: str) -> None:
        """Edit an existing phone number in the contact."""
        matches = [phone for phone in self.phones if phone.value == old_number]
        if matches:
            matches[0].value = new_number
        else:
            print(f"Phone {old_number} not found")

    def find_phone(self, contact_number: str) -> Optional[str]:
        """Find a phone number in the contact."""
        found_phones = [phone for phone in self.phones if phone.value == contact_number]
        return found_phones[0].value if found_phones else None

    def remove_phone(self, contact_number: str) -> None:
        """Remove a phone number from the contact."""
        phone_to_remove = next(
            (phone for phone in self.phones if phone.value == contact_number), None
        )
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            print(f"Phone {contact_number} removed")
        else:
            print(f"Phone {contact_number} not found")

    def add_birthday(self, birthday_str: str) -> None:
        """Add a birthday to the contact."""
        if self.birthday is None:
            self.birthday = Birthday(birthday_str)
        else:
            raise Exception(
                f"A birthday is already set for {self.name.value}. Current birthday: {self.birthday}"
            )

    def show_birthday(self) -> str:
        """Show the contact's birthday if set."""
        return (
            str(self.birthday)
            if self.birthday
            else f"No birthday set for {self.name.value}"
        )


class AddressBook(UserDict):
    def __str__(self) -> str:
        """Return all records in the address book as a formatted string."""
        return (
            "\n".join(str(record) for record in self.data.values())
            if self.data
            else "No records"
        )

    def add_record(self, record_to_add: Record) -> None:
        """Add a record to the address book."""
        self[record_to_add.name.value] = record_to_add

    def find(self, contact_name: str) -> Optional[Record]:
        """Find a record by contact name."""
        return self.data.get(contact_name)

    def delete(self, contact_name: str) -> None:
        """Delete a record by contact name."""
        if contact_name in self.data:
            del self[contact_name]
            print(f"Contact {contact_name} deleted")
        else:
            print(f"Contact {contact_name} not found")

    def get_upcoming_birthdays(self, days: int = 7) -> List[Record]:
        """Get a list of contacts with birthdays within the next specified number of days."""
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday < days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


def input_error(func):
    """Decorator to handle input errors."""

    def inner(*args, **kwargs) -> Union[str, None]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    return inner


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """Add a contact to the address book."""
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """Add a birthday to a contact."""
    name, birthday_str, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    """Show a contact's birthday."""
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return record.show_birthday()


@input_error
def birthdays(book: AddressBook) -> str:
    """Show upcoming birthdays within the next 7 days."""
    upcoming_birthdays = book.get_upcoming_birthdays()
    return (
        "\n".join(str(record) for record in upcoming_birthdays)
        if upcoming_birthdays
        else "No upcoming birthdays."
    )


@input_error
def edit_phone(args: List[str], book: AddressBook) -> str:
    """Edit a phone number for a contact."""
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone number updated for {name}."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    """Show all phone numbers for a contact."""
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    return f"Phones for {name}: " + "; ".join(p.value for p in record.phones)


def parse_input(user_input: str) -> List[str]:
    """Parse user input into command and arguments."""
    return user_input.split()


def save_data(book: AddressBook, filename: str = "addressbook.pkl") -> None:
    """Save the address book data to a file."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = "addressbook.pkl") -> AddressBook:
    """Load the address book data from a file."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main() -> None:
    """Main function for the assistant bot interface."""
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        save_data(book)
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(edit_phone(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
