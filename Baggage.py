class Baggage:
    def __init__(self, passenger, weight):
        self.passenger = passenger
        self.weight = weight        
        self.baggage_fee = 0       

    def check_baggage_weight(self):
       
        if self.weight > 20:
            print(f"baggage weight is {self.weight} kg the allowed limit is 20 kg")
        else:
            print("baggage weight is within the allowed limit")
     
    def calculate_fee(self):
     
        if self.weight <= 20:
            self.baggage_fee = 0  
        else:
            self.baggage_fee = (self.weight - 20) * 10 
        print(f"baggage fee: ${self.baggage_fee}")
