import unittest
from unittest.mock import MagicMock
from utilities.Feedback import Feedback
from passengers.PassengerClass import Passenger
from flights.Flight import Flight

class TestFeedback(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.passenger = MagicMock(spec=Passenger)
        self.flight = MagicMock(spec=Flight)
        self.feedback = Feedback(1, self.passenger, self.flight, 5, "Good flight.")

    def test_valid_feedback(self):
        """Test valid feedback submission."""
        self.feedback.rating = 8
        self.assertTrue(self.feedback.submit_feedback())

    def test_invalid_feedback(self):
        """Test invalid feedback submission."""
        self.feedback.rating = 15
        self.assertFalse(self.feedback.submit_feedback())

    def test_feedback_storage(self):
        """Test that feedback is stored correctly."""
        self.feedback.rating = 7
        self.feedback.submit_feedback()
        self.assertEqual(len(Feedback.all_feedback), 1)

    def test_get_all_feedback(self):
        """Test retrieval of all feedback."""
        self.feedback.rating = 9
        self.feedback.submit_feedback()
        all_feedback = Feedback.get_all_feedback()
        self.assertGreater(len(all_feedback), 0)

if __name__ == "__main__":
    unittest.main()
