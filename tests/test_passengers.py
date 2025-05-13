import unittest
from passengers.PassengerClass import Passenger
from passengers.ticket import Ticket, TicketProxy

class TestPassengerTicket(unittest.TestCase):

    def test_booking(self):
        p = Passenger(1, "Bruce", 30, "Male", "9999")
        result = p.book_flight("Economy", True)
        self.assertEqual(result, "Booking confirmed.")
        self.assertEqual(len(p.booking_history), 1)

    def test_ticket_generation(self):
        t = Ticket(101, "Bruce", "FL123", 12, True)
        self.assertEqual(t.generate_ticket(), "Ticket generated for Bruce.")

    def test_ticket_proxy_change_seat(self):
        t = Ticket(102, "Clark", "FL999", 7, True)
        proxy = TicketProxy(t)
        msg = proxy.change_seat(21)
        self.assertEqual(msg, "Seat changed to 21")

    def test_ticket_cancel(self):
        t = Ticket(103, "Diana", "FL321", 5, True)
        proxy = TicketProxy(t)
        self.assertEqual(proxy.cancel_ticket(), "Ticket 103 canceled.")

if __name__ == '__main__':
    unittest.main()
