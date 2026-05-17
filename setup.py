#!/usr/bin/env python
"""
Setup script to create project structure for Federated Learning
"""

import os
import sys

# Define the directory structure
DIRECTORIES = [
    'model',
    'utils',
    'server',
    'clients',
    'dashboard'
]

FILES = {
    'model/__init__.py': '',
    'model/model.py': '''import torch
import torch.nn as nn

class SimpleNN(nn.Module):
    """Simple Neural Network for classification tasks"""
    
    def __init__(self, input_size=30, num_classes=2):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

def get_model(input_size=30, num_classes=2):
    """Factory function to create model"""
    return SimpleNN(input_size, num_classes)
''',
    'utils/__init__.py': '',
    'utils/data_loader.py': '''import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np

def load_breast_cancer_dataset(client_id=None, num_clients=3):
    """
    Load and split breast cancer dataset for federated learning
    
    Args:
        client_id: ID of client (0, 1, 2...). If None, returns full dataset
        num_clients: Total number of clients
    
    Returns:
        train_loader, test_loader: DataLoaders for training and testing
    """
    # Load dataset
    data = load_breast_cancer()
    X = data.data
    y = data.target
    
    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # If client_id specified, split training data among clients
    if client_id is not None:
        samples_per_client = len(X_train) // num_clients
        start_idx = client_id * samples_per_client
        end_idx = start_idx + samples_per_client if client_id < num_clients - 1 else len(X_train)
        
        X_train = X_train[start_idx:end_idx]
        y_train = y_train[start_idx:end_idx]
    
    # Convert to tensors
    X_train = torch.FloatTensor(X_train)
    y_train = torch.LongTensor(y_train)
    X_test = torch.FloatTensor(X_test)
    y_test = torch.LongTensor(y_test)
    
    # Create datasets
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    
    # Create loaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    return train_loader, test_loader

def get_dataset_info():
    """Get info about dataset"""
    data = load_breast_cancer()
    return {
        "num_samples": len(data.data),
        "num_features": data.data.shape[1],
        "num_classes": len(np.unique(data.target)),
        "class_names": data.target_names.tolist()
    }
''',
    'utils/training.py': '''import torch
import torch.nn as nn
from typing import Tuple

def train_epoch(model, train_loader, optimizer, epochs=1):
    """
    Train model for one or more epochs
    
    Args:
        model: Neural network model
        train_loader: DataLoader for training data
        optimizer: Optimizer (SGD, Adam, etc)
        epochs: Number of epochs to train
    
    Returns:
        Average loss over all epochs
    """
    model.train()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0
    batch_count = 0
    
    for epoch in range(epochs):
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            batch_count += 1
    
    return total_loss / batch_count

def evaluate(model, test_loader) -> Tuple[float, float]:
    """
    Evaluate model on test data
    
    Args:
        model: Neural network model
        test_loader: DataLoader for test data
    
    Returns:
        (accuracy, loss)
    """
    model.eval()
    criterion = nn.CrossEntropyLoss()
    correct = 0
    total = 0
    total_loss = 0
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    avg_loss = total_loss / len(test_loader)
    
    return accuracy, avg_loss
''',
    'server/__init__.py': '',
    'server/server.py': '''"""
Federated Learning Server using Flower Framework
Aggregates model weights from multiple clients
"""

import flwr as fl
from flwr.server.strategy import FedAvg
from typing import List, Tuple
import torch
import sys
sys.path.append('..')

from model.model import get_model
from utils.data_loader import load_breast_cancer_dataset
from utils.training import evaluate

def get_eval_fn(model):
    """Returns an evaluation function for the server"""
    
    def evaluate_fn(server_round, parameters, config):
        # Load test data
        _, test_loader = load_breast_cancer_dataset()
        
        # Update model with aggregated parameters
        params_dict = zip(model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        model.load_state_dict(state_dict, strict=False)
        
        # Evaluate
        accuracy, loss = evaluate(model, test_loader)
        
        print(f"\\n[Server] Round {server_round} - Test Accuracy: {accuracy:.2f}%, Loss: {loss:.4f}")
        
        return loss, {"accuracy": accuracy}
    
    return evaluate_fn

def start_server(num_clients: int = 3, num_rounds: int = 5):
    """
    Start the Federated Learning server
    
    Args:
        num_clients: Number of clients to wait for
        num_rounds: Number of training rounds
    """
    
    # Initialize model
    model = get_model()
    
    # Define strategy
    strategy = FedAvg(
        fraction_fit=1.0,  # Use all available clients
        fraction_evaluate=1.0,  # Evaluate all clients
        min_fit_clients=num_clients,  # Wait for all clients
        min_evaluate_clients=num_clients,
        min_available_clients=num_clients,
        eval_fn=get_eval_fn(model),
    )
    
    # Start server
    print(f"\\n{'='*60}")
    print(f"Starting Federated Learning Server")
    print(f"Waiting for {num_clients} clients...")
    print(f"Number of rounds: {num_rounds}")
    print(f"{'='*60}\\n")
    
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        strategy=strategy,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
    )

if __name__ == "__main__":
    start_server(num_clients=3, num_rounds=5)
''',
    'clients/__init__.py': '',
    'clients/client.py': '''"""
Federated Learning Client using Flower Framework
Trains model locally and sends weights to server
"""

import flwr as fl
import torch
import torch.nn as nn
import sys
sys.path.append('..')

from model.model import get_model
from utils.data_loader import load_breast_cancer_dataset
from utils.training import train_epoch, evaluate

class FlowerClient(fl.client.NumPyClient):
    """Federated Learning Client"""
    
    def __init__(self, client_id: int, num_clients: int = 3):
        self.client_id = client_id
        self.model = get_model()
        self.train_loader, self.test_loader = load_breast_cancer_dataset(
            client_id=client_id, 
            num_clients=num_clients
        )
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
    
    def get_parameters(self, config):
        """Get model parameters as numpy arrays"""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]
    
    def set_parameters(self, parameters):
        """Update model with parameters from server"""
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=False)
    
    def fit(self, parameters, config):
        """Train model locally"""
        self.set_parameters(parameters)
        
        # Local training
        loss = train_epoch(self.model, self.train_loader, self.optimizer, epochs=1)
        
        print(f"[Client {self.client_id}] Trained - Loss: {loss:.4f}")
        
        return self.get_parameters(config), len(self.train_loader.dataset), {}
    
    def evaluate(self, parameters, config):
        """Evaluate model on local test data"""
        self.set_parameters(parameters)
        
        accuracy, loss = evaluate(self.model, self.test_loader)
        
        print(f"[Client {self.client_id}] Evaluated - Accuracy: {accuracy:.2f}%, Loss: {loss:.4f}")
        
        return loss, len(self.test_loader.dataset), {"accuracy": accuracy}

def start_client(client_id: int, server_address: str = "127.0.0.1:8080"):
    """Start Federated Learning Client"""
    
    client = FlowerClient(client_id=client_id)
    
    print(f"\\n[Client {client_id}] Connecting to server at {server_address}...")
    
    fl.client.start_client(
        server_address=server_address,
        client=client.to_client(),
    )

if __name__ == "__main__":
    import sys
    
    # Get client ID from command line (default to 0)
    client_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    
    print(f"Starting Client {client_id}...")
    start_client(client_id)
''',
    'dashboard/__init__.py': '',
}

def setup_project():
    """Create project structure"""
    
    # Create directories
    for directory in DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create files
    for filepath, content in FILES.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created file: {filepath}")
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. pip install -r requirements.txt")
    print("2. python server/server.py  (Terminal 1)")
    print("3. python clients/client.py 0  (Terminal 2)")
    print("4. python clients/client.py 1  (Terminal 3)")
    print("5. python clients/client.py 2  (Terminal 4)")
    print("\nOptional:")
    print("streamlit run dashboard/app.py  (Open http://localhost:8501)")

if __name__ == "__main__":
    setup_project()
