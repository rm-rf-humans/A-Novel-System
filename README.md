# Efficient Flight Scheduling and Seat Allocation in a Modern Reservation System

A comprehensive PyQt5-based flight booking and management system with AI assistance, document verification, secure payment processing, and advanced crew management capabilities.

## Key Features

### Core Application
- **Modern GUI Interface** - Intuitive PyQt5-based desktop application
- **Complete Flight Management** - Search, book, and manage flights with real-time seat selection
- **AI-Powered Assistant** - Natural language chatbot for customer support and booking assistance
- **Document Verification** - OCR-based passport/ID scanning with fraud detection
- **Secure Payment Gateway** - Encrypted payment processing with real-time transaction handling
- **Smart Seat Assignment** - Preference-based seating with passenger categorization

### Advanced Features
- **Crew Management System** - Role-based access control for airline staff
- **Baggage Fee Calculator** - Automated weight validation and fee computation
- **Email Reminder System** - Automated flight notifications
- **Customer Feedback** - Review and rating collection system
- **Database Integration** - MySQL backend with comprehensive data management

## System Architecture

Built with enterprise-grade design patterns:
- **Model-View-Controller (MVC)** - Clean separation of concerns
- **Singleton Pattern** - Database connections and system registries
- **Proxy Pattern** - Access control and caching mechanisms
- **Factory Pattern** - Dynamic document processor creation
- **Observer Pattern** - Real-time UI updates and notifications

## Quick Start

### Prerequisites
```bash
# System Requirements
Python 3.8+
MySQL Server
Tesseract OCR Engine
```

### Installation
```bash
# Clone and setup
git clone https://github.com/rm-rf-humans/A-Novel-System
cd flight-booking-system
pip install -r requirements.txt

# Database setup
mysql -u root -p
CREATE DATABASE flight_booking;
```

### Launch Application
```python
# Run the main application
python main.py

# Start payment server (separate terminal)
python Networking/payment_server.py
```

## Application Windows

### Main Seat Selection Window
- **Flight Selection** - Browse available flights with real-time data
- **Interactive Seat Map** - Visual seat selection with availability indicators
- **Passenger Information** - Complete passenger details with document scanning
- **Baggage Management** - Weight validation and fee calculation
- **Payment Integration** - Secure payment processing with encryption

### Specialized Windows
- **AI Assistant** - Natural language query processing
- **Crew Management** - Staff scheduling and role-based permissions
- **Payment Management** - Transaction monitoring and server control
- **Feedback System** - Customer review collection

## Security Features

### Payment Security
- **End-to-End Encryption** - Fernet encryption for sensitive payment data
- **Secure Credential Storage** - Encrypted card information handling
- **Transaction Logging** - Comprehensive audit trails
- **Real-time Validation** - CVV and card number verification

### Access Control
- **Role-Based Permissions** - Admin, Staff, and Guest access levels
- **Document Verification** - OCR with fraud detection algorithms
- **Secure Database Connections** - Encrypted MySQL communication

## Database Schema

```sql
-- Core Tables
flights (flight_id, airline, source, destination, times, capacity)
passengers (passenger_id, name, age, type, preferences)
seats (seat_id, flight_id, availability, type)
bookings (booking_id, ticket_id, passenger_id, flight_id, seat_id)
baggage (baggage_id, passenger_id, weight, fee)
```

## AI Assistant Capabilities

The integrated AI assistant handles:
- **Flight Booking** - "Book a flight from Cairo to Alexandria"
- **Status Inquiries** - "What's the status of flight EJ123?"
- **Cancellations** - "Cancel my reservation TKT001"
- **General Support** - Baggage policies, flight information, help

## Configuration

### Database Connection
```python
# Database/database_handler.py
DatabaseHandler(
    host="localhost",
    user="root",
    password="your_password",
    database="flight_booking"
)
```

### Payment Server
```python
# Default: localhost:8888
PaymentServer(host='localhost', port=8888)
```

### Tesseract OCR
```python
# ML/ID.py - Update path if needed
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
```

## Usage Examples

### Basic Flight Booking
1. Launch application → Select flight → Choose seat
2. Enter passenger details or scan ID document
3. Configure baggage options
4. Process secure payment
5. Receive confirmation with ticket ID

### Crew Management
1. Access crew management window
2. Switch user roles (Admin/Staff/Guest)
3. Add crew members, assign flights, update status
4. View comprehensive crew schedules

### AI Assistant
1. Open AI assistant window
2. Ask natural language questions
3. Get instant responses for bookings, status, support

## Testing & Development

### Run Application
```bash
# Main application
python main.py

# Individual components
python -m ML.Bot  # AI Assistant tests
python -m ML.ID   # Document verification tests
```

### Payment Server Testing
1. Start payment server from application
2. Use "Test Payment" feature
3. Monitor transaction logs and encryption

## Dependencies

```txt
PyQt5==5.15.11              # GUI Framework
cryptography==45.0.2        # Payment Encryption
mysql_connector_repackaged   # Database Connectivity
opencv_python==4.10.0.84     # Image Processing
pytesseract==0.3.13         # OCR Engine
numpy==2.2.6                # Numerical Computing
multipledispatch==1.0.0     # Method Overloading
```

## Quick Demo

1. **Start Application**: `python main.py`
2. **Select Flight**: Choose from dropdown menu
3. **Pick Seat**: Click on available seat (blue = available, gray = taken)
4. **Enter Details**: Fill passenger information or scan ID
5. **Process Payment**: Use integrated payment system
6. **Get Confirmation**: Receive ticket with booking details

## Advanced Features

### Smart Passenger Types
- **Socializer** - Networking preferences with interest matching
- **Tall Passenger** - Automatic legroom seat assignment
- **Eco-Friendly** - Sustainable meal recommendations

### Document Processing
- **Passport Scanning** - Extract name, DOB, passport number
- **ID Card Processing** - Driver's license and ID card support
- **Fraud Detection** - Automated validation and scoring

### Payment Processing
- **Multi-Card Support** - Visa, MasterCard, American Express
- **Real-time Processing** - Instant payment validation
- **Transaction Security** - Encrypted data transmission
- **Audit Logging** - Complete transaction history

## Troubleshooting

### Common Issues
- **Database Connection**: Ensure MySQL is running and credentials are correct
- **Tesseract OCR**: Verify installation and path configuration
- **Payment Server**: Check if port 8888 is available
- **PyQt5 Issues**: Ensure all GUI dependencies are installed

### Error Handling
The system includes comprehensive error handling with:
- Database connection retry logic
- OCR fallback to mock data
- Payment processing validation
- Graceful UI error messaging

---

**Built with ❤️ to make the world a better place**
