import os
import re
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Union
import unittest
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AirlineAI")

class Singleton(type):

    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AIAssistant(metaclass=Singleton):
    def __init__(self):
        self.name = "AirlineAI"
        self.conversation_history = []
        self.intent_recognizer = IntentRecognizer()
        self.response_generator = ResponseGenerator()
        logger.info(f"{self.name} Assistant initialized.")
    
    def process_query(self, query: str) -> str:
        try:
            self.conversation_history.append({"role": "user", "message": query})
            
            intent, entities = self.intent_recognizer.recognize_intent(query)
            
            response = self.response_generator.generate_response(intent, entities, self.conversation_history)
            
            self.conversation_history.append({"role": "assistant", "message": response})
            
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I apologize, but I encountered an error processing your request. Please try again. Error: {str(e)}"


class IntentRecognizer:
    def __init__(self):
        self.intent_patterns = {
            "greeting": [r"hello", r"hi", r"hey", r"greetings", r"good\s+(morning|afternoon|evening)"],
            "booking": [r"book", r"reserve", r"flight", r"ticket", r"booking", r"reservation"],
            "cancel": [r"cancel", r"refund", r"cancelation"],
            "flight_status": [r"status", r"delay", r"on\s+time", r"departure", r"arrival", r"track"],
            "baggage": [r"baggage", r"luggage", r"bag", r"weight", r"allowance"],
            "help": [r"help", r"assistance", r"support", r"guide"],
            "farewell": [r"bye", r"goodbye", r"see\s+you", r"farewell"]
        }
    
    def recognize_intent(self, query: str) -> tuple:
        query = query.lower()
        
        entities = self._extract_entities(query)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent, entities
        
        return "general_inquiry", entities
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        entities = {}
        
        flight_number_match = re.search(r'([A-Z]{2}|[A-Z]\d|\d[A-Z])\s*(\d{1,4})', query, re.IGNORECASE)
        if flight_number_match:
            entities["flight_number"] = flight_number_match.group(0)
        
        date_patterns = [
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(st|nd|rd|th)?(\s*,\s*|\s+)(\d{4})'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, query, re.IGNORECASE)
            if date_match:
                entities["date"] = date_match.group(0)
                break
        
        common_cities = ["new york", "los angeles", "chicago", "toronto", "london", "paris", 
                         "tokyo", "sydney", "dubai", "beijing", "delhi", "miami"]
        
        for city in common_cities:
            if city.lower() in query.lower():
                if "origin" not in entities:
                    entities["origin"] = city
                elif "destination" not in entities:
                    entities["destination"] = city
        
        return entities


class ResponseGenerator:
    def __init__(self):
        self.templates = {
            "greeting": [
                "Hello! Welcome to our airline assistant. How can I help you today?",
                "Hi there! I'm your airline AI assistant. What can I do for you?",
                "Greetings! How may I assist with your travel plans today?"
            ],
            "booking": [
                "I'd be happy to help you book a flight. Could you please provide your departure city, destination, and travel dates?",
                "Let's get your flight booked. Where will you be flying from and to, and when do you plan to travel?",
                "I can assist with your flight booking. Please share your travel details including origin, destination, and dates."
            ],
            "cancel": [
                "I understand you want to cancel a reservation. Could you please provide your booking reference or ticket number?",
                "I can help you with cancellation. Do you have your booking confirmation code handy?",
                "To process your cancellation, I'll need your booking details. Could you share your reservation number?"
            ],
            "flight_status": [
                "I can check the status of your flight. Could you provide the flight number and date?",
                "Let me look up that flight status for you. What's the flight number and date of travel?",
                "To check your flight status, I'll need the flight number and travel date."
            ],
            "baggage": [
                "For baggage information, could you tell me which airline and class of service you're flying?",
                "Baggage policies vary by airline and ticket type. Which airline are you flying with, and what type of ticket do you have?",
                "I can help with baggage questions. Please specify your airline and travel class for accurate information."
            ],
            "help": [
                "I can help with booking flights, checking flight status, baggage information, and more. What do you need assistance with?",
                "As your airline assistant, I can provide information on bookings, cancellations, flight status, and baggage. What would you like to know?",
                "I'm here to help with all your airline needs. You can ask about bookings, flight status, baggage, or any other travel questions."
            ],
            "farewell": [
                "Thank you for using our airline assistant. Have a great day!",
                "It was a pleasure assisting you. Safe travels!",
                "Thank you for chatting with me today. Enjoy your journey!"
            ],
            "general_inquiry": [
                "I'm not sure I understand your request. Could you please provide more details or rephrase your question?",
                "I'd like to help you better. Could you give me more specific information about your inquiry?",
                "I'm having trouble understanding your request. Could you please clarify what you're looking for?"
            ]
        }
    
    def generate_response(self, intent: str, entities: Dict[str, Any], conversation_history: List[Dict[str, str]]) -> str:
        import random
        
        base_response = random.choice(self.templates[intent])
        
        if intent == "flight_status" and "flight_number" in entities:
            flight_info = self._get_mock_flight_info(entities["flight_number"])
            return f"{base_response} For flight {entities['flight_number']}, {flight_info}"
        
        elif intent == "booking" and ("origin" in entities or "destination" in entities):
            origin = entities.get("origin", "[origin]")
            destination = entities.get("destination", "[destination]")
            return f"{base_response} I see you're interested in traveling from {origin} to {destination}."
        
        return base_response
    
    def _get_mock_flight_info(self, flight_number: str) -> str:
        import random
        statuses = ["on time", "delayed by 15 minutes", "delayed by 30 minutes", "boarding", "departed"]
        return random.choice(statuses)


class Flight:
    def __init__(self, flight_id: str, airline: str, origin: str, destination: str, 
                 departure_time: datetime.time, arrival_time: datetime.time, 
                 date: datetime.date, available_seats: int):
        self.flight_id = flight_id
        self.airline = airline
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.date = date
        self.available_seats = available_seats


class FlightScheduleProxy:
    def __init__(self, flight: Flight):
        self._flight = flight
    
    def get_flight_details(self) -> Dict[str, Any]:
        return {
            "flight_id": self._flight.flight_id,
            "airline": self._flight.airline,
            "origin": self._flight.origin,
            "destination": self._flight.destination,
            "departure": self._flight.departure_time.strftime('%H:%M'),
            "arrival": self._flight.arrival_time.strftime('%H:%M'),
            "date": self._flight.date.strftime('%Y-%m-%d'),
            "available_seats": self._flight.available_seats
        }
    
    def check_availability(self) -> bool:
        return self._flight.available_seats > 0
    
    def book_seat(self) -> bool:
        if self._flight.available_seats > 0:
            self._flight.available_seats -= 1
            return True
        return False


class Reservation:
    def __init__(self, reservation_id: str, passenger_name: str, flight_id: str, 
                 seat_number: str, booking_date: datetime.date):
        self.reservation_id = reservation_id
        self.passenger_name = passenger_name
        self.flight_id = flight_id
        self.seat_number = seat_number
        self.booking_date = booking_date
        self.status = "Confirmed"
    
    def cancel(self) -> bool:
        if self.status == "Confirmed":
            self.status = "Cancelled"
            return True
        return False


class ReservationManager(metaclass=Singleton):
    def __init__(self):
        self.reservations: Dict[str, Reservation] = {}
        self.flights: Dict[str, Flight] = {}
        self.flight_proxies: Dict[str, FlightScheduleProxy] = {}
        self._next_reservation_id = 1000
        
        self._initialize_sample_flights()
    
    def _initialize_sample_flights(self):
        sample_flights = [
            Flight("AA101", "American Airlines", "New York", "Los Angeles", 
                   datetime.time(8, 0), datetime.time(11, 30), 
                   datetime.date.today() + datetime.timedelta(days=1), 120),
            Flight("DL202", "Delta Airlines", "Chicago", "Miami", 
                   datetime.time(9, 15), datetime.time(12, 45), 
                   datetime.date.today() + datetime.timedelta(days=2), 90),
            Flight("UA303", "United Airlines", "Boston", "San Francisco", 
                   datetime.time(14, 30), datetime.time(18, 0), 
                   datetime.date.today() + datetime.timedelta(days=3), 75)
        ]
        
        for flight in sample_flights:
            self.add_flight(flight)
    
    def add_flight(self, flight: Flight):
        self.flights[flight.flight_id] = flight
        self.flight_proxies[flight.flight_id] = FlightScheduleProxy(flight)
    
    def get_flight(self, flight_id: str) -> Optional[FlightScheduleProxy]:
        return self.flight_proxies.get(flight_id)
    
    def list_flights(self, origin: Optional[str] = None, destination: Optional[str] = None, 
                     date: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
        results = []
        
        for flight_id, proxy in self.flight_proxies.items():
            flight = self.flights[flight_id]
            
            if origin and flight.origin.lower() != origin.lower():
                continue
            if destination and flight.destination.lower() != destination.lower():
                continue
            if date and flight.date != date:
                continue
            
            results.append(proxy.get_flight_details())
        
        return results
    
    def create_reservation(self, passenger_name: str, flight_id: str, seat_number: str) -> Optional[str]:
        flight_proxy = self.get_flight(flight_id)
        
        if not flight_proxy:
            logger.error(f"Flight {flight_id} not found")
            return None
        
        if not flight_proxy.check_availability():
            logger.warning(f"No seats available on flight {flight_id}")
            return None
        
        if not flight_proxy.book_seat():
            logger.warning(f"Failed to book seat on flight {flight_id}")
            return None
        
        reservation_id = f"RES{self._next_reservation_id}"
        self._next_reservation_id += 1
        
        reservation = Reservation(
            reservation_id=reservation_id,
            passenger_name=passenger_name,
            flight_id=flight_id,
            seat_number=seat_number,
            booking_date=datetime.date.today()
        )
        
        self.reservations[reservation_id] = reservation
        logger.info(f"Created reservation {reservation_id} for {passenger_name} on flight {flight_id}")
        
        return reservation_id
    
    def get_reservation(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        reservation = self.reservations.get(reservation_id)
        
        if not reservation:
            return None
        
        return {
            "reservation_id": reservation.reservation_id,
            "passenger_name": reservation.passenger_name,
            "flight_id": reservation.flight_id,
            "seat_number": reservation.seat_number,
            "booking_date": reservation.booking_date.strftime('%Y-%m-%d'),
            "status": reservation.status
        }
    
    def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = self.reservations.get(reservation_id)
        
        if not reservation:
            logger.warning(f"Reservation {reservation_id} not found")
            return False
        
        if reservation.cancel():
            logger.info(f"Cancelled reservation {reservation_id}")
            return True
        
        logger.warning(f"Failed to cancel reservation {reservation_id}")
        return False

class Command(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        pass


class BookFlightCommand(Command):
    def __init__(self, reservation_manager: ReservationManager, passenger_name: str, 
                 flight_id: str, seat_number: str):
        self.reservation_manager = reservation_manager
        self.passenger_name = passenger_name
        self.flight_id = flight_id
        self.seat_number = seat_number
        self.reservation_id = None
    
    def execute(self) -> Optional[str]:
        self.reservation_id = self.reservation_manager.create_reservation(
            self.passenger_name, self.flight_id, self.seat_number
        )
        return self.reservation_id
    
    def undo(self) -> bool:
        if self.reservation_id:
            return self.reservation_manager.cancel_reservation(self.reservation_id)
        return False


class CancelReservationCommand(Command):
    def __init__(self, reservation_manager: ReservationManager, reservation_id: str):
        self.reservation_manager = reservation_manager
        self.reservation_id = reservation_id
        self.reservation_details = None
    
    def execute(self) -> bool:
        self.reservation_details = self.reservation_manager.get_reservation(self.reservation_id)
        
        if not self.reservation_details:
            return False
        
        return self.reservation_manager.cancel_reservation(self.reservation_id)
    
    def undo(self) -> bool:
        if self.reservation_details:
            logger.info(f"Would restore reservation {self.reservation_id}")
            return True
        return False


class TestAIAssistant(unittest.TestCase):
    def setUp(self):
        Singleton._instances = {}
        self.assistant = AIAssistant()
    
    def test_singleton_pattern(self):
        another_instance = AIAssistant()
        self.assertIs(self.assistant, another_instance, "AIAssistant should be a singleton")
    
    def test_greeting_intent(self):
        response = self.assistant.process_query("Hello there")
        self.assertIn("Hello", response, "Response should include a greeting")
    
    def test_booking_intent(self):
        response = self.assistant.process_query("I want to book a flight")
        self.assertIn("book", response.lower(), "Response should address booking")
    
    def test_flight_status_with_entity(self):
        response = self.assistant.process_query("What's the status of flight AA123?")
        self.assertIn("AA123", response, "Response should include the flight number")


class TestReservationSystem(unittest.TestCase):
    def setUp(self):
        Singleton._instances = {}
        self.reservation_manager = ReservationManager()
    
    def test_flight_listing(self):
        flights = self.reservation_manager.list_flights()
        self.assertGreater(len(flights), 0, "Should have sample flights available")
    
    def test_create_reservation(self):
        flights = self.reservation_manager.list_flights()
        flight_id = flights[0]["flight_id"]
        
        reservation_id = self.reservation_manager.create_reservation(
            passenger_name="Test User",
            flight_id=flight_id,
            seat_number="1A"
        )
        
        self.assertIsNotNone(reservation_id, "Should return a reservation ID")
        
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["passenger_name"], "Test User")
        self.assertEqual(reservation["flight_id"], flight_id)
    
    def test_cancel_reservation(self):
        flights = self.reservation_manager.list_flights()
        flight_id = flights[0]["flight_id"]
        
        reservation_id = self.reservation_manager.create_reservation(
            passenger_name="Test User",
            flight_id=flight_id,
            seat_number="1B"
        )
        
        success = self.reservation_manager.cancel_reservation(reservation_id)
        self.assertTrue(success, "Should successfully cancel reservation")
        
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "Cancelled")


class TestCommandPattern(unittest.TestCase):
    
    def setUp(self):
        Singleton._instances = {}
        self.reservation_manager = ReservationManager()
    
    def test_book_flight_command(self):
        flights = self.reservation_manager.list_flights()
        flight_id = flights[0]["flight_id"]
        
        command = BookFlightCommand(
            reservation_manager=self.reservation_manager,
            passenger_name="Command User",
            flight_id=flight_id,
            seat_number="2A"
        )
        
        reservation_id = command.execute()
        self.assertIsNotNone(reservation_id, "Should return a reservation ID")
        
        success = command.undo()
        self.assertTrue(success, "Should successfully undo booking")


if __name__ == "__main__":
    assistant = AIAssistant()
    
    # unittest.main()
    
    sample_queries = [
        "Hello, I need some help",
        "I want to book a flight from New York to Los Angeles",
        "What's the status of flight AA101?",
        "What baggage allowance do I have?",
        "Can I cancel my reservation?",
        "Thank you, goodbye"
    ]
    
    print("=== AI Assistant Demo ===")
    for query in sample_queries:
        print(f"\nUser: {query}")
        response = assistant.process_query(query)
        print(f"Assistant: {response}")