import unittest
from baggage.Baggage import Baggage
from baggage.BaggageFeeCalc import BaggageFeeCalculator

class TestBaggage(unittest.TestCase):

    def test_baggage_under_limit(self):
        bag = Baggage("John Doe", 18)
        fee = bag.calculate_fee()
        self.assertEqual(fee, 0)

    def test_baggage_over_limit(self):
        bag = Baggage("John Doe", 25)
        fee = bag.calculate_fee()
        self.assertEqual(fee, 50)

    def test_fee_calculator(self):
        calc = BaggageFeeCalculator()
        self.assertEqual(calc.calculate_fee(25), 50)
        self.assertTrue(calc.within_limit(20))
        self.assertFalse(calc.within_limit(21))

if __name__ == '__main__':
    unittest.main()
