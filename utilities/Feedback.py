from passengers.PassengerClass import Passenger
from flights.Flight import Flight

class Feedback:
  
    all_feedback = []
  
    def __init__(self,FeedbackNum, Passenger,Flight,rating,comment ):
        self.FeedbackNum = FeedbackNum
        self.Passenger = Passenger
        self.Flight = Flight
        self.rating = rating
        self.comment = comment


    def submitfeedback(self):
        self.rating = print(input("please enter your feedback\n"))
        if self.rating >=0 and self.rating<=10:
            print("thanks for the feedback\n")
            Feedback.all_feedback.append(self.rating)
        else:
            print("invalid feedback\n")

