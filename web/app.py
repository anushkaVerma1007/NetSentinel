# web/app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
import os
sys.path.append('..')
from database.db import Database
from ml.anomaly_model import AnomalyDetector
from utils.config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

db = Database()
ml_model = AnomalyDetector()

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/packets', methods=['GET'])
def get_packets():
    """Get all packets"""
    try:
        limit = request.args.get('limit', 100, type=int)
        packets = db.get_all_packets(limit)
        
        # Convert to JSON format
        packet_list = []
        for p in packets:
            packet_list.append({
                'id': p[0],
                'source_ip': p[1],
                'dest_ip': p[2],
                'packet_size': p[3],
                'protocol': p[4],
                'timestamp': p[5].isoformat() if p[5] else None,
                'anomaly_flag': p[6]
            })
        
        return jsonify({'success': True, 'packets': packet_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get packet statistics"""
    try:
        stats = db.get_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    """Retrain the ML model"""
    try:
        success = ml_model.train_from_database(db)
        if success:
            return jsonify({'success': True, 'message': 'Model retrained successfully'})
        else:
            return jsonify({'success': False, 'error': 'Not enough data to retrain'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/filter', methods=['GET'])
def filter_packets():
    """Filter packets by protocol"""
    try:
        protocol = request.args.get('protocol', None)
        anomaly_only = request.args.get('anomaly_only', 'false').lower() == 'true'
        
        # This is a simplified version - you can extend the database class
        # to support more complex queries
        packets = db.get_all_packets(1000)
        
        # Filter in Python (for simplicity)
        filtered = []
        for p in packets:
            packet_dict = {
                'id': p[0],
                'source_ip': p[1],
                'dest_ip': p[2],
                'packet_size': p[3],
                'protocol': p[4],
                'timestamp': p[5].isoformat() if p[5] else None,
                'anomaly_flag': p[6]
            }
            
            if protocol and p[4] != protocol:
                continue
            if anomaly_only and not p[6]:
                continue
            
            filtered.append(packet_dict)
        
        return jsonify({'success': True, 'packets': filtered})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'NetSentinel API'})

if __name__ == '__main__':
    print("🌐 Starting Flask API server...")
    print(f"📡 API available at http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"📊 Dashboard at http://{FLASK_HOST}:{FLASK_PORT}/")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)