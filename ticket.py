class Ticket:
    def __init__(self,ticket_id,passenger,flight,seat_number,payment_statues):
        self.ticket_id = ticket_id
        self.passenger = passenger
        self.flight = flight
        self.seat_number =  seat_number
        self.payment_statues = payment_statues
        self.ticket_details={"ticket_id": ticket_id, "passenger":passenger,"flight": flight,"seat_number":seat_number,"payment_statues":payment_statues }
    def generate_ticket(self):
        if self.payment_statues ==1:
            print("ticket")
        else:
            ("you need to pay for the ticket first\n")

    def cancel_ticket(self):
        self.ticket_details.remove()
    def change_seat(self, new_seat:None):
        if new_seat:
            self.seat_number = new_seat
            print(f"the seat has been changed to: {new_seat}")

        
