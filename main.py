import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QSpinBox, QDoubleSpinBox, QGroupBox
from PyQt5.QtCore import Qt
from datetime import datetime

from passengers.PassengerClass import Passenger
from flights.Flight import Flight
from utilities.Feedback import Feedback
from utilities.ReminderEmailSender import ReminderEmailSender
from utilities.seat_swap import Passenger, Socializer, TallPassenger, EcoPassenger, SeatSwapper 
from baggage.Baggage import Baggage


class SeatSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initial available seats
        self.available_seats = {
            "1A": True, "1B": True, "1C": True, "1D": True,
            "2A": True, "2B": True, "2C": True, "2D": True,
            "3A": True, "3B": True, "3C": True, "3D": True,
            "4A": True, "4B": True, "4C": True, "4D": True,
        }

        self.selected_seat = None  # Track selected seat
        self.seat_swapper = SeatSwapper()  # Initialize seat swapper
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title/Instruction
        self.title_label = QLabel("Select Your Seat", self)
        layout.addWidget(self.title_label)

        # Seat Map Layout (Grid)
        self.grid_layout = QGridLayout()
        self.create_seat_buttons()
        
        layout.addLayout(self.grid_layout)

        # Display selected seat
        self.selected_seat_label = QLabel("Selected Seat: None", self)
        layout.addWidget(self.selected_seat_label)

        # Seat selection form (for user details)
        self.details_form = QFormLayout()
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Your Name")
        self.details_form.addRow("Name: ", self.name_input)

        self.flight_combo = QComboBox(self)
        self.flight_combo.addItems(["Flight 1", "Flight 2", "Flight 3"])  # Flight options
        self.details_form.addRow("Select Flight: ", self.flight_combo)

        self.age_input = QSpinBox(self)
        self.age_input.setRange(18, 100)  # Age range
        self.details_form.addRow("Age: ", self.age_input)

        # Baggage information section
        baggage_group = QGroupBox("Baggage Information")
        baggage_layout = QFormLayout()
        
        self.baggage_weight = QDoubleSpinBox(self)
        self.baggage_weight.setRange(0, 50)  # Weight range in kg
        self.baggage_weight.setDecimals(1)
        self.baggage_weight.setSuffix(" kg")
        self.baggage_weight.setValue(15.0)  # Default weight
        baggage_layout.addRow("Baggage Weight:", self.baggage_weight)
        
        self.check_baggage_button = QPushButton("Check Baggage Fee", self)
        self.check_baggage_button.clicked.connect(self.check_baggage)
        baggage_layout.addRow(self.check_baggage_button)
        
        self.baggage_status = QLabel("No baggage checked yet", self)
        baggage_layout.addRow(self.baggage_status)
        
        baggage_group.setLayout(baggage_layout)
        
        layout.addLayout(self.details_form)
        layout.addWidget(baggage_group)

        # Submit button for booking the seat
        self.submit_button = QPushButton("Book Seat", self)
        self.submit_button.clicked.connect(self.book_seat)
        layout.addWidget(self.submit_button)

        # Swap Seat button
        self.swap_button = QPushButton("Swap Seat", self)
        self.swap_button.clicked.connect(self.swap_seat)
        layout.addWidget(self.swap_button)

        self.setLayout(layout)
        self.setWindowTitle('Seat Selection & Booking')
        self.setGeometry(100, 100, 600, 700)
        self.show()

    def create_seat_buttons(self):
        row = 0
        col = 0

        for seat, available in self.available_seats.items():
            seat_button = QPushButton(seat, self)
            seat_button.setFixedSize(50, 50)
            seat_button.setEnabled(available)  
            seat_button.clicked.connect(self.select_seat)
            self.grid_layout.addWidget(seat_button, row, col)
            
            col += 1
            if col > 3:  
                col = 0
                row += 1

    def select_seat(self):
        selected_button = self.sender()  
        selected_seat = selected_button.text()

        if self.available_seats[selected_seat]:  
            self.selected_seat = selected_seat
            self.selected_seat_label.setText(f"Selected Seat: {self.selected_seat}")
            self.available_seats[selected_seat] = False  
            selected_button.setEnabled(False)
        else:
            self.selected_seat_label.setText("Seat already taken, please select another.")

    def check_baggage(self):
        passenger_name = self.name_input.text()
        weight = self.baggage_weight.value()
        
        if passenger_name == "":
            self.baggage_status.setText("Please enter your name first.")
            return
        
        # Create baggage instance
        baggage = Baggage(passenger_name, weight)
        
        # Calculate fee
        baggage.calculate_fee()
        
        # Update status
        self.baggage_status.setText(baggage.get_fee_summary())

    def book_seat(self):
        if self.selected_seat is None:
            self.selected_seat_label.setText("No seat selected. Please select a seat first.")
            return
        
        passenger_name = self.name_input.text()
        flight = self.flight_combo.currentText()
        age = self.age_input.value()
        baggage_weight = self.baggage_weight.value()

        if passenger_name == "":
            self.selected_seat_label.setText("Please enter your name.")
            return

        passenger = Passenger(name=passenger_name, seat=self.selected_seat, preference="Networking")  # Default preference
        
        # Handle baggage
        baggage = Baggage(passenger_name, baggage_weight)
        baggage.calculate_fee()
        baggage_fee = baggage.baggage_fee
        
        self.seat_swapper.add_passenger(passenger)

        confirmation_text = f"Booking confirmed for {passenger_name} on {flight} with seat {self.selected_seat}"
        
        # Add baggage information to confirmation
        if baggage_fee > 0:
            confirmation_text += f"\nBaggage fee: ${baggage_fee} (Weight: {baggage_weight}kg)"
        else:
            confirmation_text += f"\nNo baggage fee (Weight: {baggage_weight}kg)"
        
        self.selected_seat_label.setText(confirmation_text)

        ReminderEmailSender().send_reminder(passenger_name, flight)

    def swap_seat(self):
        self.seat_swapper.assign_seats()
        passenger_data = self.seat_swapper.get_passenger_data()

        swap_message = "\n".join([f"{data['name']} -> Seat {data['seat']} (Preference: {data['preference']})"
                                  for data in passenger_data])
        self.selected_seat_label.setText(f"Seat Swap Complete:\n{swap_message}")


class FeedbackWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Provide Your Feedback", self)
        layout.addWidget(self.title_label)

        # Feedback Form
        self.feedback_input = QLineEdit(self)
        self.feedback_input.setPlaceholderText("Enter your feedback here...")
        layout.addWidget(self.feedback_input)

        # Submit Button
        self.submit_button = QPushButton("Submit Feedback", self)
        self.submit_button.clicked.connect(self.submit_feedback)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle('Feedback')
        self.setGeometry(100, 100, 400, 200)

    def submit_feedback(self):
        feedback_text = self.feedback_input.text()
        if feedback_text == "":
            self.feedback_input.setText("Please enter feedback.")
        else:
            self.feedback_input.setText("Thank you for your feedback!")


class BaggageInfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Baggage Policy Information", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Policy information
        from baggage.BaggageFeeCalc import BaggageFeeCalculatorProxy
        calculator = BaggageFeeCalculatorProxy()
        
        policy_info = QLabel(f"""
        Baggage Policy:
        - Weight limit: {calculator.get_limit()} kg
        - Fee per kg overweight: ${calculator.calculator.policy.get_fee_per_kg()}
        
        Excess baggage fees will be charged for any baggage exceeding the weight limit.
        """, self)
        policy_info.setAlignment(Qt.AlignLeft)
        layout.addWidget(policy_info)

        self.setLayout(layout)
        self.setWindowTitle('Baggage Policy')
        self.setGeometry(100, 100, 400, 200)


if __name__ == "__main__":
    app = QApplication(sys.argv)  

    seat_window = SeatSelectionWindow()
    seat_window.show()

    feedback_window = FeedbackWindow()
    feedback_window.show()
    
    baggage_info_window = BaggageInfoWindow()
    baggage_info_window.show()

    sys.exit(app.exec_())