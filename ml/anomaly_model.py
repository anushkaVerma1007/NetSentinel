# ml/anomaly_model.py
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pickle
import os
import sys
sys.path.append('..')
from utils.config import MODEL_PATH, CONTAMINATION, PROTOCOLS

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(PROTOCOLS)
        self.load_model()

    def load_model(self):
        """Load the trained model from disk"""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                print("✅ ML Model loaded successfully")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}. Training new model...")
                self.train_initial_model()
        else:
            print("⚠️ No model found. Training initial model...")
            self.train_initial_model()

    def train_initial_model(self):
        """Train initial model with synthetic data"""
        # Generate synthetic normal traffic
        np.random.seed(42)
        normal_sizes = np.random.normal(1000, 300, 900)
        normal_protocols = np.random.choice(range(len(PROTOCOLS)), 900)
        
        # Generate synthetic anomalies
        anomaly_sizes = np.concatenate([
            np.random.normal(5000, 1000, 50),  # Large packets
            np.random.normal(50, 20, 50)        # Very small packets
        ])
        anomaly_protocols = np.random.choice(range(len(PROTOCOLS)), 100)
        
        # Combine data
        X = np.column_stack([
            np.concatenate([normal_sizes, anomaly_sizes]),
            np.concatenate([normal_protocols, anomaly_protocols])
        ])
        
        # Train model
        self.model = IsolationForest(contamination=CONTAMINATION, random_state=42)
        self.model.fit(X)
        self.save_model()
        print("✅ Initial model trained and saved")

    def train_from_database(self, db):
        """Retrain model using database data"""
        try:
            data = db.get_training_data()
            if len(data) < 50:
                print("⚠️ Not enough data for training. Need at least 50 samples.")
                return False
            
            # Prepare features
            X = []
            for packet_size, protocol in data:
                protocol_encoded = self.label_encoder.transform([protocol])[0]
                X.append([packet_size, protocol_encoded])
            
            X = np.array(X)
            
            # Train new model
            self.model = IsolationForest(contamination=CONTAMINATION, random_state=42)
            self.model.fit(X)
            self.save_model()
            print(f"✅ Model retrained with {len(data)} samples")
            return True
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False

    def predict(self, packet_size, protocol):
        """Predict if a packet is anomalous"""
        try:
            protocol_encoded = self.label_encoder.transform([protocol])[0]
            X = np.array([[packet_size, protocol_encoded]])
            prediction = self.model.predict(X)
            # Isolation Forest returns -1 for anomalies, 1 for normal
            return prediction[0] == -1
        except Exception as e:
            print(f"❌ Error in prediction: {e}")
            return False

    def save_model(self):
        """Save the trained model to disk"""
        try:
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            print("✅ Model saved successfully")
        except Exception as e:
            print(f"❌ Error saving model: {e}")