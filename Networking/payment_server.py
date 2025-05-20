import socket
import threading
import json
import logging
from datetime import datetime
import os

class PaymentServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('payment_transactions.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        if not os.path.exists('transactions'):
            os.makedirs('transactions')
    
    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"Payment server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.info(f"Connection from {client_address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, client_address):
        try:
            client_socket.settimeout(30)
            
            length_bytes = client_socket.recv(4)
            if not length_bytes or len(length_bytes) != 4:
                self.logger.warning(f"Invalid length header from {client_address}")
                return
            
            data_length = int.from_bytes(length_bytes, byteorder='big')
            self.logger.info(f"Expecting {data_length} bytes from {client_address}")
            
            received_data = b''
            while len(received_data) < data_length:
                remaining = data_length - len(received_data)
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    self.logger.warning(f"Connection closed while receiving data from {client_address}")
                    break
                received_data += chunk
            
            if len(received_data) != data_length:
                self.logger.error(f"Data length mismatch from {client_address}: expected {data_length}, got {len(received_data)}")
                error_response = "ERROR: Data transmission incomplete"
                self.send_response(client_socket, error_response)
                return
            
            try:
                payment_data = json.loads(received_data.decode('utf-8'))
                self.logger.info(f"Received valid JSON from {client_address}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON from {client_address}: {e}")
                error_response = "ERROR: Invalid JSON data"
                self.send_response(client_socket, error_response)
                return
            
            response = self.process_payment(payment_data, client_address)
            
            self.send_response(client_socket, response)
            
        except socket.timeout:
            self.logger.error(f"Timeout handling client {client_address}")
            error_response = "ERROR: Request timeout"
            try:
                self.send_response(client_socket, error_response)
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"Error handling client {client_address}: {e}")
            error_response = f"ERROR: {str(e)}"
            try:
                self.send_response(client_socket, error_response)
            except:
                pass
            
        finally:
            try:
                client_socket.close()
                self.logger.info(f"Connection closed for {client_address}")
            except:
                pass
    
    def send_response(self, client_socket, response):
        try:
            response_bytes = response.encode('utf-8')
            client_socket.sendall(len(response_bytes).to_bytes(4, byteorder='big'))
            client_socket.sendall(response_bytes)
            self.logger.info(f"Response sent: {response[:50]}...")
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
    
    def process_payment(self, payment_data, client_address):
        try:
            transaction_id = payment_data.get('transaction_id', 'UNKNOWN')
            passenger_name = payment_data.get('passenger_info', {}).get('name', 'Unknown')
            total_amount = payment_data.get('payment_details', {}).get('total_amount', 0)
            card_type = payment_data.get('card_info', {}).get('card_type', 'Unknown')
            
            self.logger.info(f"Processing payment: {transaction_id}")
            self.logger.info(f"Passenger: {passenger_name}")
            self.logger.info(f"Amount: ${total_amount:.2f}")
            self.logger.info(f"Card Type: {card_type}")
            
            self.save_transaction(payment_data)
            
            success = self.simulate_payment_processing(payment_data)
            
            if success:
                response = f"SUCCESS: Payment processed for transaction {transaction_id}"
                self.logger.info(f"Payment successful: {transaction_id}")
            else:
                response = f"ERROR: Payment failed for transaction {transaction_id}"
                self.logger.warning(f"Payment failed: {transaction_id}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Payment processing error: {e}")
            return f"ERROR: Payment processing failed - {str(e)}"
    
    def simulate_payment_processing(self, payment_data):
        card_number = payment_data.get('card_info', {}).get('card_number_masked', '')
        total_amount = payment_data.get('payment_details', {}).get('total_amount', 0)
        
        if total_amount <= 0:
            return False
        
        if total_amount > 10000:
            return False
        
        if not card_number or card_number.startswith('****-****-****-0000'):
            return False
        
        import random
        return random.random() > 0.05
    
    def save_transaction(self, payment_data):
        try:
            transaction_id = payment_data.get('transaction_id', 'UNKNOWN')
            filename = f"transactions/transaction_{transaction_id}.json"
            
            with open(filename, 'w') as f:
                json.dump(payment_data, f, indent=2)
            
            self.logger.info(f"Transaction saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving transaction: {e}")
    
    def stop_server(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.info("Payment server stopped")

def main():
    server = PaymentServer(host='localhost', port=8888)
    
    try:
        print("Starting Payment Server...")
        print("Press Ctrl+C to stop the server")
        server.start_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop_server()

if __name__ == "__main__":
    main()