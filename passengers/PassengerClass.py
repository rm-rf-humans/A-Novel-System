class PassengerRegistry:
    """Singleton to manage all passengers."""
    _instance = None
    _passengers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_passenger(self, passenger):
        self._passengers[passenger.passenger_id] = passenger

    def get_passenger(self, passenger_id):
        return self._passengers.get(passenger_id)

    def all_passengers(self):
        return list(self._passengers.values())


class Passenger:
    def __init__(self, passenger_id, name, age, sex, phone_number, booking_history=None):
        self.passenger_id = passenger_id
        self.name = name
        self.age = age
        self.sex = sex
        self.phone_number = phone_number
        self.booking_history = booking_history if booking_history else []

        PassengerRegistry().add_passenger(self)

    def book_flight(self, class_type, paid):
        booking = {
            "passenger": self.name,
            "class": class_type,
            "paid": paid
        }
        self.booking_history.append(booking)
        return "Booking confirmed." if paid else "Payment required to complete booking."

    def cancel_flight(self, passenger_name):
        for booking in self.booking_history:
            if booking["passenger"] == passenger_name:
                self.booking_history.remove(booking)
                return "Booking cancelled."
        return "Booking not found."

    def view_info(self):
        return {
            "passenger_id": self.passenger_id,
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "phone_number": self.phone_number,
            "booking_history": self.booking_history
        }
