# client/client.py
import socket
import json
import random
import time
import sys
sys.path.append('..')
from utils.config import SERVER_HOST, SERVER_PORT, PROTOCOLS

class TrafficGenerator:
    def __init__(self, client_id):
        self.client_id = client_id
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.socket = None

    def generate_packet(self):
        """Generate random packet data"""
        packet = {
            'id': f"PKT-{self.client_id}-{random.randint(1000, 9999)}",
            'source_ip': f"192.168.1.{random.randint(1, 254)}",
            'dest_ip': f"10.0.0.{random.randint(1, 254)}",
            'packet_size': random.randint(64, 1500),
            'protocol': random.choice(PROTOCOLS)
        }
        
        # Occasionally generate anomalous packets
        if random.random() < 0.1:  # 10% chance of anomaly
            packet['packet_size'] = random.choice([
                random.randint(20, 50),      # Very small
                random.randint(5000, 10000)  # Very large
            ])
        
        return packet

    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ Client {self.client_id} connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def send_traffic(self, num_packets=10, delay=1):
        """Send multiple packets to the server"""
        if not self.connect():
            return
        
        try:
            for i in range(num_packets):
                # Generate and send packet
                packet = self.generate_packet()
                self.socket.send(json.dumps(packet).encode('utf-8'))
                print(f"📤 Sent: {packet['id']} | {packet['packet_size']}B | {packet['protocol']}")
                
                # Receive acknowledgment
                response = self.socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)
                print(f"📥 Ack: {response_data['status']}")
                
                # Wait before sending next packet
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Client {self.client_id} stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.socket.close()
            print(f"✅ Client {self.client_id} disconnected")

    def send_continuous(self, delay=2):
        """Send packets continuously until stopped"""
        if not self.connect():
            return
        
        try:
            packet_count = 0
            while True:
                packet = self.generate_packet()
                self.socket.send(json.dumps(packet).encode('utf-8'))
                packet_count += 1
                print(f"📤 [{packet_count}] {packet['protocol']} | {packet['packet_size']}B")
                
                # Receive acknowledgment
                response = self.socket.recv(1024).decode('utf-8')
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Client {self.client_id} stopped. Sent {packet_count} packets.")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.socket.close()
            print(f"✅ Client {self.client_id} disconnected")

if __name__ == "__main__":
    # Get client ID from command line or use default
    client_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    
    client = TrafficGenerator(client_id)
    
    print("\n🎯 Traffic Generator Menu:")
    print("1. Send fixed number of packets")
    print("2. Send continuous traffic")
    choice = input("Choose option (1 or 2): ")
    
    if choice == "1":
        num = int(input("Number of packets: "))
        delay = float(input("Delay between packets (seconds): "))
        client.send_traffic(num, delay)
    elif choice == "2":
        delay = float(input("Delay between packets (seconds): "))
        client.send_continuous(delay)
    else:
        print("Invalid choice!")