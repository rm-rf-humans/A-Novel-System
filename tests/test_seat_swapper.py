import unittest
from utilities.seat_swap import SeatSwapper, Socializer, TallPassenger, EcoPassenger

class TestSeatSwapper(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.system = SeatSwapper()
        self.socializer = Socializer("Alice", "10A", "Networking", "Tech")
        self.tall_passenger = TallPassenger("Bob", "30A", "Comfort", 190)
        self.eco_passenger = EcoPassenger("Charlie", "20B", "Eco-Friendly")

    def test_add_passenger(self):
        """Test adding a passenger."""
        self.system.add_passenger(self.socializer)
        self.assertIn(self.socializer, self.system._passengers)

    def test_seat_assignment(self):
        """Test that passengers are assigned seats based on preference."""
        self.system.add_passenger(self.socializer)
        self.system.add_passenger(self.tall_passenger)
        self.system.add_passenger(self.eco_passenger)

        self.system.assign_seats()

        self.assertNotEqual(self.socializer.get_seat(), "10A")  # Seat should be swapped
        self.assertNotEqual(self.tall_passenger.get_seat(), "30A")
        self.assertIn(self.eco_passenger.get_seat(), ["10A", "10B", "10C", "10D"])  # Networking Zone
        self.assertIn(self.tall_passenger.get_seat(), ["40A", "40B", "40C", "40D"])  # Comfort Zone

    def test_get_passenger_data(self):
        """Test that passenger data is retrieved correctly."""
        self.system.add_passenger(self.socializer)
        self.system.add_passenger(self.tall_passenger)

        data = self.system.get_passenger_data()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["name"], "Alice")
        self.assertEqual(data[1]["name"], "Bob")

    def test_get_available_seats(self):
        """Test retrieval of available seats."""
        available_seats = self.system.get_available_seats()
        self.assertIn("Networking", available_seats)
        self.assertIn("Quiet", available_seats)

    def test_ecofriendly_meal_recommendation(self):
        """Test that eco-friendly meals are recommended correctly."""
        self.system.add_passenger(self.eco_passenger)
        self.eco_passenger.recommend_meal()  # Should recommend a meal
