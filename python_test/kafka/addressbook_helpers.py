
from enum import Enum


class PhoneType(Enum):
    PHONE_TYPE_UNSPECIFIED = 0
    PHONE_TYPE_MOBILE = 1
    PHONE_TYPE_HOME = 2
    PHONE_TYPE_WORK = 3

class PhoneNumber:
    def __init__(self, pn_pb2):
        self.number: str = pn_pb2.number
        self.type: PhoneType = PhoneType(pn_pb2.type)

class Person:
    def __init__(self, psn_pb2):
        self.name: str = psn_pb2.name
        self.id: int = psn_pb2.id
        self.email: str = psn_pb2.email
        self.phones: list[PhoneNumber] = [
            PhoneNumber(ph_pb2) for ph_pb2 in psn_pb2.phones
        ]

class AddressBook:
    def __init__(self, adb_pb2):
        self.people: list[Person] = [
            Person(psn_pb2) for psn_pb2 in adb_pb2
        ]

