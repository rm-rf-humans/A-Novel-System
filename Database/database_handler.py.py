import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DatabaseHandler:
    def __init__(self, host="localhost", user="root", password="", database="flight_booking"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return False
        
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def fetch_data(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchall()
            cursor.close()
            return result
        return None
    
    def create_tables(self):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    flight_id VARCHAR(10) PRIMARY KEY,
                    airline VARCHAR(50) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    destination VARCHAR(50) NOT NULL,
                    departure_time TIME NOT NULL,
                    arrival_time TIME NOT NULL,
                    flight_date DATE NOT NULL,
                    capacity INT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passengers (
                    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    age INT,
                    passenger_type VARCHAR(20),
                    preferences VARCHAR(50),
                    special_data VARCHAR(100)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seats (
                    seat_id VARCHAR(5) PRIMARY KEY,
                    flight_id VARCHAR(10) NOT NULL,
                    is_available BOOLEAN DEFAULT TRUE,
                    seat_type VARCHAR(20),
                    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INT AUTO_INCREMENT PRIMARY KEY,
                    ticket_id VARCHAR(20) UNIQUE NOT NULL,
                    passenger_id INT NOT NULL,
                    flight_id VARCHAR(10) NOT NULL,
                    seat_id VARCHAR(5) NOT NULL,
                    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    payment_status BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
                    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
                    FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS baggage (
                    baggage_id INT AUTO_INCREMENT PRIMARY KEY,
                    passenger_id INT NOT NULL,
                    weight DECIMAL(5,2) NOT NULL,
                    fee DECIMAL(6,2) NOT NULL,
                    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
                )
            """)
            
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error creating tables: {e}")
            return False
    
    def add_flight(self, flight_id, airline, source, destination, departure_time, arrival_time, flight_date, capacity):
        query = """
            INSERT INTO flights (flight_id, airline, source, destination, departure_time, arrival_time, flight_date, capacity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (flight_id, airline, source, destination, departure_time, arrival_time, flight_date, capacity)
        cursor = self.execute_query(query, params)
        if cursor:
            return True
        return False
    
    def get_all_flights(self):
        query = "SELECT * FROM flights"
        return self.fetch_data(query)
    
    def get_flight_by_id(self, flight_id):
        query = "SELECT * FROM flights WHERE flight_id = %s"
        result = self.fetch_data(query, (flight_id,))
        if result and len(result) > 0:
            return result[0]
        return None
    
    def initialize_seats_for_flight(self, flight_id, seat_map):
        success = True
        for seat_id, is_available in seat_map.items():
            seat_type = "Window" if seat_id.endswith(('A', 'D')) else "Middle"
            
            query = """
                INSERT INTO seats (seat_id, flight_id, is_available, seat_type)
                VALUES (%s, %s, %s, %s)
            """
            params = (seat_id, flight_id, is_available, seat_type)
            cursor = self.execute_query(query, params)
            if not cursor:
                success = False
        
        return success
    
    def get_available_seats(self, flight_id):
        query = """
            SELECT seat_id, seat_type 
            FROM seats 
            WHERE flight_id = %s AND is_available = TRUE
        """
        return self.fetch_data(query, (flight_id,))
    
    def update_seat_availability(self, seat_id, flight_id, is_available):
        query = """
            UPDATE seats 
            SET is_available = %s 
            WHERE seat_id = %s AND flight_id = %s
        """
        params = (is_available, seat_id, flight_id)
        cursor = self.execute_query(query, params)
        if cursor:
            return True
        return False
    
    def add_passenger(self, name, email, age, passenger_type, preferences, special_data=None):
        query = """
            INSERT INTO passengers (name, email, age, passenger_type, preferences, special_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, email, age, passenger_type, preferences, special_data)
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_passenger_by_id(self, passenger_id):
        query = "SELECT * FROM passengers WHERE passenger_id = %s"
        result = self.fetch_data(query, (passenger_id,))
        if result and len(result) > 0:
            return result[0]
        return None
    
    def create_booking(self, ticket_id, passenger_id, flight_id, seat_id, payment_status=False):
        query = """
            INSERT INTO bookings (ticket_id, passenger_id, flight_id, seat_id, payment_status)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (ticket_id, passenger_id, flight_id, seat_id, payment_status)
        cursor = self.execute_query(query, params)
        if cursor:
            self.update_seat_availability(seat_id, flight_id, False)
            return True
        return False
    
    def update_booking_payment(self, ticket_id, payment_status):
        query = """
            UPDATE bookings 
            SET payment_status = %s 
            WHERE ticket_id = %s
        """
        params = (payment_status, ticket_id)
        cursor = self.execute_query(query, params)
        if cursor:
            return True
        return False
    
    def get_booking_by_ticket(self, ticket_id):
        query = """
            SELECT b.*, p.name, p.email, f.airline, f.source, f.destination, f.flight_date
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE b.ticket_id = %s
        """
        result = self.fetch_data(query, (ticket_id,))
        if result and len(result) > 0:
            return result[0]
        return None
    
    def add_baggage(self, passenger_id, weight, fee):
        query = """
            INSERT INTO baggage (passenger_id, weight, fee)
            VALUES (%s, %s, %s)
        """
        params = (passenger_id, weight, fee)
        cursor = self.execute_query(query, params)
        if cursor:
            return True
        return False
    
    def get_baggage_by_passenger(self, passenger_id):
        query = "SELECT * FROM baggage WHERE passenger_id = %s"
        return self.fetch_data(query, (passenger_id,))
