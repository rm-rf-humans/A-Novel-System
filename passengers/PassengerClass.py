class Passenger:
    def __init__(self,passenger_id, name, age, sex, phone_number, booking_history=None):
        self.__passenger_id = passenger_id
        self.__name = name
        self.age = age
        self.sex = sex 
        self.phone_number = phone_number
        self.booking_history = booking_history if booking_history is not None else []    

    def BookFlight(self, name, ID, Theclass, paid):
        try:
            Booking_details = {"name": name, "theclass": Theclass, "paid": paid}
            self.booking_history.append(Booking_details)

            if paid == 1:
                print("You have booked your flight!")
            else:
                print("You need to pay first before proceeding")
        except Exception as e:
            print(f"An error occurred while booking the flight: {e}")

    def CancelFlight(self, name):
        try:
            if not self.booking_history:
                print("No bookings available to cancel.")
                return

            for i in self.booking_history:
                if i["name"] == name:
                    self.booking_history.remove(i)
                    print("The flight has been cancelled.")
                    return

            print(f"No booking found for {name}.")
        except Exception as e:
            print(f"An error occurred while canceling the flight: {e}")

    def getinfo(self):
        try:
            print(f"Passenger name: {self.__name}\nPassenger ID: {self.__passenger_id}")
        except Exception as e:
            print(f"An error occurred while retrieving passenger info: {e}")


    def ViewBookingDetails(self):
        try:
            print(self.__passenger_id)
            print(self.__name)
            print(self.age)
            print(self.sex)
            print(self.phone_number)
        except Exception as e:
            print(f"An error occurred while viewing booking details: {e}")


passenger = Passenger(passenger_id=1, name="moatassem", age=18, sex="Male", phone_number="9999")
passenger.BookFlight("moatassem",105 , "economy", True ) #this is not the data appearing when you call the (ViewBookingDetails) method
passenger.ViewBookingDetails()
