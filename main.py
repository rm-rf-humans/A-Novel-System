import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QFileDialog, QTextEdit, QGraphicsDropShadowEffect, QFrame
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from datetime import datetime, time

from passengers.PassengerClass import Passenger as BasePassenger
from passengers.ticket import Ticket, TicketProxy
from flights.Flight import Flight, FlightScheduleProxy
from flights.CrewMember import CrewMember, CrewRegistry
from utilities.Feedback import Feedback
from utilities.ReminderEmailSender import ReminderEmailSender
from utilities.seat_swap import Passenger, Socializer, TallPassenger, EcoPassenger, SeatSwapper 
from baggage.Baggage import Baggage
from ML.Bot import AIAssistant

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
        self.flights = [
        Flight("FL001", "AirExpress", "New York", "Los Angeles", 
               time(8, 0), time(11, 30), datetime.now().date(), 120),
        Flight("FL002", "SkyWings", "Chicago", "Miami", 
               time(9, 15), time(12, 45), datetime.now().date(), 90),
        Flight("FL003", "OceanAir", "Boston", "San Francisco", 
               time(14, 30), time(18, 0), datetime.now().date(), 75)
        ]
    
        # Create proxies for each flight
        self.flight_proxies = [FlightScheduleProxy(flight) for flight in self.flights]
    
        self.ticket_counter = 1000  # Starting ticket number
        self.tickets = {}  # Dictionary to store tickets by ticket_id
 
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        

        # Title/Instruction with modern styling
        self.title_label = QLabel("Select Your Seat", self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9; margin-bottom: 0px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Seat Map Layout (Grid)
        self.grid_layout = QGridLayout()
        self.create_seat_buttons()
        
        layout.addLayout(self.grid_layout)

        # Display selected seat
        self.selected_seat_label = QLabel("Selected Seat: None", self)
        layout.addWidget(self.selected_seat_label)

        # Passenger Type Selection
        passenger_group = QGroupBox("Passenger Type")
        passenger_layout = QFormLayout()
        
        self.passenger_type = QComboBox(self)
        self.passenger_type.addItems(["Regular", "Socializer", "Tall", "Eco-Friendly"])
        self.passenger_type.currentIndexChanged.connect(self.update_passenger_options)
        passenger_layout.addRow("Type:", self.passenger_type)
        
        # Additional fields for passenger types
        self.interest_input = QLineEdit(self)
        self.interest_input.setPlaceholderText("Enter your interests")
        self.interest_input.setVisible(False)
        passenger_layout.addRow("Interests:", self.interest_input)
        
        self.height_input = QSpinBox(self)
        self.height_input.setRange(150, 220)
        self.height_input.setSuffix(" cm")
        self.height_input.setVisible(False)
        passenger_layout.addRow("Height:", self.height_input)
        
        passenger_group.setLayout(passenger_layout)
        layout.addWidget(passenger_group)

        # Seat preference selection
        preference_group = QGroupBox("Seating Preference")
        preference_layout = QFormLayout()
        
        self.preference_combo = QComboBox(self)
        self.preference_combo.addItems(["Networking", "Sleep", "Work", "Comfort", "Eco-Friendly"])
        preference_layout.addRow("Preference:", self.preference_combo)
        
        preference_group.setLayout(preference_layout)
        layout.addWidget(preference_group)

        # Seat selection form (for user details)
        self.details_form = QFormLayout()
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Your Name")
        self.details_form.addRow("Name: ", self.name_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter Your Email")
        self.details_form.addRow("Email: ", self.email_input)

        self.flight_combo = QComboBox(self)
        for flight in self.flights:
            self.flight_combo.addItem(f"{flight.flight_id}: {flight.airline} - {flight.source} to {flight.destination}", 
                                    flight.flight_id)
        self.details_form.addRow("Select Flight: ", self.flight_combo)

        self.flight_date = QDateEdit(self)
        self.flight_date.setDate(datetime.now().date())
        self.flight_date.setCalendarPopup(True)
        self.details_form.addRow("Flight Date:", self.flight_date)

        self.age_input = QSpinBox(self)
        self.age_input.setRange(18, 100)  # Age range
        self.details_form.addRow("Age: ", self.age_input)

        self.payment_status = QCheckBox("Payment Completed", self)
        self.payment_status.setChecked(True)  # Default to paid
        self.details_form.addRow("Payment Status:", self.payment_status)

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

        # ID Scanner Section
        id_scanner_group = QGroupBox("ID Scanner")
        id_scanner_layout = QVBoxLayout()
        
        self.scan_id_button = QPushButton("Scan ID or Passport", self)
        self.scan_id_button.setIcon(QIcon.fromTheme("document-scanner", QIcon()))
        self.scan_id_button.clicked.connect(self.scan_id_document)
        
        self.document_type_combo = QComboBox(self)
        self.document_type_combo.addItems(["passport", "id_card"])
        
        scanner_form = QFormLayout()
        scanner_form.addRow("Document Type:", self.document_type_combo)
        
        id_scanner_layout.addLayout(scanner_form)
        id_scanner_layout.addWidget(self.scan_id_button)
        
        id_scanner_group.setLayout(id_scanner_layout)
        layout.addWidget(id_scanner_group)

        # Submit button for booking the seat
        self.submit_button = QPushButton(" Book Seat", self)
        self.submit_button.setIcon(QIcon.fromTheme("document-save", QIcon()))  # PyQt will use system theme icon if available
        self.submit_button.clicked.connect(self.book_seat)
        layout.addWidget(self.submit_button)

        # Swap Seat button
        self.swap_button = QPushButton(" Swap Seat", self)
        self.swap_button.setIcon(QIcon.fromTheme("view-refresh", QIcon()))
        self.swap_button.clicked.connect(self.swap_seat)
        layout.addWidget(self.swap_button)

        # Show available zone seats
        self.zone_button = QPushButton(" Show Zone Seats", self)
        self.zone_button.setIcon(QIcon.fromTheme("view-grid", QIcon()))
        self.zone_button.clicked.connect(self.show_zone_seats)
        layout.addWidget(self.zone_button)

        # Send reminder email button
        self.reminder_button = QPushButton(" Schedule Reminder Email", self)
        self.reminder_button.setIcon(QIcon.fromTheme("mail-send", QIcon()))
        self.reminder_button.clicked.connect(self.schedule_reminder)
        layout.addWidget(self.reminder_button)

        self.setLayout(layout)
        self.setWindowTitle('Seat Selection & Booking')
        self.setGeometry(100, 100, 600, 800)
        self.show()

    def generate_ticket_id(self):
        """Generate a unique ticket ID"""
        self.ticket_counter += 1
        return f"TKT{self.ticket_counter}"

    def create_ticket(self, passenger_name, flight_id, seat_number, payment_status):
        """Create a new ticket and return its proxy"""
        ticket_id = self.generate_ticket_id()
        ticket = Ticket(ticket_id, passenger_name, flight_id, seat_number, payment_status)
        ticket_proxy = TicketProxy(ticket)
        self.tickets[ticket_id] = ticket_proxy
        return ticket_proxy

    def change_seat_with_ticket(self, ticket_id, new_seat):
        """Change seat using a ticket proxy"""
        if ticket_id in self.tickets:
            ticket_proxy = self.tickets[ticket_id]
            result = ticket_proxy.change_seat(new_seat)
            return result
        return "Ticket not found."

    def update_passenger_options(self):
        passenger_type = self.passenger_type.currentText()
        
        # Hide all optional fields first
        self.interest_input.setVisible(False)
        self.height_input.setVisible(False)
        
        # Show fields based on passenger type
        if passenger_type == "Socializer":
            self.interest_input.setVisible(True)
        elif passenger_type == "Tall":
            self.height_input.setVisible(True)
        elif passenger_type == "Eco-Friendly":
            pass
    
    def get_selected_flight(self):
        flight_id = self.flight_combo.currentData()
        for flight in self.flights:
            if flight.flight_id == flight_id:
                return flight
        return None

    def create_seat_buttons(self):
        row = 0
        col = 0

        # Create airplane layout
        for seat, available in self.available_seats.items():
            seat_button = QPushButton(seat, self)
            seat_button.setFixedSize(45, 45)
            seat_button.setEnabled(available)
            
            if seat.endswith(('A', 'D')):  # Window seats
                if available:
                    seat_button.setStyleSheet("""
                        QPushButton {
                            background-color: #85c1e9;
                            color: #2c3e50;
                            border: none;
                            border-radius: 8px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #5dade2;
                        }
                    """)
                else:
                    seat_button.setStyleSheet("background-color: #d6eaf8; color: #7f8c8d; border: none; border-radius: 8px;")
            else:  # Middle seats
                if available:
                    seat_button.setStyleSheet("""
                        QPushButton {
                            background-color: #aed6f1;
                            color: #2c3e50;
                            border: none;
                            border-radius: 8px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #7fb3d5;
                        }
                    """)
                else:
                    seat_button.setStyleSheet("background-color: #ebf5fb; color: #7f8c8d; border: none; border-radius: 8px;")
            
            seat_button.clicked.connect(self.select_seat)
            self.grid_layout.addWidget(seat_button, row, col)
            
            if seat.endswith('B'):
                col += 1
                aisle = QLabel("", self)
                aisle.setFixedSize(20, 60)
                self.grid_layout.addWidget(aisle, row, col)
                
            col += 1
            if col > 4:  # Adjusted for aisle
                col = 0
                row += 1

    def select_seat(self):
        selected_button = self.sender()  
        selected_seat = selected_button.text()

        # Reset previous selection if any
        if self.selected_seat:
            old_seat_button = None
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.text() == self.selected_seat:
                    old_seat_button = widget
                    break
            
            if old_seat_button:
                # Reset to available styling
                if self.selected_seat.endswith(('A', 'D')):  # Window seats
                    old_seat_button.setStyleSheet("""
                        QPushButton {
                            background-color: #85c1e9;
                            color: #2c3e50;
                            border: none;
                            border-radius: 8px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #5dade2;
                        }
                    """)
                else:  # Middle seats
                    old_seat_button.setStyleSheet("""
                        QPushButton {
                            background-color: #aed6f1;
                            color: #2c3e50;
                            border: none;
                            border-radius: 8px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #7fb3d5;
                        }
                    """)

        if self.available_seats[selected_seat]:  
            self.selected_seat = selected_seat
            self.selected_seat_label.setText(f"Selected Seat: {self.selected_seat}")
            
            selected_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
            """)
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

    def create_appropriate_passenger(self, name, seat, preference):
        """Create the appropriate passenger type based on selection"""
        passenger_type = self.passenger_type.currentText()
        
        if passenger_type == "Socializer":
            interest = self.interest_input.text() or "General socializing"
            return Socializer(name, seat, preference, interest)
        elif passenger_type == "Tall":
            height = self.height_input.value()
            return TallPassenger(name, seat, preference, height)
        elif passenger_type == "Eco-Friendly":
            eco_passenger = EcoPassenger(name, seat, preference)
            recommended_meal = eco_passenger.recommend_meal()
            self.selected_seat_label.setText(f"Selected Seat: {seat}\nRecommended Meal: {recommended_meal}")
            return eco_passenger
        else:
            return Passenger(name, seat, preference)

    def book_seat(self):
        if self.selected_seat is None:
            self.selected_seat_label.setText("No seat selected. Please select a seat first.")
            return
        
        passenger_name = self.name_input.text()
        selected_flight = self.get_selected_flight()
        flight_id = selected_flight.flight_id
        preference = self.preference_combo.currentText()
        age = self.age_input.value()
        baggage_weight = self.baggage_weight.value()
        payment_status = self.payment_status.isChecked()

        if passenger_name == "":
            self.selected_seat_label.setText("Please enter your name.")
            return

        passenger = self.create_appropriate_passenger(
            name=passenger_name, 
            seat=self.selected_seat, 
            preference=preference
        )
        
        # Create ticket
        ticket_proxy = self.create_ticket(
            passenger_name=passenger_name,
            flight_id=flight_id,
            seat_number=self.selected_seat,
            payment_status=payment_status
        )
        ticket_details = ticket_proxy.get_ticket_details()
        
        # Handle baggage
        baggage = Baggage(passenger_name, baggage_weight)
        baggage.calculate_fee()
        baggage_fee = baggage.baggage_fee
        
        self.seat_swapper.add_passenger(passenger)

        flight_info = f"{selected_flight.flight_id}: {selected_flight.airline} ({selected_flight.source} to {selected_flight.destination})"
        
        confirmation_text = f"Booking confirmed for {passenger_name} on {flight_info} with seat {self.selected_seat}"
        confirmation_text += f"\nPreference: {preference}"
        confirmation_text += f"\nTicket ID: {ticket_details['ticket_id']}"
        confirmation_text += f"\nPayment Status: {'Paid' if payment_status else 'Pending'}"
                
        # Add passenger type specific info
        passenger_type = self.passenger_type.currentText()
        if passenger_type == "Socializer":
            confirmation_text += f"\nInterests: {self.interest_input.text()}"
        elif passenger_type == "Tall":
            confirmation_text += f"\nHeight: {self.height_input.value()} cm"
        elif passenger_type == "Eco-Friendly":
            eco_passenger = passenger
            confirmation_text += f"\nRecommended Meal: {eco_passenger.recommend_meal()}"
        
        # Add baggage information to confirmation
        if baggage_fee > 0:
            confirmation_text += f"\nBaggage fee: ${baggage_fee} (Weight: {baggage_weight}kg)"
        else:
            confirmation_text += f"\nNo baggage fee (Weight: {baggage_weight}kg)"
        
        self.selected_seat_label.setStyleSheet("""
            background-color: #e8f8f5;
            border: 1px solid #abebc6;
            border-radius: 5px;
            padding: 10px;
            color: #27ae60;
            font-weight: bold;
        """)
        self.selected_seat_label.setText(confirmation_text)
        
    def swap_seat(self):
        self.seat_swapper.assign_seats()
        passenger_data = self.seat_swapper.get_passenger_data()

        if not passenger_data:
            self.selected_seat_label.setText("No passengers available for seat swapping.")
            return

        swap_message = "\n".join([f"{data['name']} -> Seat {data['seat']} (Preference: {data['preference']})"
                                  for data in passenger_data])
        self.selected_seat_label.setText(f"Seat Swap Complete:\n{swap_message}")

    def show_zone_seats(self):
        available_zones = self.seat_swapper.get_available_seats()
        zone_info = []
        
        for zone, seats in available_zones.items():
            if seats:
                seat_list = ", ".join(seats)
                zone_info.append(f"{zone} Zone: {seat_list}")
            else:
                zone_info.append(f"{zone} Zone: No seats available")
        
        self.selected_seat_label.setText("Available Zone Seats:\n" + "\n".join(zone_info))

    def schedule_reminder(self):
        passenger_name = self.name_input.text()
        email = self.email_input.text()
        flight_date = self.flight_date.date().toString("yyyy-MM-dd")
        
        if not passenger_name or not email:
            self.selected_seat_label.setText("Please enter your name and email to schedule a reminder.")
            return
        
        email_sender = ReminderEmailSender(
            sender_email="flightsystem@example.com",
            sender_password="password123"
        )
        
        # Attempt to send/schedule reminder
        success = email_sender.send_reminder(
            passenger_name=passenger_name,
            recipient_email=email,
            flight_date=flight_date
        )
        
        if success:
            self.selected_seat_label.setText(f"Reminder emails scheduled for {flight_date}")
        else:
            self.selected_seat_label.setText("Failed to schedule reminder. Please try again later.")

    def scan_id_document(self):
        """Open a file dialog to select an ID document image and process it"""
        try:
            # Open file dialog to select image
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self, 
                "Select ID Document", 
                "", 
                "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if file_path:
                # Get selected document type
                document_type = self.document_type_combo.currentText()
                
                # Show processing message
                self.selected_seat_label.setText("Processing document... Please wait.")
                self.selected_seat_label.setStyleSheet("""
                    background-color: #eaf2f8;
                    border: 1px solid #aed6f1;
                    border-radius: 5px;
                    padding: 10px;
                    color: #2980b9;
                    font-weight: bold;
                """)
                QApplication.processEvents()  # Update UI
                
                # Process the document using the function from ID.py
                from ML.ID import process_id_for_seat_selection
                process_id_for_seat_selection(self, file_path, document_type)
                
        except Exception as e:
            # Display error
            self.selected_seat_label.setText(f"Error scanning document: {str(e)}")
            self.selected_seat_label.setStyleSheet("""
                background-color: #fdedec;
                border: 1px solid #f5b7b1;
                border-radius: 5px;
                padding: 10px;
                color: #c0392b;
                font-weight: bold;
            """)

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

        ticket_group = QGroupBox("Ticket Operations")
        ticket_layout = QFormLayout()

        self.ticket_id_input = QLineEdit(self)
        self.ticket_id_input.setPlaceholderText("Enter Ticket ID")
        ticket_layout.addRow("Ticket ID:", self.ticket_id_input)

        self.new_seat_input = QLineEdit(self)
        self.new_seat_input.setPlaceholderText("e.g., 2B")
        ticket_layout.addRow("New Seat:", self.new_seat_input)

        # Button for changing seat
        seat_change_button = QPushButton("Change Seat", self)
        seat_change_button.clicked.connect(self.handle_seat_change)
        ticket_layout.addRow(seat_change_button)

        # Button for canceling ticket
        cancel_ticket_button = QPushButton("Cancel Ticket", self)
        cancel_ticket_button.clicked.connect(self.handle_ticket_cancel)
        ticket_layout.addRow(cancel_ticket_button)

        ticket_group.setLayout(ticket_layout)
        layout.addWidget(ticket_group)

        self.setLayout(layout)
        self.setWindowTitle('Feedback')
        self.setGeometry(100, 100, 400, 200)

    def submit_feedback(self):
        feedback_text = self.feedback_input.text()
        if feedback_text == "":
            self.feedback_input.setText("Please enter feedback.")
        else:
            self.feedback_input.setText("Thank you for your feedback!")
    
    def handle_seat_change(self):
        """Handle seat change request"""
        ticket_id = self.ticket_id_input.text().strip()
        new_seat = self.new_seat_input.text().strip()
        
        if not ticket_id or not new_seat:
            self.selected_seat_label.setText("Please enter both Ticket ID and new seat.")
            return
        
        if new_seat not in self.available_seats or not self.available_seats[new_seat]:
            self.selected_seat_label.setText(f"Seat {new_seat} is not available.")
            return
        
        result = self.change_seat_with_ticket(ticket_id, new_seat)
        self.selected_seat_label.setText(result)

    def handle_ticket_cancel(self):
        """Handle ticket cancellation request"""
        ticket_id = self.ticket_id_input.text().strip()
        
        if not ticket_id:
            self.selected_seat_label.setText("Please enter a Ticket ID.")
            return
        
        if ticket_id in self.tickets:
            ticket_proxy = self.tickets[ticket_id]
            result = ticket_proxy.cancel_ticket()
            
            # Free up the seat
            ticket_details = ticket_proxy.get_ticket_details()
            old_seat = ticket_details["seat_number"]
            self.available_seats[old_seat] = True
            
            # Remove the ticket
            del self.tickets[ticket_id]
            
            self.selected_seat_label.setText(result)
        else:
            self.selected_seat_label.setText("Ticket not found.")


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


class CrewManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.crew_registry = CrewRegistry()
        # Initialize with some sample crew members
        self.init_sample_data()
        self.init_ui()
        
    def init_sample_data(self):
        """Initialize with sample crew members for demonstration"""
        try:
            crew1 = CrewMember(101, "John Smith", "Pilot", "john.smith@airline.com")
            crew2 = CrewMember(102, "Emily Jones", "Flight Attendant", "emily.jones@airline.com")
            crew3 = CrewMember(103, "Carlos Rodriguez", "Co-Pilot", "carlos.rodriguez@airline.com")
        except Exception as e:
            print(f"Error creating sample crew members: {e}")
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel("Crew Management", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Form for adding new crew members
        form_group = QGroupBox("Add New Crew Member")
        form_layout = QFormLayout()
        
        self.crew_id_input = QSpinBox(self)
        self.crew_id_input.setRange(100, 999)
        form_layout.addRow("Crew ID:", self.crew_id_input)
        
        self.crew_name_input = QLineEdit(self)
        form_layout.addRow("Name:", self.crew_name_input)
        
        self.crew_role_combo = QComboBox(self)
        self.crew_role_combo.addItems(["Pilot", "Co-Pilot", "Flight Attendant", "Purser"])
        form_layout.addRow("Role:", self.crew_role_combo)
        
        self.crew_contact_input = QLineEdit(self)
        self.crew_contact_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Contact (Email):", self.crew_contact_input)
        
        self.add_crew_button = QPushButton("Add Crew Member", self)
        self.add_crew_button.clicked.connect(self.add_crew_member)
        form_layout.addRow(self.add_crew_button)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table to display crew members
        self.crew_table = QTableWidget(self)
        self.crew_table.setColumnCount(6)
        self.crew_table.setHorizontalHeaderLabels(["ID", "Name", "Role", "Contact", "Flight", "Status"])
        self.crew_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.crew_table)
        
        # Flight assignment section
        assignment_group = QGroupBox("Assign Flight")
        assignment_layout = QFormLayout()
        
        self.crew_select_combo = QComboBox(self)
        self.update_crew_combo()
        assignment_layout.addRow("Select Crew:", self.crew_select_combo)
        
        self.flight_id_input = QLineEdit(self)
        self.flight_id_input.setPlaceholderText("e.g., FL123")
        assignment_layout.addRow("Flight ID:", self.flight_id_input)
        
        self.assign_flight_button = QPushButton("Assign Flight", self)
        self.assign_flight_button.clicked.connect(self.assign_flight)
        assignment_layout.addRow(self.assign_flight_button)
        
        # Status update section
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Available", "On Duty", "Resting", "Boarding Passengers"])
        assignment_layout.addRow("Update Status:", self.status_combo)
        
        self.update_status_button = QPushButton("Update Status", self)
        self.update_status_button.clicked.connect(self.update_crew_status)
        assignment_layout.addRow(self.update_status_button)
        
        assignment_group.setLayout(assignment_layout)
        layout.addWidget(assignment_group)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Crew List", self)
        self.refresh_button.clicked.connect(self.refresh_crew_list)
        layout.addWidget(self.refresh_button)
        
        self.setLayout(layout)
        self.setWindowTitle('Crew Management')
        self.setGeometry(100, 100, 600, 700)
        
        # Initial population of the table
        self.refresh_crew_list()
    
    def update_crew_combo(self):
        """Update the crew selection dropdown"""
        self.crew_select_combo.clear()
        for crew in self.crew_registry.all_crew():
            self.crew_select_combo.addItem(f"{crew.crew_id}: {crew.name}", crew.crew_id)
    
    def add_crew_member(self):
        """Add a new crew member"""
        try:
            crew_id = self.crew_id_input.value()
            name = self.crew_name_input.text().strip()
            role = self.crew_role_combo.currentText()
            contact = self.crew_contact_input.text().strip()
            
            if not name:
                raise ValueError("Name cannot be empty")
            
            new_crew = CrewMember(crew_id, name, role, contact)
            QMessageBox.information(self, "Success", f"Added crew member: {name}")
            
            # Clear inputs
            self.crew_name_input.clear()
            self.crew_contact_input.clear()
            self.crew_id_input.setValue(self.crew_id_input.value() + 1)
            
            # Refresh displays
            self.refresh_crew_list()
            self.update_crew_combo()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def assign_flight(self):
        """Assign selected crew member to a flight"""
        if self.crew_select_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No crew members available")
            return
        
        crew_id = self.crew_select_combo.currentData()
        flight_id = self.flight_id_input.text().strip()
        
        if not flight_id:
            QMessageBox.warning(self, "Error", "Please enter a flight ID")
            return
        
        try:
            crew_member = self.crew_registry.get_crew_member(crew_id)
            if crew_member:
                crew_member.assign_flight(flight_id)
                QMessageBox.information(self, "Success", f"Assigned {crew_member.name} to flight {flight_id}")
                self.refresh_crew_list()
            else:
                QMessageBox.warning(self, "Error", "Crew member not found")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def update_crew_status(self):
        """Update the status of selected crew member"""
        if self.crew_select_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No crew members available")
            return
        
        crew_id = self.crew_select_combo.currentData()
        new_status = self.status_combo.currentText()
        
        try:
            crew_member = self.crew_registry.get_crew_member(crew_id)
            if crew_member:
                crew_member.update_status(new_status)
                QMessageBox.information(self, "Success", f"Updated {crew_member.name}'s status to {new_status}")
                self.refresh_crew_list()
            else:
                QMessageBox.warning(self, "Error", "Crew member not found")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def refresh_crew_list(self):
        """Refresh the crew list table"""
        crew_list = self.crew_registry.all_crew()
        self.crew_table.setRowCount(len(crew_list))
        
        for row, crew in enumerate(crew_list):
            self.crew_table.setItem(row, 0, QTableWidgetItem(str(crew.crew_id)))
            self.crew_table.setItem(row, 1, QTableWidgetItem(crew.name))
            self.crew_table.setItem(row, 2, QTableWidgetItem(crew.role))
            self.crew_table.setItem(row, 3, QTableWidgetItem(crew.contact_info))
            self.crew_table.setItem(row, 4, QTableWidgetItem(crew.assigned_flight or "None"))
            self.crew_table.setItem(row, 5, QTableWidgetItem(crew.status))
        
        self.crew_table.resizeColumnsToContents()

class AIAssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ai_assistant = AIAssistant()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Add AI Assistant logo/avatar at the top
        avatar_label = QLabel()
        avatar_pixmap = QPixmap(64, 64)  # Create a larger empty pixmap
        avatar_pixmap.fill(QColor(52, 152, 219))  # Fill with blue color
        avatar_label.setPixmap(avatar_pixmap)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setFixedHeight(70)
        avatar_layout = QHBoxLayout()
        avatar_layout.addStretch()
        avatar_layout.addWidget(avatar_label)
        avatar_layout.addStretch()
        
        # Title
        title_label = QLabel("AI Flight Assistant")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2980b9; margin-bottom: 15px;")
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.addLayout(avatar_layout)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)
        
        # Create divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #d1d8e0;")
        main_layout.addWidget(divider)
        
        # Chat history display
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #d6d8db;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            line-height: 1.5;
        """)
        main_layout.addWidget(self.chat_history, stretch=1)  # Give chat history more vertical space
        
        # Quick question section (chips)
        quick_question_frame = QFrame()
        quick_question_frame.setStyleSheet("""
            background-color: #f0f4f8;
            border-radius: 8px;
            padding: 10px;
        """)
        quick_question_layout = QVBoxLayout(quick_question_frame)
        
        quick_label = QLabel("Quick Questions:")
        quick_label.setStyleSheet("font-weight: bold; color: #4a6fa5;")
        quick_question_layout.addWidget(quick_label)
        
        # First row of quick questions
        quick_row1 = QHBoxLayout()
        self.q1_button = QPushButton("Help with booking")
        self.q1_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
        """)
        self.q1_button.clicked.connect(lambda: self.handle_quick_question("I need help with booking"))
        quick_row1.addWidget(self.q1_button)
        
        self.q2_button = QPushButton("Flight status")
        self.q2_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
        """)
        self.q2_button.clicked.connect(lambda: self.handle_quick_question("What's my flight status?"))
        quick_row1.addWidget(self.q2_button)
        
        self.q3_button = QPushButton("Baggage info")
        self.q3_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
        """)
        self.q3_button.clicked.connect(lambda: self.handle_quick_question("What are the baggage rules?"))
        quick_row1.addWidget(self.q3_button)
        quick_question_layout.addLayout(quick_row1)
        
        # Second row of quick questions
        quick_row2 = QHBoxLayout()
        self.q4_button = QPushButton("Seat selection help")
        self.q4_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
        """)
        self.q4_button.clicked.connect(lambda: self.handle_quick_question("How do I select a seat?"))
        quick_row2.addWidget(self.q4_button)
        
        self.q5_button = QPushButton("Cancel booking")
        self.q5_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
        """)
        self.q5_button.clicked.connect(lambda: self.handle_quick_question("How do I cancel my booking?"))
        quick_row2.addWidget(self.q5_button)
        
        self.q6_button = QPushButton("Talk to human agent")
        self.q6_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
        """)
        self.q6_button.clicked.connect(lambda: self.handle_quick_question("I want to speak with a human agent"))
        quick_row2.addWidget(self.q6_button)
        quick_question_layout.addLayout(quick_row2)
        
        main_layout.addWidget(quick_question_frame)
        
        # User input and send button in horizontal layout
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 10px;
        """)
        input_layout = QHBoxLayout(input_frame)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your question here...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d8e0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 1px solid #4a6fa5;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_bot_message)
        input_layout.addWidget(self.chat_input)
        
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon.fromTheme("mail-send", QIcon()))
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a6fa5;
                border-radius: 20px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5a7fb5;
            }
        """)
        self.send_button.clicked.connect(self.send_bot_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addWidget(input_frame)
        
        self.setLayout(main_layout)
        
        # Initialize the chat with a welcome message
        self.chat_history.append("<b>AI Assistant:</b> Hello! Welcome to E-JUST Airways. How can I help you with your flight today?")

    def send_bot_message(self):
        """Send user message to the AI assistant and display response"""
        user_message = self.chat_input.text().strip()
        if not user_message:
            return
        
        # Display user message
        self.chat_history.append(f"<b>You:</b> {user_message}")
        
        # Get response from AI assistant
        response = self.ai_assistant.process_query(user_message)
        
        # Display bot response
        self.chat_history.append(f"<b>AI Assistant:</b> {response}")
        
        # Clear input field
        self.chat_input.clear()
        
        # Process any seat related commands in the message
        self.process_bot_commands(user_message)
        
        # Scroll to bottom to see latest messages
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def handle_quick_question(self, question):
        """Handle predefined quick questions"""
        self.chat_input.setText(question)
        self.send_bot_message()

    def process_bot_commands(self, message):
        """Process any seat or flight related commands from the bot conversation"""
        # This is a stub for now - would need to communicate with other tabs
        # Will be implemented when integrating with the main application
        pass

class MainApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f7f9fc;
            }
            QGroupBox {
                border: 1px solid #dde2eb;
                border-radius: 6px;
                margin-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4a6fa5;
            }
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a7fb5;
            }
            QPushButton:pressed {
                background-color: #3a5f95;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #dde2eb;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #dde2eb;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #dde2eb;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)

        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Add fancy header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        app_title = QLabel("E-JUST Airways", self)
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2980b9;")
        header_layout.addWidget(app_title)

        header_layout.addStretch()
        layout.addWidget(header)

        # Create tab widget with modern styling
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dde2eb;
                border-radius: 6px;
                padding: 0px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e8f0;
                color: #4a6fa5;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 5px 15px;
                margin-right: 4px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #4a6fa5;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d1d8e0;
            }
        """)        

        # Create individual window instances
        self.seat_window = SeatSelectionWindow()
        self.feedback_window = FeedbackWindow()
        self.baggage_window = BaggageInfoWindow()
        self.crew_window = CrewManagementWindow()
        self.ai_assistant_window = AIAssistantWindow()  # Add our new AI Assistant window

        # Add windows to tabs
        tabs.addTab(self.seat_window, "Seat Selection")
        tabs.addTab(self.feedback_window, "Feedback")
        tabs.addTab(self.baggage_window, "Baggage Info")
        tabs.addTab(self.crew_window, "Crew Management")
        tabs.addTab(self.ai_assistant_window, "AI Assistant")  # Add AI Assistant tab

        layout.addWidget(tabs)
        
        self.setLayout(layout)
        self.setWindowTitle("Flight Booking System")
        self.setGeometry(100, 100, 800, 900)


if __name__ == "__main__":
    app = QApplication(sys.argv)  

    main_app = MainApplication()
    main_app.show()

    sys.exit(app.exec_())