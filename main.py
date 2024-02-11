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
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        if new_phone not in self.phones:
            self.phones.append(new_phone)
        else:
            raise ValueError("Phone number already exists")

    def remove_phone(self, phone):
        phone_obj_searched = Phone(phone)
        for phone_obj in self.phones:
            if phone_obj.value == phone_obj_searched.value:
                self.phones.remove(phone_obj)
        return None

    def find_phone(self, phone):
        phone_obj_searched = Phone(phone)
        for phone_obj in self.phones:
            if phone_obj.value == phone_obj_searched.value:
                return phone_obj
        return None

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now().date()
        next_birthday = datetime(today.year, datetime.strptime(self.birthday.value, '%Y-%m-%d').month, datetime.strptime(self.birthday.value, '%Y-%m-%d').day).date()
        if today > next_birthday:
            next_birthday = datetime(today.year + 1, datetime.strptime(self.birthday.value, '%Y-%m-%d').month, datetime.strptime(self.birthday.value, '%Y-%m-%d').day).date()
        return (next_birthday - today).days

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value if self.birthday else 'Not specified'}"
    
    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = Phone(old_phone)
        new_phone_obj = Phone(new_phone)
        found = False
        for phone_obj in self.phones:
            if phone_obj.value == old_phone_obj.value:
                phone_obj.value = new_phone_obj.value
                found = True
                break
        if not found:
            raise ValueError("Phone number not found")

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        name_field = Name(name)
        return self.data.get(name_field.value)

    def delete(self, name):
        name_field = Name(name)
        if name_field.value in self.data:
            del self.data[name_field.value]
        else:
            return None

    def iterator(self, batch_size=10):
        all_records = list(self.data.values())
        num_batches = len(all_records) // batch_size + (1 if len(all_records) % batch_size != 0 else 0)
        for i in range(num_batches):
            yield all_records[i*batch_size : (i+1)*batch_size]
    
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.data = pickle.load(f)

    def search(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                results.append(record)
            else:
                for phone in record.phones:
                    if query in phone.value:
                        results.append(record)
                        break
        return results
    
    def __enter__(self):
        self.load('address_book.pkl')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save('address_book.pkl')

if __name__ == "__main__":
    book = AddressBook()
        
    john_record = Record("John", "1990-05-20")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    book.add_record(john_record)

    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Зберігаємо дані у файл 'address_book.pkl'
    book.save('address_book.pkl')

    # Далі можна використовувати з контекстом або окремо
    with AddressBook() as book:
        for batch in book.iterator(batch_size=1):
            for record in batch:
                print(record)

        john = book.find("John")
        print(john.days_to_birthday())

        found_phone = john.find_phone("5555555555")
        print(f"{found_phone}")

        book.delete("Jane")

        # Пошук за іменем або номером телефону
        search_results = book.search("John")  # Пошук за ім'ям
        for result in search_results:
            print(result)
        
        search_results = book.search("555")  # Пошук за номером телефону
        for result in search_results:
            print(result)