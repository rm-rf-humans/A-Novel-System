class Passenger:
    def __init__(self,passenger_id, name, age, sex, phone_number, booking_history=None):
        self.passenger_id = passenger_id
        self.name = name
        self.age = age
        self.sex = sex 
        self.phone_number = phone_number
        self.booking_history = booking_history if booking_history is not None else []    

    def BookFlight(self,name, ID,Theclass,paid):
       Booking_details = {"name": name,"theclass": Theclass, "paid": paid}
       self.booking_history.append(Booking_details)

       if paid==1:
        print("You have booked your flight!")
       else:
        print("You need to pay first before proceeding")

    def CancelFlight(self, name):
       for i in self.booking_history:
          if i["name"]== name:
             self.booking_history.remove(i)
             print("the flight has benn cancelled")
             return
          else:
             print(f"no booking found for {name}")
    def ViewBookingDetails(self):
       print(self.passenger_id)
       print(self.name)
       print(self.age)
       print(self.sex)
       print(self.phone_number)


passenger = Passenger(passenger_id=1, name="moatassem", age=18, sex="Male", phone_number="9999")
passenger.BookFlight("moatassem",105 , "economy", True )
passenger.ViewBookingDetails()
