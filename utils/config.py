# utils/config.py
# Configuration file for NetSentinel

# Server Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 9999
MAX_CONNECTIONS = 5

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'netsentinel',
    'user': 'postgres',
    'password': 'my_password',
    'port': 5432
}

# ML Model Configuration
MODEL_PATH = 'ml/anomaly_detector.pkl'
CONTAMINATION = 0.1  # Expected proportion of anomalies

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

# Protocol Types
PROTOCOLS = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']