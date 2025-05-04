import random

class Passenger:
    def __init__(self, name, seat, preference):
        self.__name = name        
        self.__seat = seat        
        self.__preference = preference 

    def get_name(self):
        return self.__name

    def get_seat(self):
        return self.__seat

    def get_preference(self):
        return self.__preference

    def set_name(self, name):
        self.__name = name

    def set_seat(self, seat):
        self.__seat = seat

    def set_preference(self, preference):
        self.__preference = preference

    def swap_seat(self, new_seat):
        print(f"{self.__name} swapped seat {self.__seat} to {new_seat}")
        self.__seat = new_seat

    def show_details(self):
        print(f"Passenger: {self.__name} | Seat: {self.__seat} | Preference: {self.__preference}")

class Socializer(Passenger):
    def __init__(self, name, seat, preference, interest):
        super().__init__(name, seat, preference)
        self.__interest = interest  

    def get_interest(self):
        return self.__interest

    def set_interest(self, interest):
        self.__interest = interest

class Sleeper(Passenger):
    def __init__(self, name, seat, preference, noise_level):
        super().__init__(name, seat, preference)
        self.__noise_level = noise_level  

    def get_noise_level(self):
        return self.__noise_level

    def set_noise_level(self, noise_level):
        self.__noise_level = noise_level

class Worker(Passenger):
    def __init__(self, name, seat, preference, needs_power):
        super().__init__(name, seat, preference)
        self.__needs_power = needs_power  

    def get_needs_power(self):
        return self.__needs_power

    def set_needs_power(self, needs_power):
        self.__needs_power = needs_power

class TallPassenger(Passenger):
    def __init__(self, name, seat, preference, height):
        super().__init__(name, seat, preference)
        self.__height = height  

    def get_height(self):
        return self.__height

    def set_height(self, height):
        self.__height = height

class EcoPassenger(Passenger):
    def __init__(self, name, seat, preference):
        super().__init__(name, seat, preference)
        self.__meals = [ 
                        "Plant-Based Wrap", "Organic Salad Bowl", "Sustainable Fish Meal", "Locally Sourced Vegan Dish"
                        ]

    def get_meals(self):
        return self.__meals

    def set_meals(self, meals):
        self.__meals = meals

    def recommend_meal(self):
        try:
            if not self.__meals:
                raise ValueError("No eco meals available.")
            meal = random.choice(self.__meals)
            print(f"{self.get_name()}, AI recommends the eco-friendly meal: {meal}.")
        except Exception as e:
            print(f"Meal recommendation error for {self.get_name()}: {e}")

class SeatSwapper:
    def __init__(self):
        self.__seats = {
                "Networking": ["10A", "10B", "10C", "10D"],
                "Quiet": ["20A", "20B", "20C", "20D"],
                "Work": ["30A", "30B", "30C", "30D"],
                "Legroom": ["40A", "40B", "40C", "40D"]
                }
        self.__passengers = []

    def add_passenger(self, passenger):
        try:
            if not isinstance(passenger, Passenger):
                raise TypeError("Only Passenger instances can be added.")
            self.__passengers.append(passenger)
        except TypeError as e:
            print(f"Error: {e}")

    def assign_seats(self):
        for passenger in self.__passengers:
            try:
                preference = passenger.get_preference()
                zone = self.__get_zone(preference)

                if zone in self.__seats and self.__seats[zone]:
                    new_seat = self.__seats[zone].pop(0)
                    passenger.swap_seat(new_seat)
                    print(f"{passenger.get_name()} assigned to {new_seat} in {zone} zone.")
                else:
                    raise ValueError(f"No available seats in {zone} zone.")
            except Exception as e:
                print(f"Seat assignment error for {passenger.get_name()}: {e}")

    def show_available_seats(self):
        print("\nAvailable Seats:")
        try:
            for zone, seats in self.__seats.items():
                seat_list = ', '.join(seats) if seats else 'No available seats'
                print(f"- {zone} Zone: {seat_list}")
        except Exception as e:
            print(f"Error showing available seats: {e}")

    def __get_zone(self, preference):
        zones = {
                "Networking": "Networking",
                "Sleep": "Quiet",
                "Work": "Work",
                "Comfort": "Legroom",
                "Eco-Friendly": "Networking"
                }
        return zones.get(preference, "Networking")

    def show_details(self):
        try:
            for passenger in self.__passengers:
                passenger.show_details()
                if isinstance(passenger, EcoPassenger):
                    passenger.recommend_meal()
        except Exception as e:
            print(f"Error displaying passenger details: {e}")

if __name__ == "__main__":
    try:
        system = SeatSwapper()

        system.add_passenger(Socializer("ELSISY", "12A", "Networking", "bridges"))
        system.add_passenger(Socializer("Amr", "14B", "Networking", "Tech"))
        system.add_passenger(TallPassenger("cristiano ronaldo", "55E", "Comfort", 190))
        system.add_passenger(EcoPassenger("muslimano ronaldo ", "18C", "Eco-Friendly"))

        system.assign_seats()
        system.show_details()
        system.show_available_seats()
    except Exception as e:
        print(f"Unexpected error in the system: {e}")
