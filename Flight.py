class Flight:
    def __init__(self,flight_id, airline, source, destination, departure_time, arrival_time,date, available_seats):
        self.flight_id = flight_id
        self.airline = airline
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.available_seats = available_seats
        self.date = date

        self.flighdetails={"flight id": flight_id, "airline: ": airline, "source": source , "destination" : destination,
                      "departure_time" : departure_time, "arrival_time": arrival_time, "available_seats": available_seats
                      ,"date": date}
        

    def update_flight_schedule(self,new_date = None,new_departure_time= None, new_arrival_time= None):
           if new_date:
            self.date = new_date
            self.flighdetails ["date"]=new_date
            print(f"flight date is updated to {new_date}") 
           
            if new_departure_time:
                 self.departure_time = new_departure_time
                 self.flighdetails ["departure_time"] = new_departure_time
                 print(f"departure time updated to {new_departure_time}")

           
            if new_arrival_time:
                 self.arrival_time = new_arrival_time
                 self.flighdetails ["arrival_time"] = new_arrival_time
                 print(f"new arrival time is updated to {new_arrival_time}")

            if new_arrival_time and new_departure_time:
                 if new_arrival_time<= new_departure_time:
                  print("Error: departure time must be before arrival time")


    def check_availability(self):
        if self.available_seats != 0:
            print(f"{self.available_seats} seats is available")

        else :
            print("no seats are available for this flight")
    
    
    def flightschedule(self):
        print(f" departure time: {self.departure_time}\n arrival time: {self.arrival_time}")


flight1 = Flight(489, "egypt air", "egypt", "denmark","16:00", "23:30", "16/10/2025",26)
flight1.update_flight_schedule("6/6/2006", "15", "23")
# print(flight1.flighdetails)
# flight1.check_availability()
flight1.flightschedule()

