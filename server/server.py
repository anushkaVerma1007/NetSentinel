# server/server.py
import socket
import threading
import json
import sys
sys.path.append('..')
from utils.config import SERVER_HOST, SERVER_PORT, MAX_CONNECTIONS
from database.db import Database
from ml.anomaly_model import AnomalyDetector

class NetSentinelServer:
    def __init__(self):
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.server_socket = None
        self.db = Database()
        self.ml_model = AnomalyDetector()
        self.active_connections = 0
        self.lock = threading.Lock()

    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            
            print(f"🚀 NetSentinel Server started on {self.host}:{self.port}")
            print(f"📡 Listening for connections... (Max: {MAX_CONNECTIONS})")
            
            while True:
                client_socket, address = self.server_socket.accept()
                
                with self.lock:
                    self.active_connections += 1
                
                print(f"✅ New connection from {address} (Active: {self.active_connections})")
                
                # Create a new thread for each client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n⏹️ Server shutting down...")
            self.shutdown()
        except Exception as e:
            print(f"❌ Server error: {e}")
            self.shutdown()

    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        try:
            while True:
                # Receive data from client
                data = client_socket.recv(1024).decode('utf-8')
                
                if not data:
                    break
                
                # Parse packet data
                try:
                    packet = json.loads(data)
                    self.process_packet(packet, address)
                    
                    # Send acknowledgment
                    response = {"status": "received", "packet_id": packet.get('id', 'unknown')}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON from {address}")
                    
        except Exception as e:
            print(f"❌ Error handling client {address}: {e}")
        finally:
            client_socket.close()
            with self.lock:
                self.active_connections -= 1
            print(f"❌ Connection closed from {address} (Active: {self.active_connections})")

    def process_packet(self, packet, address):
        """Process received packet using FCFS scheduling"""
        try:
            source_ip = packet.get('source_ip', str(address[0]))
            dest_ip = packet.get('dest_ip', 'unknown')
            packet_size = packet.get('packet_size', 0)
            protocol = packet.get('protocol', 'TCP')
            
            # ML anomaly detection
            is_anomaly = self.ml_model.predict(packet_size, protocol)
            
            # Convert numpy bool to Python bool for PostgreSQL
            is_anomaly = bool(is_anomaly)
            
            # Store in database
            self.db.insert_packet(source_ip, dest_ip, packet_size, protocol, is_anomaly)
            
            # Log the packet
            status = "🚨 ANOMALY" if is_anomaly else "✅ NORMAL"
            print(f"{status} | {source_ip} → {dest_ip} | {packet_size}B | {protocol}")
            
        except Exception as e:
            print(f"❌ Error processing packet: {e}")

    def shutdown(self):
        """Shutdown the server gracefully"""
        if self.server_socket:
            self.server_socket.close()
        if self.db:
            self.db.close()
        print("✅ Server shutdown complete")

if __name__ == "__main__":
    server = NetSentinelServer()
    server.start()