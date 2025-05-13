class BaggageFeePolicy:
    _instance = None

    def __new__(cls, limit=20, fee_per_kg=10):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.limit = limit
            cls._instance.fee_per_kg = fee_per_kg
        return cls._instance

    def get_limit(self):
        return self.limit

    def get_fee_per_kg(self):
        return self.fee_per_kg


class BaggageFeeCalculator:
    def __init__(self):
        self.policy = BaggageFeePolicy()

    def calculate_fee(self, weight):
        over_limit = max(0, weight - self.policy.get_limit())
        return over_limit * self.policy.get_fee_per_kg()

    def within_limit(self, weight):
        return weight <= self.policy.get_limit()


class BaggageFeeCalculatorProxy:
    def __init__(self):
        self.calculator = BaggageFeeCalculator()

    def calculate_fee(self, weight):
        return self.calculator.calculate_fee(weight)

    def get_limit(self):
        return self.calculator.policy.get_limit()

