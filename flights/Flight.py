class Flight:
    def __init__(self, flight_id, airline, source, destination, departure_time, arrival_time, date, available_seats):
        self.flight_id = flight_id
        self.airline = airline
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.date = date
        self.available_seats = available_seats

    def to_dict(self):
        return {
            "flight_id": self.flight_id,
            "airline": self.airline,
            "source": self.source,
            "destination": self.destination,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "date": self.date,
            "available_seats": self.available_seats
        }

    def check_availability(self):
        return self.available_seats > 0

    def schedule_summary(self):
        return {
            "departure": self.departure_time,
            "arrival": self.arrival_time
        }

    def update_schedule(self, new_date=None, new_departure_time=None, new_arrival_time=None):
        if new_departure_time and new_arrival_time and new_arrival_time <= new_departure_time:
            raise ValueError("Departure time must be before arrival time.")

        if new_date:
            self.date = new_date
        if new_departure_time:
            self.departure_time = new_departure_time
        if new_arrival_time:
            self.arrival_time = new_arrival_time


class FlightScheduleProxy:
    """Proxy to control and log updates to flight schedules"""
    def __init__(self, flight):
        self._flight = flight

    def update_schedule(self, *args, **kwargs):
        # Here you could add logging, access control, etc.
        return self._flight.update_schedule(*args, **kwargs)

    def get_schedule(self):
        return self._flight.schedule_summary()
