import os
import sys
import threading
import socket
import json
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QGridLayout, QPushButton, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QFileDialog, QTextEdit, QGraphicsDropShadowEffect, QFrame, QRadioButton, QProgressBar
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from datetime import datetime, time

from passengers.PassengerClass import Passenger as BasePassenger
from passengers.ticket import Ticket, TicketProxy
from flights.Flight import Flight, FlightScheduleProxy
from flights.CrewMember import CrewMember, CrewRegistry, CrewRegistryProxy, User
from utilities.Feedback import Feedback
from utilities.ReminderEmailSender import ReminderEmailSender
from utilities.seat_swap import Passenger, Socializer, TallPassenger, EcoPassenger, SeatSwapper 
from Security.credentials_encryption import CredentialsManager
from baggage.Baggage import Baggage
from ML.Bot import AIAssistant
from Networking.payment_server import PaymentServer
from Database.database_handler import DatabaseHandler

class SeatSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler(host="localhost", user="root", password="11", database="flight_booking")
        if not self.db.connect():
            print("Failed to connect to database")
            return
                
        self.db.create_tables()

        self.init_flights_in_db()

        self.flight_id = "FL001"
        self.load_available_seats()

        self.selected_seat = None
        self.seat_swapper = SeatSwapper()

        self.flights = self.load_flights_from_db()
        self.flight_proxies = [FlightScheduleProxy(flight) for flight in self.flights]
    
        self.ticket_counter = 1000
        self.tickets = {}
 
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        

        self.title_label = QLabel("Select Your Seat", self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9; margin-bottom: 0px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.grid_layout = QGridLayout()
        self.create_seat_buttons()
        
        layout.addLayout(self.grid_layout)

        self.selected_seat_label = QLabel("Selected Seat: None", self)
        layout.addWidget(self.selected_seat_label)

        passenger_group = QGroupBox("Passenger Type")
        passenger_layout = QFormLayout()
        
        self.passenger_type = QComboBox(self)
        self.passenger_type.addItems(["Regular", "Socializer", "Tall", "Eco-Friendly"])
        self.passenger_type.currentIndexChanged.connect(self.update_passenger_options)
        passenger_layout.addRow("Type:", self.passenger_type)
        
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

        preference_group = QGroupBox("Seating Preference")
        preference_layout = QFormLayout()
        
        self.preference_combo = QComboBox(self)
        self.preference_combo.addItems(["Networking", "Sleep", "Work", "Comfort", "Eco-Friendly"])
        preference_layout.addRow("Preference:", self.preference_combo)
        
        preference_group.setLayout(preference_layout)
        layout.addWidget(preference_group)

        self.details_form = QFormLayout()

        personal_info_layout = QHBoxLayout()

        self.details_form.addRow(personal_info_layout)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Your Name")
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.name_input)
        personal_info_layout.addLayout(name_layout)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter Your Email")
        email_layout = QVBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        email_layout.addWidget(self.email_input)
        personal_info_layout.addLayout(email_layout)

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
        self.age_input.setRange(18, 100)
        age_layout = QVBoxLayout()
        age_layout.addWidget(QLabel("Age:"))
        age_layout.addWidget(self.age_input)
        personal_info_layout.addLayout(age_layout)
        
        self.payment_status = QCheckBox("Mark as paid", self)
        self.details_form.addRow("Payment status:", self.payment_status)

        baggage_group = QGroupBox("Baggage Information")
        baggage_layout = QFormLayout()
        
        self.baggage_weight = QDoubleSpinBox(self)
        self.baggage_weight.setRange(0, 50)
        self.baggage_weight.setDecimals(1)
        self.baggage_weight.setSuffix(" kg")
        self.baggage_weight.setValue(15.0)
        baggage_layout.addRow("Baggage Weight:", self.baggage_weight)
        
        self.check_baggage_button = QPushButton("Check Baggage Fee", self)
        self.check_baggage_button.clicked.connect(self.check_baggage)
        baggage_layout.addRow(self.check_baggage_button)
        
        self.baggage_status = QLabel("No baggage checked yet", self)
        baggage_layout.addRow(self.baggage_status)
        
        baggage_group.setLayout(baggage_layout)
        
        layout.addLayout(self.details_form)
        layout.addWidget(baggage_group)

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

        button_layout = QHBoxLayout()


        self.submit_button = QPushButton(" Book Seat", self)
        self.submit_button.setIcon(QIcon.fromTheme("document-save", QIcon()))  
        self.submit_button.clicked.connect(self.book_seat)
        button_layout.addWidget(self.submit_button)

        self.swap_button = QPushButton(" Swap Seat", self)
        self.swap_button.setIcon(QIcon.fromTheme("view-refresh", QIcon()))
        self.swap_button.clicked.connect(self.swap_seat)
        button_layout.addWidget(self.swap_button)

        self.zone_button = QPushButton(" Show Zone Seats", self)
        self.zone_button.setIcon(QIcon.fromTheme("view-grid", QIcon()))
        self.zone_button.clicked.connect(self.show_zone_seats)
        button_layout.addWidget(self.zone_button)

        self.reminder_button = QPushButton(" Schedule Reminder Email", self)
        self.reminder_button.setIcon(QIcon.fromTheme("mail-send", QIcon()))
        self.reminder_button.clicked.connect(self.schedule_reminder)
        button_layout.addWidget(self.reminder_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('Seat Selection & Booking')
        self.setGeometry(100, 100, 600, 800)
        self.show()

    def init_flights_in_db(self):
        existing_flights = self.db.get_all_flights()
        if existing_flights and len(existing_flights) > 0:
            return  # Flights already exist
        
        # Add sample flights
        flights_data = [
            ("FL001", "AirExpress", "New York", "Los Angeles", 
             time(8, 0), time(11, 30), datetime.now().date(), 120),
            ("FL002", "SkyWings", "Chicago", "Miami", 
             time(9, 15), time(12, 45), datetime.now().date(), 90),
            ("FL003", "OceanAir", "Boston", "San Francisco", 
             time(14, 30), time(18, 0), datetime.now().date(), 75)
        ]
        
        for flight_data in flights_data:
            self.db.add_flight(*flight_data)
        
        # Initialize seats for each flight
        default_seat_map = {
            "1A": True, "1B": True, "1C": True, "1D": True,
            "2A": True, "2B": True, "2C": True, "2D": True,
            "3A": True, "3B": True, "3C": True, "3D": True,
            "4A": True, "4B": True, "4C": True, "4D": True,
        }
        
        for flight_data in flights_data:
            flight_id = flight_data[0]
            self.db.initialize_seats_for_flight(flight_id, default_seat_map)

    def load_flights_from_db(self):
        """Load flights from database"""
        flights_data = self.db.get_all_flights()
        flights = []
        
        for flight_data in flights_data:
            # Assuming Flight class constructor matches database fields
            flight = Flight(
                flight_data[0],  
                flight_data[1],  
                flight_data[2],  
                flight_data[3],  
                flight_data[4],  
                flight_data[5],  
                flight_data[6],  
                flight_data[7]   
            )
            flights.append(flight)
        
        return flights

    def load_available_seats(self):
        """Load available seats from database for current flight"""
        available_seats_data = self.db.get_available_seats(self.flight_id)
        
        # Initialize all seats as unavailable first
        self.available_seats = {
            "1A": False, "1B": False, "1C": False, "1D": False,
            "2A": False, "2B": False, "2C": False, "2D": False,
            "3A": False, "3B": False, "3C": False, "3D": False,
            "4A": False, "4B": False, "4C": False, "4D": False,
        }
        
        # Update with available seats from database
        for seat_data in available_seats_data:
            seat_id = seat_data[0]
            if seat_id in self.available_seats:
                self.available_seats[seat_id] = True

    def generate_ticket_id(self):
        self.ticket_counter += 1
        return f"TKT{self.ticket_counter}"

    def create_ticket(self, passenger_name, flight_id, seat_number, payment_status):
        ticket_id = self.generate_ticket_id()
        ticket = Ticket(ticket_id, passenger_name, flight_id, seat_number, payment_status)
        ticket_proxy = TicketProxy(ticket)
        self.tickets[ticket_id] = ticket_proxy
        return ticket_proxy

    def change_seat_with_ticket(self, ticket_id, new_seat):
        if ticket_id in self.tickets:
            ticket_proxy = self.tickets[ticket_id]
            result = ticket_proxy.change_seat(new_seat)
            return result
        return "Ticket not found."

    def update_passenger_options(self):
        passenger_type = self.passenger_type.currentText()
        
        self.interest_input.setVisible(False)
        self.height_input.setVisible(False)
        
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


    def on_flight_changed(self):
        """Handle flight selection change"""
        selected_flight = self.get_selected_flight()
        if selected_flight:
            self.flight_id = selected_flight.flight_id
            self.load_available_seats()
            self.refresh_seat_display()

    def refresh_seat_display(self):
        """Refresh seat buttons display based on current availability"""
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() in self.available_seats:
                seat_id = widget.text()
                is_available = self.available_seats[seat_id]
                widget.setEnabled(is_available)
                
                if seat_id.endswith(('A', 'D')):  # Window seats
                    if is_available:
                        widget.setStyleSheet("""
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
                        widget.setStyleSheet("background-color: #d6eaf8; color: #7f8c8d; border: none; border-radius: 8px;")
                else:  # Middle seats
                    if is_available:
                        widget.setStyleSheet("""
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
                        widget.setStyleSheet("background-color: #ebf5fb; color: #7f8c8d; border: none; border-radius: 8px;")

    def create_seat_buttons(self):
        row = 0
        col = 0

        for seat, available in self.available_seats.items():
            seat_button = QPushButton(seat, self)
            seat_button.setFixedSize(45, 45)
            seat_button.setEnabled(available)
            
            if seat.endswith(('A', 'D')):
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
            else:
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
            if col > 4:
                col = 0
                row += 1

    def select_seat(self):
        selected_button = self.sender()  
        selected_seat = selected_button.text()

        if self.selected_seat:
            old_seat_button = None
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.text() == self.selected_seat:
                    old_seat_button = widget
                    break
            
            if old_seat_button:
                if self.selected_seat.endswith(('A', 'D')):
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
                else:
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
    
    def get_flight_info(self):
        flight_id = self.flight_combo.currentData()
        for flight in self.flights:
            if flight.flight_id == flight_id:
                return f"{flight.flight_id}: {flight.airline} ({flight.source} to {flight.destination})"
        return None
    
    def check_baggage(self):
        passenger_name = self.name_input.text()
        weight = self.baggage_weight.value()
        
        if passenger_name == "":
            self.baggage_status.setText("Please enter your name first.")
            return
        
        baggage = Baggage(passenger_name, weight)
        
        baggage.calculate_fee()
        
        self.baggage_status.setText(baggage.get_fee_summary())

    def create_appropriate_passenger(self, name, seat, preference):
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
        
        if passenger_name == "":
            self.selected_seat_label.setText("Please enter your name.")
            return

        baggage = Baggage(passenger_name, baggage_weight)
        baggage.calculate_fee()
        baggage_fee = baggage.baggage_fee
        
        flight_info = f"{selected_flight.flight_id}: {selected_flight.airline} ({selected_flight.source} to {selected_flight.destination})"
        
        if self.payment_status.isChecked():
            self.complete_booking(
                passenger_name=passenger_name,
                flight_id=flight_id,
                email=None,
                age=age,
                preference=preference,
                baggage_weight=baggage_weight,
                baggage_fee=baggage_fee,
                payment_status=True
            )
        else:
            payment_window = PaymentWindow(
                parent=self,
                passenger_name=passenger_name,
                flight_info=flight_info,
                seat_id=self.selected_seat,
                baggage_fee=baggage_fee
            )
            
            if payment_window.exec_() == QDialog.Accepted:
                self.complete_booking(
                    passenger_name=passenger_name,
                    flight_id=flight_id,
                    email=None,
                    age=age,
                    preference=preference,
                    baggage_weight=baggage_weight,
                    baggage_fee=baggage_fee,
                    payment_status=True
                )
        
      #  passenger_id = self.db.add_passenger(passenger_name, email, age, )
    def complete_booking(self, passenger_name, email, age, flight_id, preference, baggage_weight, baggage_fee, payment_status):
        try:
            passenger_type = self.passenger_type.currentText()
            special_data = None
            
            if passenger_type == "Socializer":
                special_data = self.interest_input.text() or "General socializing"
            elif passenger_type == "Tall":
                special_data = f"Height: {self.height_input.value()} cm"
            elif passenger_type == "Eco-Friendly":
                eco_passenger = EcoPassenger(passenger_name, self.selected_seat, preference)
                special_data = f"Recommended Meal: {eco_passenger.recommend_meal()}"
            
            # Add passenger to database
            passenger_id = self.db.add_passenger(
                name=passenger_name,
                email=email,
                age=age,
                passenger_type=passenger_type,
                preferences=preference,
                special_data=special_data
            )
            
            if passenger_id is None:
                self.selected_seat_label.setText("Error: Failed to save passenger data")
                return
            
            # Add baggage if applicable
            if baggage_weight > 0:
                baggage_success = self.db.add_baggage(passenger_id, baggage_weight, baggage_fee)
                if not baggage_success:
                    print("Warning: Failed to save baggage data")
            
            # Generate ticket ID and create booking
            ticket_id = self.generate_ticket_id()
            booking_success = self.db.create_booking(
                ticket_id=ticket_id,
                passenger_id=passenger_id,
                flight_id=flight_id,
                seat_id=self.selected_seat,
                payment_status=payment_status
            )
            
            if not booking_success:
                self.selected_seat_label.setText("Error: Failed to create booking")
                return
            
            # Update payment status if needed
            if payment_status:
                payment_update = self.db.update_booking_payment(ticket_id, True)
                if not payment_update:
                    print("Warning: Failed to update payment status")
            
            # Create passenger object for seat swapper
            selected_flight = None
            for flight in self.flights:
                if flight.flight_id == flight_id:
                    selected_flight = flight
                    break
                    
            passenger = self.create_appropriate_passenger(
                name=passenger_name, 
                seat=self.selected_seat, 
                preference=preference
            )
            
            # Create ticket proxy
            ticket_proxy = self.create_ticket(
                passenger_name=passenger_name,
                flight_id=flight_id,
                seat_number=self.selected_seat,
                payment_status=payment_status
            )
            ticket_details = ticket_proxy.get_ticket_details()
            
            self.seat_swapper.add_passenger(passenger)

            flight_info = f"{selected_flight.flight_id}: {selected_flight.airline} ({selected_flight.source} to {selected_flight.destination})"
            
            confirmation_text = f"Booking confirmed for {passenger_name} on {flight_info} with seat {self.selected_seat}"
            confirmation_text += f"\nPreference: {preference}"
            confirmation_text += f"\nTicket ID: {ticket_id}"
            confirmation_text += f"\nPayment Status: {'Paid' if payment_status else 'Pending'}"
            confirmation_text += f"\nPassenger ID: {passenger_id}"
                    
            # Add passenger type specific info
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
            
            # Mark seat as unavailable in local state and database
            self.available_seats[self.selected_seat] = False
            
            # Update seat button styles to show as unavailable
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.text() == self.selected_seat:
                    if self.selected_seat.endswith(('A', 'D')):  # Window seats
                        widget.setStyleSheet("background-color: #d6eaf8; color: #7f8c8d; border: none; border-radius: 8px;")
                    else:  # Middle seats
                        widget.setStyleSheet("background-color: #ebf5fb; color: #7f8c8d; border: none; border-radius: 8px;")
                    widget.setEnabled(False)
                    break
            
            # Reset selection
            self.selected_seat = None
            
        except Exception as e:
            self.selected_seat_label.setText(f"Error: Failed to complete booking - {str(e)}")
            print(f"Booking error: {e}")

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

    def get_booking_details(self, ticket_id):
        return self.db.get_booking_by_ticket(ticket_id)

    def get_passenger_baggage(self, passenger_id):
        return self.db.get_baggage_by_passenger(passenger_id)

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.disconnect()

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
    def __init__(self, current_user=None):
        super().__init__()
        
        self.current_user = current_user or User("guest", "guest")
        
        self.registry_proxy = CrewRegistryProxy(self.current_user)
        
        self.init_sample_data()
        self.init_ui()
        
    def init_sample_data(self):
        if self.current_user.role == "admin":
            try:
                crew1 = CrewMember(101, "John Smith", "Pilot", "john.smith@airline.com")
                crew2 = CrewMember(102, "Emily Jones", "Flight Attendant", "emily.jones@airline.com")
                crew3 = CrewMember(103, "Carlos Rodriguez", "Co-Pilot", "carlos.rodriguez@airline.com")
            except Exception as e:
                print(f"Error creating sample crew members: {e}")
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.user_info_label = QLabel(f"Logged in as: {self.current_user.username} ({self.current_user.role})", self)
        layout.addWidget(self.user_info_label)
        
        self.title_label = QLabel("Crew Management", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
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
        
        if not self.current_user.has_permission("add"):
            self.crew_id_input.setEnabled(False)
            self.crew_name_input.setEnabled(False)
            self.crew_role_combo.setEnabled(False)
            self.crew_contact_input.setEnabled(False)
            self.add_crew_button.setEnabled(False)
            form_group.setTitle("Add New Crew Member (Requires Admin Permission)")
        
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
        
        # Disable update controls if user doesn't have update permission
        if not self.current_user.has_permission("update"):
            self.flight_id_input.setEnabled(False)
            self.assign_flight_button.setEnabled(False)
            self.status_combo.setEnabled(False)
            self.update_status_button.setEnabled(False)
            assignment_group.setTitle("Update Crew (Requires Staff or Admin Permission)")
        
        assignment_group.setLayout(assignment_layout)
        layout.addWidget(assignment_group)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Crew List", self)
        self.refresh_button.clicked.connect(self.refresh_crew_list)
        layout.addWidget(self.refresh_button)
        
        # Add a user role switcher for testing (normally this would be handled by login)
        if True:  # Testing mode
            role_group = QGroupBox("Switch User Role (For Testing)")
            role_layout = QHBoxLayout()
            
            self.guest_button = QPushButton("Guest", self)
            self.guest_button.clicked.connect(lambda: self.switch_user_role("guest"))
            role_layout.addWidget(self.guest_button)
            
            self.staff_button = QPushButton("Staff", self)
            self.staff_button.clicked.connect(lambda: self.switch_user_role("staff"))
            role_layout.addWidget(self.staff_button)
            
            self.admin_button = QPushButton("Admin", self)
            self.admin_button.clicked.connect(lambda: self.switch_user_role("admin"))
            role_layout.addWidget(self.admin_button)
            
            role_group.setLayout(role_layout)
            layout.addWidget(role_group)
        
        self.setLayout(layout)
        self.setWindowTitle('Crew Management')
        self.setGeometry(100, 100, 600, 700)
        
        # Initial population of the table
        self.refresh_crew_list()
    
    def switch_user_role(self, role):
        """Change the current user's role for testing"""
        self.current_user = User(f"test_{role}", role)
        self.registry_proxy = CrewRegistryProxy(self.current_user)
        self.user_info_label.setText(f"Logged in as: {self.current_user.username} ({self.current_user.role})")
        
        # Update UI based on new permissions
        has_add = self.current_user.has_permission("add")
        self.crew_id_input.setEnabled(has_add)
        self.crew_name_input.setEnabled(has_add)
        self.crew_role_combo.setEnabled(has_add)
        self.crew_contact_input.setEnabled(has_add)
        self.add_crew_button.setEnabled(has_add)
        
        has_update = self.current_user.has_permission("update")
        self.flight_id_input.setEnabled(has_update)
        self.assign_flight_button.setEnabled(has_update)
        self.status_combo.setEnabled(has_update)
        self.update_status_button.setEnabled(has_update)
        
        # Refresh the list through the proxy
        self.refresh_crew_list()
        
        QMessageBox.information(self, "Role Changed", f"User role changed to {role}")
    
    def update_crew_combo(self):
        """Update the crew selection dropdown"""
        self.crew_select_combo.clear()
        
        try:
            for crew in self.registry_proxy.all_crew():
                # Handle both object and dictionary results from proxy
                if isinstance(crew, dict):
                    crew_id = crew["crew_id"]
                    name = crew["name"]
                else:
                    crew_id = crew.crew_id
                    name = crew.name
                self.crew_select_combo.addItem(f"{crew_id}: {name}", crew_id)
        except PermissionError as e:
            QMessageBox.warning(self, "Permission Error", str(e))
    
    def add_crew_member(self):
        """Add a new crew member"""
        try:
            crew_id = self.crew_id_input.value()
            name = self.crew_name_input.text().strip()
            role = self.crew_role_combo.currentText()
            contact = self.crew_contact_input.text().strip()
            
            if not name:
                raise ValueError("Name cannot be empty")
            
            # Create the crew member directly - it will self-register
            new_crew = CrewMember(crew_id, name, role, contact)
            
            # But check if we can see it through the proxy
            try:
                self.registry_proxy.get_crew_member(crew_id)
                QMessageBox.information(self, "Success", f"Added crew member: {name}")
                
                # Clear inputs
                self.crew_name_input.clear()
                self.crew_contact_input.clear()
                self.crew_id_input.setValue(self.crew_id_input.value() + 1)
                
                # Refresh displays
                self.refresh_crew_list()
                self.update_crew_combo()
            except PermissionError as e:
                QMessageBox.warning(self, "Permission Error", 
                                   "Created crew member but you don't have permission to view it: " + str(e))
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def assign_flight(self):
        if self.crew_select_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No crew members available")
            return
        
        crew_id = self.crew_select_combo.currentData()
        flight_id = self.flight_id_input.text().strip()
        
        if not flight_id:
            QMessageBox.warning(self, "Error", "Please enter a flight ID")
            return
        
        try:
            crew_member = self.registry_proxy.get_crew_member(crew_id)
            if crew_member:
                # Check if flight_details are supported (overloaded method)
                try:
                    # First try with flight details dictionary (new overloaded method)
                    flight_details = {
                        'id': flight_id,
                        'departure': '08:00',  # Example additional data
                        'arrival': '10:30'     # Example additional data
                    }
                    crew_member.assign_flight(flight_details)
                except (TypeError, AttributeError):
                    # Fall back to original method if overloaded one fails
                    crew_member.assign_flight(flight_id)
                
                QMessageBox.information(self, "Success", f"Assigned {crew_member.name} to flight {flight_id}")
                self.refresh_crew_list()
            else:
                QMessageBox.warning(self, "Error", "Crew member not found")
        except PermissionError as e:
            QMessageBox.warning(self, "Permission Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def update_crew_status(self):
        if self.crew_select_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No crew members available")
            return
        
        crew_id = self.crew_select_combo.currentData()
        new_status = self.status_combo.currentText()
        
        try:
            # Get the crew member through the proxy
            crew_member = self.registry_proxy.get_crew_member(crew_id)
            if crew_member:
                # Use the update_crew_member_status method from the proxy
                try:
                    # First try calling through the proxy
                    self.registry_proxy.update_crew_member_status(crew_id, new_status)
                    QMessageBox.information(self, "Success", f"Updated status to {new_status}")
                except AttributeError:
                    # Fall back to direct call if proxy doesn't support it
                    crew_member.update_status(new_status)
                    QMessageBox.information(self, "Success", f"Updated {crew_member.name}'s status to {new_status}")
                
                self.refresh_crew_list()
            else:
                QMessageBox.warning(self, "Error", "Crew member not found")
        except PermissionError as e:
            QMessageBox.warning(self, "Permission Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def refresh_crew_list(self):
        try:
            crew_list = self.registry_proxy.all_crew()
            self.crew_table.setRowCount(len(crew_list))
            
            for row, crew in enumerate(crew_list):
                # Handle both object and dictionary results from proxy
                if isinstance(crew, dict):
                    # Dictionary format
                    self.crew_table.setItem(row, 0, QTableWidgetItem(str(crew["crew_id"])))
                    self.crew_table.setItem(row, 1, QTableWidgetItem(crew["name"]))
                    self.crew_table.setItem(row, 2, QTableWidgetItem(crew["role"]))
                    self.crew_table.setItem(row, 3, QTableWidgetItem(crew["contact_info"]))
                    self.crew_table.setItem(row, 4, QTableWidgetItem(crew.get("assigned_flight") or "None"))
                    self.crew_table.setItem(row, 5, QTableWidgetItem(crew.get("status", "Unknown")))
                else:
                    # Object format
                    self.crew_table.setItem(row, 0, QTableWidgetItem(str(crew.crew_id)))
                    self.crew_table.setItem(row, 1, QTableWidgetItem(crew.name))
                    self.crew_table.setItem(row, 2, QTableWidgetItem(crew.role))
                    self.crew_table.setItem(row, 3, QTableWidgetItem(crew.contact_info))
                    self.crew_table.setItem(row, 4, QTableWidgetItem(crew.assigned_flight or "None"))
                    self.crew_table.setItem(row, 5, QTableWidgetItem(crew.status))
            
            self.crew_table.resizeColumnsToContents()
            self.update_crew_combo()
            
        except PermissionError as e:
            # Clear the table if no permission
            self.crew_table.setRowCount(0)
            QMessageBox.warning(self, "Permission Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh crew list: {str(e)}")

class AIAssistantWindow(QWidget):
    def __init__(self, seat_selection_window):
        super().__init__()
        self.seat_selection_window = seat_selection_window

        self.ai_assistant = AIAssistant()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
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
        
        self.chat_history.append("<b>AI Assistant:</b> Hello! Welcome to E-JUST Airways. How can I help you with your flight today?")

    def send_bot_message(self):

        self.flight = self.seat_selection_window.get_flight_info()

        user_message = self.chat_input.text().strip()
        if user_message == "flight":
            self.chat_history.append(f"<b>You:</b> {user_message}")
            flight_info = self.flight
            self.chat_history.append(f"<b>AI Assistant:</b> {flight_info}")
            self.chat_input.clear()
            return

        if not user_message:
            return
        
        self.chat_history.append(f"<b>You:</b> {user_message}")
        
        response = self.ai_assistant.process_query(user_message)
        
        self.chat_history.append(f"<b>AI Assistant:</b> {response}")
        
        self.chat_input.clear()
        
        self.process_bot_commands(user_message)
        
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def handle_quick_question(self, question):
        self.chat_input.setText(question)
        self.send_bot_message()

    def process_bot_commands(self, message):
        pass


class PaymentWindow(QDialog):
    def __init__(self, parent=None, passenger_name="", flight_info="", seat_id="", baggage_fee=0.0, ticket_price=149.99, host='localhost', port=8888):
        super().__init__(parent)
        self.parent = parent
        self.passenger_name = passenger_name
        self.flight_info = flight_info
        self.seat_id = seat_id
        self.baggage_fee = baggage_fee
        self.ticket_price = ticket_price
        self.payment_completed = False
        
        self.host = host
        self.port = port
        
        # Initialize credential manager for secure payment processing
        self.credentials_manager = CredentialsManager()
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_label = QLabel("Payment Processing", self)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        summary_group = QGroupBox("Order Summary")
        summary_layout = QFormLayout()
        
        passenger_label = QLabel(self.passenger_name)
        summary_layout.addRow("Passenger:", passenger_label)
        
        flight_label = QLabel(self.flight_info)
        summary_layout.addRow("Flight:", flight_label)
        
        seat_label = QLabel(self.seat_id)
        summary_layout.addRow("Seat:", seat_label)
        
        ticket_price_label = QLabel(f"${self.ticket_price:.2f}")
        summary_layout.addRow("Ticket Price:", ticket_price_label)
        
        baggage_fee_label = QLabel(f"${self.baggage_fee:.2f}")
        summary_layout.addRow("Baggage Fee:", baggage_fee_label)
        
        total_price = self.ticket_price + self.baggage_fee
        total_label = QLabel(f"${total_price:.2f}")
        total_label.setStyleSheet("font-weight: bold; color: #16a085;")
        summary_layout.addRow("Total:", total_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        payment_group = QGroupBox("Payment Method")
        payment_layout = QVBoxLayout()
        
        card_type_layout = QHBoxLayout()
        
        self.visa_radio = QRadioButton("Visa", self)
        self.visa_radio.setChecked(True)
        self.mastercard_radio = QRadioButton("MasterCard", self)
        self.amex_radio = QRadioButton("American Express", self)
        
        card_type_layout.addWidget(self.visa_radio)
        card_type_layout.addWidget(self.mastercard_radio)
        card_type_layout.addWidget(self.amex_radio)
        
        payment_layout.addLayout(card_type_layout)
        
        card_form = QFormLayout()
        
        self.card_number = QLineEdit(self)
        self.card_number.setPlaceholderText("1234 5678 9012 3456")
        self.card_number.setInputMask("9999 9999 9999 9999;_")
        card_form.addRow("Card Number:", self.card_number)
        
        expiry_layout = QHBoxLayout()
        self.expiry_month = QComboBox(self)
        self.expiry_month.addItems([f"{i:02d}" for i in range(1, 13)])
        
        self.expiry_year = QComboBox(self)
        current_year = datetime.now().year
        self.expiry_year.addItems([str(current_year + i) for i in range(10)])
        
        expiry_layout.addWidget(self.expiry_month)
        expiry_layout.addWidget(QLabel("/"))
        expiry_layout.addWidget(self.expiry_year)
        expiry_layout.addStretch()
        
        card_form.addRow("Expiration Date:", expiry_layout)
        
        self.cvv_code = QLineEdit(self)
        self.cvv_code.setPlaceholderText("123")
        self.cvv_code.setMaxLength(4)
        self.cvv_code.setFixedWidth(80)
        self.cvv_code.setEchoMode(QLineEdit.Password)
        card_form.addRow("CVV:", self.cvv_code)
        
        self.cardholder_name = QLineEdit(self)
        self.cardholder_name.setText(self.passenger_name)
        card_form.addRow("Cardholder Name:", self.cardholder_name)
        
        payment_layout.addLayout(card_form)
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        
        self.process_button = QPushButton("Process Payment", self)
        self.process_button.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.process_button.clicked.connect(self.process_payment)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.process_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setWindowTitle("Payment Processing")
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)
    
    def get_selected_card_type(self):
        if self.visa_radio.isChecked():
            return "Visa"
        elif self.mastercard_radio.isChecked():
            return "MasterCard"
        elif self.amex_radio.isChecked():
            return "American Express"
        return "Unknown"

    def prepare_payment_data(self):
        total_price = self.ticket_price + self.baggage_fee
        transaction_id = f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(self.passenger_name) % 10000:04d}"
        
        card_info = {
            "card_type": self.get_selected_card_type(),
            "card_number": self.card_number.text().replace(" ", ""),  # Store full card number temporarily
            "cardholder_name": self.cardholder_name.text(),
            "expiry_month": self.expiry_month.currentText(),
            "expiry_year": self.expiry_year.currentText(),
            "cvv": self.cvv_code.text()  # Store CVV temporarily
        }
        
        card_secret = f"{card_info['card_number']}:{card_info['cvv']}:{transaction_id}"
        
        # Encrypt the sensitive card data
        self.credentials_manager.encrypt_credentials(
            email=f"{card_info['cardholder_name']}_{transaction_id}", 
            password=card_secret
        )
        
        payment_data = {
            "transaction_id": transaction_id,
            "timestamp": datetime.now().isoformat(),
            "passenger_info": {
                "name": self.passenger_name,
                "flight": self.flight_info,
                "seat": self.seat_id
            },
            "payment_details": {
                "ticket_price": self.ticket_price,
                "baggage_fee": self.baggage_fee,
                "total_amount": total_price,
                "currency": "USD"
            },
            "card_info": {
                "card_type": card_info["card_type"],
                "card_number_masked": f"****-****-****-{self.card_number.text()[-4:]}",
                "cardholder_name": card_info["cardholder_name"],
                "expiry_month": card_info["expiry_month"],
                "expiry_year": card_info["expiry_year"],
                # CVV is not included in the payload, it's encrypted separately
            },
            "security": {
                "encrypted": True,
                "encryption_method": "fernet",
                "credentials_file": self.credentials_manager.creds_file
            },
            "status": "pending"
        }
        
        return payment_data
    
    def send_payment_data(self, payment_data):
        client_socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(15)
            
            print(f"Connecting to {self.host}:{self.port}...")
            client_socket.connect((self.host, self.port))
            print("Connected successfully!")
            
            json_data = json.dumps(payment_data, indent=2)
            message = json_data.encode('utf-8')
            
            print(f"Sending {len(message)} bytes of encrypted payment data...")
            client_socket.sendall(len(message).to_bytes(4, byteorder='big'))
            client_socket.sendall(message)
            print("Data sent successfully!")
            
            print("Waiting for response length...")
            response_length_bytes = client_socket.recv(4)
            if len(response_length_bytes) != 4:
                return "ERROR: Invalid response length header"
            
            response_length = int.from_bytes(response_length_bytes, byteorder='big')
            print(f"Expecting response of {response_length} bytes...")
            
            response_data = b''
            while len(response_data) < response_length:
                remaining = response_length - len(response_data)
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    return "ERROR: Connection closed while receiving response"
                response_data += chunk
            
            response = response_data.decode('utf-8')
            print(f"Received response: {response}")
            
            # After successful processing, clean up encrypted credentials
            if "SUCCESS" in response and os.path.exists(self.credentials_manager.creds_file):
                try:
                    os.remove(self.credentials_manager.creds_file)
                    print("Temporary encrypted credentials cleaned up")
                except Exception as e:
                    print(f"Warning: Could not clean up credentials file: {e}")
                    
            return response
                
        except socket.timeout:
            return "ERROR: Connection timeout - server may be down"
        except ConnectionRefusedError:
            return "ERROR: Unable to connect to payment server - please ensure server is running"
        except Exception as e:
            return f"ERROR: Network error - {str(e)}"
        finally:
            if client_socket:
                try:
                    client_socket.close()
                except:
                    pass
    def process_payment(self):
        # Validation
        if not self.card_number.text().replace(" ", "").isdigit() or len(self.card_number.text().replace(" ", "")) < 16:
            self.status_label.setText("Invalid card number")
            self.status_label.setStyleSheet("color: #c0392b;")
            return
            
        if not self.cvv_code.text().isdigit() or len(self.cvv_code.text()) < 3:
            self.status_label.setText("Invalid CVV code")
            self.status_label.setStyleSheet("color: #c0392b;")
            return
            
        if not self.cardholder_name.text():
            self.status_label.setText("Please enter cardholder name")
            self.status_label.setStyleSheet("color: #c0392b;")
            return
        
        self.process_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        self.status_label.setText("Processing payment...")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        self.progress_bar.setVisible(True)
        
        self.worker_thread = PaymentWorkerThread(self)
        self.worker_thread.payment_response.connect(self.handle_payment_response)
        self.worker_thread.start()
    
    def handle_payment_response(self, response):
        self.progress_bar.setVisible(False)
        
        if response.startswith("ERROR:"):
            self.status_label.setText(f"Payment Failed: {response[7:]}")
            self.status_label.setStyleSheet("color: #c0392b;")
            self.process_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
        elif "SUCCESS" in response:
            self.status_label.setText("Payment Successful!")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.payment_completed = True
            self.cancel_button.setText("Close")
            self.cancel_button.setEnabled(True)
            self.process_button.setVisible(False)
            QTimer.singleShot(1500, lambda: self.accept())
        else:
            self.status_label.setText("Payment processed - please check confirmation")
            self.status_label.setStyleSheet("color: #f39c12;")
            self.payment_completed = True
            self.cancel_button.setText("Close")
            self.cancel_button.setEnabled(True)
            self.process_button.setVisible(False)
            QTimer.singleShot(1500, lambda: self.accept())

class PaymentWorkerThread(QThread):
    payment_response = pyqtSignal(str)
    
    def __init__(self, payment_window):
        super().__init__()
        self.payment_window = payment_window
    
    def run(self):
        try:
            payment_data = self.payment_window.prepare_payment_data()
            response = self.payment_window.send_payment_data(payment_data)
            self.payment_response.emit(response)
        except Exception as e:
            self.payment_response.emit(f"ERROR: {str(e)}")


# PaymentServer class
class PaymentServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.transactions_dir = "transactions"
        self.log_file = "payment_transactions.log"
        
        # Initialize the credentials manager for decryption
        self.credentials_manager = CredentialsManager()
        
        # Create transactions directory if it doesn't exist
        if not os.path.exists(self.transactions_dir):
            os.makedirs(self.transactions_dir)
    
    def start_server(self):
        """Start the payment server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"Payment server started on {self.host}:{self.port}")
            self.log_transaction("SERVER", f"Payment server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"Connection from {addr}")
                    self.handle_client(client_socket, addr)
                except Exception as e:
                    if self.running:  # Only print error if server is supposed to be running
                        print(f"Error accepting connection: {e}")
                        self.log_transaction("ERROR", f"Error accepting connection: {e}")
        
        except Exception as e:
            print(f"Server error: {e}")
            self.log_transaction("ERROR", f"Server startup error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def stop_server(self):
        """Stop the payment server"""
        self.running = False
        try:
            # Connect to our own server to unblock accept()
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect((self.host, self.port))
            temp_socket.close()
        except:
            pass
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        print("Payment server stopped")
        self.log_transaction("SERVER", "Payment server stopped")
    
    def handle_client(self, client_socket, addr):
        """Handle client connection with encryption support"""
        try:
            # Receive message length
            length_bytes = client_socket.recv(4)
            if len(length_bytes) != 4:
                print("Invalid length header")
                return
                
            message_length = int.from_bytes(length_bytes, byteorder='big')
            print(f"Expecting message of {message_length} bytes")
            
            # Receive message data
            message_data = b''
            while len(message_data) < message_length:
                remaining = message_length - len(message_data)
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    break
                message_data += chunk
            
            if len(message_data) < message_length:
                print(f"Incomplete message: {len(message_data)}/{message_length} bytes")
                return
                
            # Parse message
            message = message_data.decode('utf-8')
            payment_data = json.loads(message)
            
            # Extract transaction ID for logging
            transaction_id = payment_data.get('transaction_id', 'UNKNOWN')
            
            print(f"Received payment data for transaction: {transaction_id}")
            self.log_transaction(transaction_id, f"Received payment request from {addr}")
            
            if payment_data.get('security', {}).get('encrypted', False):
                print("Received encrypted payment data, decrypting...")
                
                try:
                    email, password = self.credentials_manager.decrypt_credentials()
                    
                    if email and password:
                        card_parts = password.split(':')
                        if len(card_parts) == 3 and card_parts[2] == transaction_id:
                            # Successfully decrypted matching transaction
                            card_number = card_parts[0]
                            cvv = card_parts[1]
                            
                            # Add back the sensitive data for processing (would normally be sent to payment processor)
                            payment_data['card_info']['card_number_full'] = card_number
                            payment_data['card_info']['cvv'] = cvv
                            
                            print(f"Successfully decrypted payment data for transaction {transaction_id}")
                            self.log_transaction(transaction_id, "Payment data decrypted successfully")
                        else:
                            print("Error: Transaction ID mismatch in decrypted data")
                            self.log_transaction(transaction_id, "ERROR: Transaction ID mismatch in decrypted data")
                    else:
                        print("Error: Could not decrypt credentials")
                        self.log_transaction(transaction_id, "ERROR: Could not decrypt credentials")
                        
                except Exception as e:
                    print(f"Decryption error: {e}")
                    self.log_transaction(transaction_id, f"ERROR: Decryption failed - {str(e)}")
            
            # Process payment (simulated)
            payment_data['status'] = 'approved'
            payment_data['authorization_code'] = f"AUTH_{hash(transaction_id) % 1000000:06d}"
            payment_data['processed_at'] = datetime.now().isoformat()
            
            # Remove sensitive data before saving
            if 'card_info' in payment_data:
                if 'card_number_full' in payment_data['card_info']:
                    del payment_data['card_info']['card_number_full']
                if 'cvv' in payment_data['card_info']:
                    del payment_data['card_info']['cvv']
            
            # Save transaction data
            self.save_transaction(transaction_id, payment_data)
            
            # Send response
            response = "SUCCESS: Payment processed successfully"
            response_data = response.encode('utf-8')
            
            client_socket.sendall(len(response_data).to_bytes(4, byteorder='big'))
            client_socket.sendall(response_data)
            
            print(f"Payment processed for transaction: {transaction_id}")
            self.log_transaction(transaction_id, "Payment processed successfully")
            
        except Exception as e:
            print(f"Error handling client: {e}")
            self.log_transaction("ERROR", f"Client handling error: {e}")
            
            # Try to send error response
            try:
                error_msg = f"ERROR: {str(e)}"
                error_data = error_msg.encode('utf-8')
                client_socket.sendall(len(error_data).to_bytes(4, byteorder='big'))
                client_socket.sendall(error_data)
            except:
                pass
                
        finally:
            client_socket.close()
    
    def save_transaction(self, transaction_id, payment_data):
        """Save transaction data to file"""
        try:
            filename = os.path.join(self.transactions_dir, f"{transaction_id}.json")
            with open(filename, 'w') as f:
                json.dump(payment_data, f, indent=2)
            print(f"Transaction saved to {filename}")
        except Exception as e:
            print(f"Error saving transaction: {e}")
            self.log_transaction(transaction_id, f"ERROR: Could not save transaction - {str(e)}")
    
    def log_transaction(self, transaction_id, message):
        """Log transaction activity"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{transaction_id}] {message}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log: {e}")

# Modify PaymentManagementWindow to include security status
class PaymentManagementWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.payment_server = None
        self.server_thread = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        server_group = QGroupBox("Payment Server Control")
        server_layout = QVBoxLayout()
        
        self.status_label = QLabel("Payment Server: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: #c0392b;")
        server_layout.addWidget(self.status_label)
        
        button_layout = QHBoxLayout()
        
        self.start_server_btn = QPushButton("Start Payment Server")
        self.start_server_btn.clicked.connect(self.start_payment_server)
        button_layout.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("Stop Payment Server")
        self.stop_server_btn.clicked.connect(self.stop_payment_server)
        self.stop_server_btn.setEnabled(False)
        button_layout.addWidget(self.stop_server_btn)
        
        server_layout.addLayout(button_layout)
        
        # Add security status
        security_label = QLabel("Encryption: Enabled (Fernet)")
        security_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        server_layout.addWidget(security_label)
        
        info_label = QLabel("Server will run on localhost:8888 with encrypted payment processing")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        server_layout.addWidget(info_label)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # Security Info Group
        security_group = QGroupBox("Security Information")
        security_layout = QVBoxLayout()
        
        security_info = QLabel(
            "Payment data is encrypted using Fernet symmetric encryption:\n"
            "• Card numbers and CVV codes are never stored in plain text\n"
            "• Sensitive data is encrypted during transmission\n"
            "• Temporary encryption keys are used for each transaction\n"
            "• Credentials are securely cleaned up after processing"
        )
        security_info.setStyleSheet("color: #2c3e50;")
        security_layout.addWidget(security_info)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Test Payment Group
        test_group = QGroupBox("Test Payment Processing")
        test_layout = QVBoxLayout()
        
        test_label = QLabel("Test the payment system with sample data:")
        test_layout.addWidget(test_label)
        
        self.test_payment_btn = QPushButton("Open Test Payment Window")
        self.test_payment_btn.clicked.connect(self.open_test_payment)
        self.test_payment_btn.setEnabled(False)  # Disabled until server starts
        test_layout.addWidget(self.test_payment_btn)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # Transaction Logs Group
        logs_group = QGroupBox("Transaction Logs")
        logs_layout = QVBoxLayout()
        
        logs_info = QLabel("Transaction logs will be saved to:\n• payment_transactions.log\n• transactions/ directory")
        logs_info.setStyleSheet("color: #7f8c8d;")
        logs_layout.addWidget(logs_info)
        
        self.view_logs_btn = QPushButton("View Recent Transactions")
        self.view_logs_btn.clicked.connect(self.view_transaction_logs)
        logs_layout.addWidget(self.view_logs_btn)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def start_payment_server(self):
        """Start the payment server in a separate thread"""
        if self.payment_server is None or not getattr(self.payment_server, 'running', False):
            self.payment_server = PaymentServer(host='localhost', port=8888)
            
            def run_server():
                try:
                    self.payment_server.start_server()
                except Exception as e:
                    print(f"Server error: {e}")
            
            self.server_thread = threading.Thread(target=run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Give server time to start
            QTimer.singleShot(1000, self.update_server_status)
            
            self.start_server_btn.setEnabled(False)
            self.stop_server_btn.setEnabled(True)
            self.status_label.setText("Payment Server: Starting...")
            self.status_label.setStyleSheet("font-weight: bold; color: #f39c12;")
    
    def stop_payment_server(self):
        if self.payment_server:
            self.payment_server.stop_server()
            self.payment_server = None
        
        self.status_label.setText("Payment Server: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: #c0392b;")
        self.start_server_btn.setEnabled(True)
        self.stop_server_btn.setEnabled(False)
        self.test_payment_btn.setEnabled(False)
    
    def update_server_status(self):
        """Update server status display"""
        if self.payment_server and getattr(self.payment_server, 'running', False):
            self.status_label.setText("Payment Server: Running on localhost:8888 (Encrypted)")
            self.status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            self.test_payment_btn.setEnabled(True)
        else:
            self.status_label.setText("Payment Server: Failed to start")
            self.status_label.setStyleSheet("font-weight: bold; color: #c0392b;")
            self.start_server_btn.setEnabled(True)
            self.stop_server_btn.setEnabled(False)
    
    def open_test_payment(self):
        payment_window = PaymentWindow(
            parent=self,
            passenger_name="John Smith",
            flight_info="EJ123 - Cairo to Alexandria",
            seat_id="12A",
            baggage_fee=25.00,
            ticket_price=299.99,
            host='localhost',
            port=8888
        )
        
        result = payment_window.exec_()
        
        if result == payment_window.Accepted and payment_window.payment_completed:
            QMessageBox.information(self, "Payment Success", "Payment completed successfully with encryption!")
        else:
            QMessageBox.information(self, "Payment Info", "Payment was cancelled or failed")
    
    def view_transaction_logs(self):
        """Show a simple dialog with recent transaction info"""
        try:
            import os
            import json
            from datetime import datetime
            
            transactions_dir = "transactions"
            if not os.path.exists(transactions_dir):
                QMessageBox.information(self, "No Transactions", "No transactions found yet.")
                return
            
            files = [f for f in os.listdir(transactions_dir) if f.endswith('.json')]
            if not files:
                QMessageBox.information(self, "No Transactions", "No transactions found yet.")
                return
            
            files.sort(reverse=True)
            recent_files = files[:5]
            
            log_text = "Recent Transactions (Encrypted Processing):\n\n"
            for file in recent_files:
                try:
                    with open(os.path.join(transactions_dir, file), 'r') as f:
                        data = json.load(f)
                        passenger = data.get('passenger_info', {}).get('name', 'Unknown')
                        amount = data.get('payment_details', {}).get('total_amount', 0)
                        timestamp = data.get('timestamp', 'Unknown')
                        encryption_status = "🔒 Encrypted" if data.get('security', {}).get('encrypted', False) else "⚠️ Unencrypted"
                        log_text += f"• {passenger} - ${amount:.2f} - {timestamp} - {encryption_status}\n"
                except:
                    continue
            
            # Show in a message box
            msg = QMessageBox(self)
            msg.setWindowTitle("Recent Transactions")
            msg.setText(log_text)
            msg.setStyleSheet("QLabel { min-width: 450px; }")
            msg.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load transaction logs: {str(e)}")

class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.payment_management = None

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

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        app_title = QLabel("E-JUST Airways", self)
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2980b9;")
        header_layout.addWidget(app_title)

        header_layout.addStretch()
        layout.addWidget(header)

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

        self.seat_window = SeatSelectionWindow()
        self.feedback_window = FeedbackWindow()
        self.baggage_window = BaggageInfoWindow()
        self.crew_window = CrewManagementWindow()
        self.ai_assistant_window = AIAssistantWindow(self.seat_window)
        self.payment_management = PaymentManagementWindow(self)

        tabs.addTab(self.seat_window, "Seat Selection")
        tabs.addTab(self.feedback_window, "Feedback")
        tabs.addTab(self.baggage_window, "Baggage Info")
        tabs.addTab(self.crew_window, "Crew Management")
        tabs.addTab(self.ai_assistant_window, "AI Assistant")
        tabs.addTab(self.payment_management, "Payment System")

        layout.addWidget(tabs)
        
        self.setLayout(layout)
        self.setWindowTitle("Flight Booking System")
        self.setGeometry(100, 100, 800, 900)
    
    def closeEvent(self, event):
        if self.payment_management and self.payment_management.payment_server:
            self.payment_management.stop_payment_server()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)  

    main_app = MainApplication()
    main_app.show()

    sys.exit(app.exec_())