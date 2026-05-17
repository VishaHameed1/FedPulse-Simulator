"""
Federated Learning Server using Flower Framework
Aggregates model weights from multiple clients using FedAvg algorithm
IMPORTANT: Server receives ONLY WEIGHTS, never sees raw client data!
"""

import flwr as fl
import logging
from flwr.server.strategy import FedAvg
from typing import List, Tuple
import torch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FlowerDeprecationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "DEPRECATED FEATURE" not in record.getMessage()

logging.getLogger("flwr").addFilter(FlowerDeprecationFilter())

from model.model import get_model
from utils.data_loader import load_dataset, get_dataset_info
from utils.training import evaluate
from config import (
    NUM_CLIENTS, NUM_ROUNDS, DATASET_TYPE, MODEL_TYPE,
    SERVER_ADDRESS, SERVER_HOST, SERVER_PORT,
    get_dataset_config, get_model_config
)


class FederatedLearningServer:
    """
    Federated Learning Server - Aggregates weights from clients
    
    Key Privacy Feature:
    - Server ONLY receives model weights
    - Server NEVER receives raw data
    - Server performs FedAvg (Federated Averaging) algorithm
    """
    
    def __init__(self, num_clients: int = 3, num_rounds: int = 5):
        self.num_clients = num_clients
        self.num_rounds = num_rounds
        self.dataset_type = DATASET_TYPE
        self.model_type = MODEL_TYPE
        
        # Print server configuration
        self._print_server_config()
    
    def _print_server_config(self):
        """Print server configuration on startup"""
        dataset_config = get_dataset_config(self.dataset_type)
        model_config = get_model_config(self.model_type)
        
        print(f"\n{'='*70}")
        print(f"FEDERATED LEARNING SERVER - SIMULATOR CONFIGURATION")
        print(f"{'='*70}")
        print(f"\n📊 Dataset Configuration:")
        print(f"   Name: {dataset_config['dataset_name']}")
        print(f"   Total Samples: {dataset_config['num_samples']}")
        print(f"   Features: {dataset_config['num_features']}")
        print(f"   Classes: {dataset_config['num_classes']}")
        
        print(f"\n🧠 Model Configuration:")
        print(f"   Type: {model_config['name']}")
        print(f"   Architecture: {model_config['architecture']}")
        
        print(f"\n⚙️  Training Configuration:")
        print(f"   Clients: {self.num_clients}")
        print(f"   Rounds: {self.num_rounds}")
        
        print(f"\n🔒 Privacy & Security:")
        print(f"   Server Data Size: 0 BYTES (only model weights)")
        print(f"   Client Data: Stored ONLY locally on each client")
        print(f"   Communication: Weights only (no raw data)")
        print(f"   Algorithm: FedAvg (Federated Averaging)")
        
        print(f"\n{'='*70}\n")
    
    def start(self):
        """Start the Federated Learning server"""
        
        # Define strategy - FedAvg is the standard for federated learning
        strategy = FedAvg(
            fraction_fit=1.0,  # Use all available clients
            fraction_evaluate=0.0,  # No server-side evaluation
            min_fit_clients=self.num_clients,  # Wait for all clients
            min_available_clients=self.num_clients,
        )
        
        print(f"{'='*70}")
        print(f"🚀 STARTING FEDERATED LEARNING SERVER")
        print(f"{'='*70}")
        print(f"Waiting for {self.num_clients} clients to connect...")
        print(f"Server Address: {SERVER_HOST}:{SERVER_PORT}")
        print(f"\n⏳ Once all clients connect, training will begin automatically.")
        print(f"   Each client trains locally → sends weights → server aggregates\n")
        
        # Start server
        fl.server.start_server(
            server_address=f"{SERVER_HOST}:{SERVER_PORT}",
            strategy=strategy,
            config=fl.server.ServerConfig(num_rounds=self.num_rounds),
        )


def start_server(num_clients: int = None, num_rounds: int = None):
    """
    Start the Federated Learning server
    
    Args:
        num_clients: Number of clients to wait for (default from config)
        num_rounds: Number of training rounds (default from config)
    """
    
    num_clients = num_clients or NUM_CLIENTS
    num_rounds = num_rounds or NUM_ROUNDS
    
    server = FederatedLearningServer(num_clients=num_clients, num_rounds=num_rounds)
    server.start()


if __name__ == "__main__":
    start_server()
