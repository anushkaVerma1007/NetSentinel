# 🛡️ NetSentinel - Network Anomaly Detection System

A comprehensive network traffic monitoring and anomaly detection system built with multi-threaded socket programming, machine learning, and real-time web visualization.

## Features

- **Multi-threaded Socket Server**: Handles multiple concurrent client connections
- **ML-based Anomaly Detection**: Uses Isolation Forest algorithm to detect suspicious traffic
- **PostgreSQL Database**: Stores all network packets with full history
- **Real-time Web Dashboard**: Monitor traffic and anomalies in real-time
- **Traffic Generator Client**: Simulate network traffic for testing
- **FCFS Scheduling**: First-Come-First-Served packet processing

## Architecture

```
┌─────────────┐
│   Clients   │ (Generate traffic)
└──────┬──────┘
       │ TCP Socket
       ▼
┌─────────────┐
│   Server    │ (Multi-threaded)
└──────┬──────┘
       │
       ├──► ML Model (Isolation Forest)
       │
       └──► PostgreSQL Database
              │
              ▼
       ┌─────────────┐
       │  Flask API  │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │  Dashboard  │ (HTML/JS)
       └─────────────┘
```

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd NetSentinel
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL Database

```sql
-- Create database
CREATE DATABASE netsentinel;

-- Connect to database
\c netsentinel

-- The table will be created automatically by the application
```

### 4. Configure Settings

Edit `utils/config.py` and update your database credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'netsentinel',
    'user': 'your_username',
    'password': 'your_password',
    'port': 5432
}
```

## Usage

### Step 1: Start the Server

```bash
cd server
python server.py
```

You should see:
```
 NetSentinel Server started on localhost:9999
 Listening for connections...
```

### Step 2: Start the Web Dashboard

Open a new terminal:

```bash
cd web
python app.py
```

Access the dashboard at: **http://localhost:5000**

### Step 3: Run Traffic Generator Clients

Open another terminal:

```bash
cd client
python client.py 1
```

Follow the prompts:
- Option 1: Send a fixed number of packets
- Option 2: Send continuous traffic

You can run multiple clients simultaneously:

```bash
# Terminal 1
python client.py client1

# Terminal 2
python client.py client2

# Terminal 3
python client.py client3
```

##  Dashboard Features

- **Real-time Statistics**: Total packets, anomalies detected, anomaly rate
- **Interactive Chart**: Visualize traffic by protocol
- **Packet Table**: View detailed packet information
- **Filters**: Filter by protocol or show only anomalies
- **Auto-refresh**: Enable automatic data updates
- **Model Retraining**: Retrain ML model with new data

##  How It Works

### 1. Traffic Generation
Clients generate random network packets with:
- Random source/destination IPs
- Packet sizes (64-1500 bytes)
- Various protocols (TCP, UDP, ICMP, HTTP, HTTPS)
- 10% chance of generating anomalous packets

### 2. Server Processing
- Accepts client connections using multi-threading
- Each client handled by a separate thread
- Implements FCFS scheduling for packet processing
- Passes packets through ML model for classification

### 3. Anomaly Detection
- Uses Scikit-learn's Isolation Forest algorithm
- Trained on normal traffic patterns
- Detects anomalies based on packet size and protocol
- Marks suspicious packets in the database

### 4. Data Storage
- All packets stored in PostgreSQL
- Includes timestamp, IPs, size, protocol, and anomaly flag
- Historical data used for model retraining

### 5. Web Visualization
- Flask API serves packet data and statistics
- Real-time dashboard with interactive charts
- Filter and search capabilities

##  Testing

### Generate Normal Traffic
```bash
python client.py
# Choose option 2 for continuous traffic
# Set delay to 1 second
```

### Generate Burst Traffic
```bash
# Run 3-4 clients simultaneously
# This tests multi-threading capabilities
```

### Test Anomaly Detection
The client automatically generates anomalous packets (very large or very small). Watch the dashboard for red "ANOMALY" badges.

##  Performance

- Handles up to 5 concurrent connections (configurable)
- Processes ~10-20 packets per second per client
- ML inference: <10ms per packet
- Database insertion: <5ms per packet

##  Customization

### Change Server Port
Edit `utils/config.py`:
```python
SERVER_PORT = 8888  # Your custom port
```

### Adjust ML Sensitivity
Edit `utils/config.py`:
```python
CONTAMINATION = 0.15  # Higher = more anomalies detected
```

### Add New Protocols
Edit `utils/config.py`:
```python
PROTOCOLS = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'FTP', 'SSH']
```

##  Database Schema

```sql
CREATE TABLE packets (
    id SERIAL PRIMARY KEY,
    source_ip VARCHAR(15) NOT NULL,
    dest_ip VARCHAR(15) NOT NULL,
    packet_size INTEGER NOT NULL,
    protocol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    anomaly_flag BOOLEAN DEFAULT FALSE
);
```

##  Troubleshooting

### "Connection Refused" Error
- Ensure server is running on the correct port
- Check firewall settings
- Verify SERVER_HOST and SERVER_PORT in config.py

### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials in config.py
- Ensure database 'netsentinel' exists

### Model Training Error
- Ensure at least 50 packets in database
- Check sklearn installation
- Verify ml/ directory has write permissions

##  Learning Outcomes

This project demonstrates:
- **Networking**: Socket programming, client-server architecture
- **OS Concepts**: Multi-threading, concurrent processing, FCFS scheduling
- **DBMS**: PostgreSQL, CRUD operations, query optimization
- **AI/ML**: Isolation Forest, anomaly detection, model retraining
- **Web Development**: Flask API, REST endpoints, real-time visualization

##  Technologies Used

- **Python 3.8+**: Core programming language
- **Socket Programming**: Network communication
- **Threading**: Concurrent client handling
- **PostgreSQL**: Relational database
- **Scikit-learn**: Machine learning library
- **Flask**: Web framework
- **Chart.js**: Data visualization
- **HTML/CSS/JavaScript**: Frontend


##  Author

Built as a comprehensive project demonstrating networking, OS concepts, database management, and machine learning.

---

**Happy Monitoring! 🛡️**