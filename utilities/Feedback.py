from typing import List
from passengers.PassengerClass import Passenger
from flights.Flight import Flight


class Feedback:
    all_feedback: List[dict] = []

    def __init__(self, feedback_id: int, passenger: Passenger, flight: Flight, rating: int, comment: str):
        self.feedback_id = feedback_id
        self.passenger = passenger
        self.flight = flight
        self.rating = rating
        self.comment = comment

    def is_valid(self) -> bool:
        return 0 <= self.rating <= 10

    def submit_feedback(self) -> bool:
        """Store the feedback if valid."""
        if self.is_valid():
            Feedback.all_feedback.append({
                "id": self.feedback_id,
                "passenger": self.passenger,
                "flight": self.flight,
                "rating": self.rating,
                "comment": self.comment
            })
            return True
        return False

    @classmethod
    def get_all_feedback(cls) -> List[dict]:
        return cls.all_feedback
