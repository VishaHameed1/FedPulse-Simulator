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
import json

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


def save_training_metrics(round_num, accuracy):
    """Save training metrics to file for dashboard"""
    metrics_file = "training_metrics.json"
    
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    else:
        data = {'rounds': [], 'accuracies': []}
    
    data['rounds'].append(round_num)
    data['accuracies'].append(accuracy)
    
    with open(metrics_file, 'w') as f:
        json.dump(data, f)
    
    print(f"📊 Metrics saved: Round {round_num}, Accuracy: {accuracy:.2f}%")


class CustomFedAvg(FedAvg):
    """Custom FedAvg that saves accuracy metrics from evaluation"""
    
    def aggregate_fit(self, rnd, results, failures):
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(rnd, results, failures)
        return aggregated_parameters, aggregated_metrics
    
    def aggregate_evaluate(self, rnd, results, failures):
        """This receives evaluation results from clients"""
        accuracies = []
        for _, res in results:
            if hasattr(res, 'metrics') and res.metrics and 'accuracy' in res.metrics:
                accuracies.append(res.metrics['accuracy'])
        
        if accuracies:
            avg_accuracy = sum(accuracies) / len(accuracies)
            print(f"\n{'='*50}")
            print(f"🎯 Round {rnd} - Global Accuracy: {avg_accuracy:.2f}%")
            print(f"{'='*50}")
            save_training_metrics(rnd, avg_accuracy)
        
        return super().aggregate_evaluate(rnd, results, failures)


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
        self.round_accuracies = []
    
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
        
        if os.path.exists("training_metrics.json"):
            os.remove("training_metrics.json")
            print("🔄 Cleared previous training metrics\n")
        
        self._print_server_config()
        
        strategy = CustomFedAvg(
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            min_fit_clients=self.num_clients,
            min_evaluate_clients=self.num_clients,
            min_available_clients=self.num_clients,
        )
        
        print(f"{'='*70}")
        print(f"🚀 STARTING FEDERATED LEARNING SERVER")
        print(f"{'='*70}")
        print(f"Server Address: {SERVER_HOST}:{SERVER_PORT}")
        print(f"Waiting for {self.num_clients} clients to connect...")
        print(f"\n⏳ Once all clients connect, training will begin automatically.")
        print(f"   Each client trains locally → sends weights → server aggregates")
        print(f"\n📁 Metrics will be saved to: training_metrics.json\n")
        
        fl.server.start_server(
            server_address=f"{SERVER_HOST}:{SERVER_PORT}",
            strategy=strategy,
            config=fl.server.ServerConfig(num_rounds=self.num_rounds),
        )


def start_server(num_clients: int = None, num_rounds: int = None):
    num_clients = num_clients or NUM_CLIENTS
    num_rounds = num_rounds or NUM_ROUNDS
    
    server = FederatedLearningServer(num_clients=num_clients, num_rounds=num_rounds)
    server.start()


if __name__ == "__main__":
    start_server()