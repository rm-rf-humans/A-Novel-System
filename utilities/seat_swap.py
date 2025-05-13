import random
from typing import List


class Passenger:
    def __init__(self, name: str, seat: str, preference: str):
        self._name = name
        self._seat = seat
        self._preference = preference

    def get_name(self) -> str:
        return self._name

    def get_seat(self) -> str:
        return self._seat

    def get_preference(self) -> str:
        return self._preference

    def set_seat(self, seat: str):
        self._seat = seat

    def swap_seat(self, new_seat: str):
        self._seat = new_seat


class Socializer(Passenger):
    def __init__(self, name, seat, preference, interest):
        super().__init__(name, seat, preference)
        self._interest = interest


class TallPassenger(Passenger):
    def __init__(self, name, seat, preference, height: int):
        super().__init__(name, seat, preference)
        self._height = height


class EcoPassenger(Passenger):
    def __init__(self, name, seat, preference):
        super().__init__(name, seat, preference)
        self._meals = [
            "Plant-Based Wrap", "Organic Salad Bowl",
            "Sustainable Fish Meal", "Locally Sourced Vegan Dish"
        ]

    def recommend_meal(self) -> str:
        return random.choice(self._meals) if self._meals else "No eco meals available."


class SeatSwapper:
    def __init__(self):
        self._seats = {
            "Networking": ["10A", "10B", "10C", "10D"],
            "Quiet": ["20A", "20B", "20C", "20D"],
            "Work": ["30A", "30B", "30C", "30D"],
            "Legroom": ["40A", "40B", "40C", "40D"]
        }
        self._passengers: List[Passenger] = []

    def add_passenger(self, passenger: Passenger):
        if isinstance(passenger, Passenger):
            self._passengers.append(passenger)

    def assign_seats(self):
        for passenger in self._passengers:
            zone = self._get_zone(passenger.get_preference())
            if self._seats[zone]:
                new_seat = self._seats[zone].pop(0)
                passenger.swap_seat(new_seat)

    def get_passenger_data(self) -> List[dict]:
        return [{
            "name": p.get_name(),
            "seat": p.get_seat(),
            "preference": p.get_preference()
        } for p in self._passengers]

    def get_available_seats(self) -> dict:
        return self._seats

    def _get_zone(self, preference: str) -> str:
        return {
            "Networking": "Networking",
            "Sleep": "Quiet",
            "Work": "Work",
            "Comfort": "Legroom",
            "Eco-Friendly": "Networking"
        }.get(preference, "Networking")
