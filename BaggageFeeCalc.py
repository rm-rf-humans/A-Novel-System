class Baggage:
    def __init__(self, weight, limit, Fee_kg):
        self.weight = weight
        self.limit = limit
        self.Fee_kg = Fee_kg

    def fee(self):
        return max(0, (self.weight - self.limit) * self.Fee_kgkg)

    def within_limit(self):
        return self.weight <= self.limit

if __name__ == "__main__":
    bag = Baggage(25, 20, 10)
    if bag.within_limit():
        print("No extra fee.")
    else:
        print(f"Extra fee: {bag.fee():.2f}")
