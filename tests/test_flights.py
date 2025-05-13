import unittest
from flights.CrewMember import CrewMember, CrewRegistry
from flights.Flight import Flight, FlightScheduleProxy

class TestFlights(unittest.TestCase):

    def test_crew_member_creation(self):
        crew = CrewMember(101, "Alice", "Pilot", "alice@example.com")
        self.assertEqual(crew.status, "Available")
        self.assertEqual(crew.view_schedule(), "No assigned flight.")

    def test_assign_flight(self):
        crew = CrewMember(102, "Bob", "Attendant", "bob@example.com")
        crew.assign_flight("FL123")
        self.assertEqual(crew.assigned_flight, "FL123")
        self.assertEqual(crew.status, "On Duty")

    def test_flight_schedule_proxy(self):
        flight = Flight("FL123", "AirCo", "NY", "LA", "10:00", "14:00", "2025-06-06", 5)
        proxy = FlightScheduleProxy(flight)
        proxy.update_schedule(new_departure_time="09:00", new_arrival_time="13:00")
        self.assertEqual(proxy.get_schedule()["departure"], "09:00")

if __name__ == '__main__':
    unittest.main()
