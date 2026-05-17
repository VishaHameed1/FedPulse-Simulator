"""
Federated Learning Client using Flower Framework
Trains model locally and sends WEIGHTS ONLY to server (never raw data!)
This is a key feature of federated learning: Data Privacy
"""

import flwr as fl
import logging
import torch
import torch.nn as nn
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FlowerDeprecationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "DEPRECATED FEATURE" not in record.getMessage()

logging.getLogger("flwr").addFilter(FlowerDeprecationFilter())

from model.model import get_model
from utils.data_loader import load_dataset, get_dataset_info
from utils.training import train_epoch, evaluate
from config import (
    DATASET_TYPE, MODEL_TYPE, NUM_CLIENTS, 
    LEARNING_RATE, SERVER_ADDRESS, get_dataset_config, get_model_config
)

class FlowerClient(fl.client.NumPyClient):
    """
    Federated Learning Client
    
    IMPORTANT: This client only sends MODEL WEIGHTS to the server, never raw data!
    All training happens locally on each client's private data.
    """
    
    def __init__(self, client_id: int, num_clients: int = 3):
        self.client_id = client_id
        self.dataset_type = DATASET_TYPE
        self.model_type = MODEL_TYPE
        
        # Get dataset configuration
        dataset_config = get_dataset_config(self.dataset_type)
        input_size = dataset_config["input_size"]
        num_classes = dataset_config["num_classes"]
        
        # Initialize model (can be any architecture from model.py)
        self.model = get_model(
            model_type=self.model_type,
            input_size=input_size,
            num_classes=num_classes
        )
        
        # Load ONLY LOCAL DATA for this client
        # ⚠️ CRITICAL: Raw data is stored ONLY here on the client, NOT on server
        self.train_loader, self.test_loader, self.dataset_info = load_dataset(
            dataset_type=self.dataset_type,
            client_id=client_id, 
            num_clients=num_clients
        )
        
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=LEARNING_RATE)
        
        # Print client startup info
        self._print_startup_info()
    
    def _print_startup_info(self):
        """Print client configuration on startup"""
        print(f"\n{'='*60}")
        print(f"[Client {self.client_id}] Initialized")
        print(f"{'='*60}")
        print(f"Dataset: {self.dataset_info['name']}")
        print(f"Model: {self.model_type.upper()}")
        print(f"Local Data Samples: {len(self.train_loader.dataset)}")
        print(f"⚠️  DATA LOCATION: LOCAL (Private on Client)")
        print(f"✓ Server has: ZERO raw data")
        print(f"{'='*60}\n")
    
    def get_parameters(self, config):
        """
        Get model parameters (WEIGHTS ONLY)
        These are the only things sent to server - never raw data!
        """
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]
    
    def set_parameters(self, parameters):
        """Update model with parameters from server (global weights)"""
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=False)
    
    def fit(self, parameters, config):
        """
        Train model locally with private data
        
        Process:
        1. Receive global weights from server
        2. Train on LOCAL data only
        3. Send updated weights back (NOT data)
        """
        self.set_parameters(parameters)
        
        # Local training on private data
        loss = train_epoch(self.model, self.train_loader, self.optimizer, epochs=1)
        
        print(f"[Client {self.client_id}] ✓ Training Complete - Loss: {loss:.4f}")
        print(f"  → Sending weights (size: {sum(p.numel() for p in self.model.parameters())} params)")
        print(f"  → Keeping raw data local (size: {len(self.train_loader.dataset)} samples)")
        
        return self.get_parameters(config), len(self.train_loader.dataset), {}
    
    def evaluate(self, parameters, config):
        """
        Evaluate model on local test data
        Server never sees this evaluation data either!
        """
        self.set_parameters(parameters)
        
        accuracy, loss = evaluate(self.model, self.test_loader)
        
        print(f"[Client {self.client_id}] ✓ Evaluation Complete")
        print(f"  → Local Accuracy: {accuracy:.2f}%, Loss: {loss:.4f}")
        
        return loss, len(self.test_loader.dataset), {"accuracy": accuracy}


def start_client(client_id: int, server_address: str = None):
    """
    Start Federated Learning Client
    
    The client:
    - Keeps all raw data private and local
    - Only sends model weights to server
    - Trains the model locally on private data
    """
    
    server_address = server_address or SERVER_ADDRESS
    
    client = FlowerClient(client_id=client_id)
    
    print(f"[Client {client_id}] 🔗 Connecting to server at {server_address}...")
    print(f"[Client {client_id}] ⏳ Waiting for training instructions...\n")
    
    fl.client.start_client(
        server_address=server_address,
        client=client.to_client(),
    )


if __name__ == "__main__":
    import sys
    
    # Get client ID from command line (default to 0)
    client_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    
    print(f"{'='*60}")
    print(f"Starting Federated Learning Client {client_id}")
    print(f"{'='*60}")
    
    start_client(client_id)
