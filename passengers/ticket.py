class Ticket:
    def __init__(self, ticket_id, passenger_name, flight_id, seat_number, payment_status):
        self.ticket_id = ticket_id
        self.passenger = passenger_name
        self.flight = flight_id
        self.seat_number = seat_number
        self.payment_status = payment_status

    def generate_ticket(self):
        return f"Ticket generated for {self.passenger}." if self.payment_status else "Payment required."

    def get_ticket_details(self):
        return {
            "ticket_id": self.ticket_id,
            "passenger": self.passenger,
            "flight": self.flight,
            "seat_number": self.seat_number,
            "payment_status": self.payment_status
        }

    def change_seat(self, new_seat):
        self.seat_number = new_seat
        return f"Seat changed to {new_seat}."


class TicketProxy:
    """Controls access to Ticket modifications"""
    def __init__(self, ticket: Ticket):
        self._ticket = ticket

    def cancel_ticket(self):
        # In real-world scenario, mark it canceled, or remove from registry
        return f"Ticket {self._ticket.ticket_id} canceled."

    def change_seat(self, new_seat):
        if not self._ticket.payment_status:
            return "Cannot change seat. Payment required."
        return self._ticket.change_seat(new_seat)

    def get_ticket_details(self):
        return self._ticket.get_ticket_details()
