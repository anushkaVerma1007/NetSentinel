# database/db.py
import psycopg2
from psycopg2 import pool
from datetime import datetime
import sys
sys.path.append('..')
from utils.config import DB_CONFIG

class Database:
    def __init__(self):
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **DB_CONFIG)
            if self.connection_pool:
                print("✅ Database connection pool created successfully")
                self.create_table()
        except Exception as e:
            print(f"❌ Error creating connection pool: {e}")
            self.connection_pool = None

    def create_table(self):
        """Create packets table if it doesn't exist"""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS packets (
                    id SERIAL PRIMARY KEY,
                    source_ip VARCHAR(15) NOT NULL,
                    dest_ip VARCHAR(15) NOT NULL,
                    packet_size INTEGER NOT NULL,
                    protocol VARCHAR(10) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    anomaly_flag BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
            cursor.close()
            self.connection_pool.putconn(conn)
            print("✅ Table 'packets' ready")
        except Exception as e:
            print(f"❌ Error creating table: {e}")

    def insert_packet(self, source_ip, dest_ip, packet_size, protocol, anomaly_flag):
        """Insert a packet into the database"""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO packets (source_ip, dest_ip, packet_size, protocol, anomaly_flag)
                VALUES (%s, %s, %s, %s, %s)
            """, (source_ip, dest_ip, packet_size, protocol, anomaly_flag))
            
            conn.commit()
            cursor.close()
            self.connection_pool.putconn(conn)
            return True
        except Exception as e:
            print(f"❌ Error inserting packet: {e}")
            return False

    def get_all_packets(self, limit=100):
        """Retrieve all packets from database"""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, source_ip, dest_ip, packet_size, protocol, timestamp, anomaly_flag
                FROM packets
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            
            packets = cursor.fetchall()
            cursor.close()
            self.connection_pool.putconn(conn)
            return packets
        except Exception as e:
            print(f"❌ Error fetching packets: {e}")
            return []

    def get_training_data(self):
        """Get data for ML training"""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT packet_size, protocol
                FROM packets
            """)
            
            data = cursor.fetchall()
            cursor.close()
            self.connection_pool.putconn(conn)
            return data
        except Exception as e:
            print(f"❌ Error fetching training data: {e}")
            return []

    def get_stats(self):
        """Get statistics about packets"""
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM packets")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM packets WHERE anomaly_flag = TRUE")
            anomalies = cursor.fetchone()[0]
            
            cursor.close()
            self.connection_pool.putconn(conn)
            return {'total': total, 'anomalies': anomalies}
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")
            return {'total': 0, 'anomalies': 0}

    def close(self):
        """Close all database connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Database connections closed")