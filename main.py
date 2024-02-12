import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value

    def __str__(self):
        return str(self.__value)

    def is_valid(self, value):
        return True

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value

class Name(Field):
    pass

class Phone(Field):
    def is_valid(self, value):
        return value.isdigit() and len(value) == 10

class Birthday(Field):
    def is_valid(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name, phone, birthday=None):
        self.name = Name(name)
        self.phone = Phone(phone)
        self.birthday = Birthday(birthday) if birthday else None

    def __str__(self):
        return f"{self.name}: {self.phone}"

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            next_birthday = datetime.strptime(str(today.year) + self.birthday.value[4:], '%Y-%m-%d').date()
            if next_birthday < today:
                next_birthday = datetime.strptime(str(today.year + 1) + self.birthday.value[4:], '%Y-%m-%d').date()
            return (next_birthday - today).days
        else:
            return None

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete_record(self, name):
        del self.data[name]

    def find_record(self, name):
        return self.data.get(name)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load(self, filename):
        try:
            with open(filename, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {}

    def __enter__(self):
        self.load("address_book.pkl")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save("address_book.pkl")

    def __iter__(self):
        for key in self.data:
            yield self.data[key]

def search_contacts(query):
    search_results = []
    with AddressBook() as book:
        for record in book.data.values():
            if query.lower() in record.name.value.lower():
                search_results.append(record)
            elif query in record.phone.value:
                search_results.append(record)
    return search_results


    
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError):
            return "Invalid command. Please try again."
    return wrapper

def main():
    with AddressBook() as book:
        print("How can I help you?")
        while True:
            user_input = input("Enter your command: ").lower().strip()
            if user_input.startswith("add "):
                try:
                    components = user_input.split(maxsplit=3)
                    if len(components) < 3:
                        print("Invalid command. Please provide name and phone.")
                        continue  # Продовжуємо зчитувати наступну команду
                    name = components[1]
                    phone = components[2]
                    birthday = components[3] if len(components) > 3 else None
                    
                    if name in book.data:
                        print(f"Contact {name} already exists. Use 'change' command to update it.")
                    else:
                        record = Record(name, phone, birthday)
                        book.add_record(record)
                        print(f"Contact {name} added with phone number {phone} and birthday {birthday}")
                except ValueError:
                    print("Invalid command. Please provide name, phone, and optionally birthday.")

            elif user_input.startswith("change "):  
                try:
                    args = user_input.split(maxsplit=1)[1].split()  # Розділити аргументи команди
                    name, phone = args[:2]  # Перші два аргументи: ім'я та номер телефону
                    birthday = args[2] if len(args) > 2 else None  # Третій аргумент (якщо є): день народження
                    record = Record(name, phone, birthday)
                    book.add_record(record)
                    print(f"Contact {name} added with phone number {phone}")
                except ValueError:
                    print("Invalid command. Please provide name and phone.")

            
            elif user_input.startswith("phone"):
                try:
                    _, name = user_input.split(maxsplit=1)
                    record = book.find_record(name)
                    if record:
                        print(f"The phone number for {name} is {record.phone}")
                    else:
                        print(f"No contact with the name {name} found.")
                except ValueError:
                    print("Invalid command. Please provide name.")
                    
            elif user_input.startswith("show all"):
                if book.data:
                    for record in book.data.values():
                        print(record)
                        if record.birthday:
                            print(f"Birthday: {record.birthday}")
                            days_left = record.days_to_birthday()
                            if days_left is not None:
                                print(f"Days left until birthday: {days_left}")
                else:
                    print("No contacts available")
                    
            elif user_input.startswith("search "):
                query = user_input.split(maxsplit=1)[-1].strip()
                search_results = search_contacts(query)
                if search_results:
                    print("Search results:")
                    for result in search_results:
                        print(result)
                else:
                    print("No matching contacts found.")
                  
            elif user_input.startswith(("good bye", "close", "exit")):
                print("Good bye!")
                break
            else:
                print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
