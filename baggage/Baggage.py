from baggage.BaggageFeeCalc import BaggageFeeCalculatorProxy

class Baggage:
    def __init__(self, passenger_name, weight):
        self.passenger_name = passenger_name
        self.weight = weight        
        self.baggage_fee = 0
        self.calculator = BaggageFeeCalculatorProxy()

    def check_baggage_weight(self):
        return self.weight <= self.calculator.get_limit()

    def calculate_fee(self):
        self.baggage_fee = self.calculator.calculate_fee(self.weight)
        return self.baggage_fee

    def get_fee_summary(self):
        limit = self.calculator.get_limit()
        if self.check_baggage_weight():
            return f"No extra fee. Weight: {self.weight}kg (Limit: {limit}kg)"
        else:
            return f"Baggage is {self.weight}kg, which exceeds limit of {limit}kg. Fee: ${self.baggage_fee}"

