from abc import ABC, abstractmethod

class Vehicle(ABC):
    def __init__(self, driver):
        self.driver = driver
        self._rating = 0

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if value >= 1 and value <= 5:
            self._rating = value
        else:
            raise ValueError("Rating must be between 1 and 5")

    @abstractmethod
    def calculate_fare(self, distance):
        pass


class Bike(Vehicle):
    def calculate_fare(self, distance):
        return distance * 15


class Car(Vehicle):
    def calculate_fare(self, distance):
        return distance * 25