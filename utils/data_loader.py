"""
Federated Learning Simulator - Data Loading Module
Supports multiple datasets for simulator flexibility
This demonstrates that the simulator can work with ANY dataset
"""

import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.datasets import load_breast_cancer, load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATASET_TYPE, get_dataset_config


# ============================================================================
# DATASET 1: Breast Cancer Wisconsin (Healthcare Dataset)
# ============================================================================

def load_breast_cancer_data():
    """Load breast cancer dataset - 569 samples, 30 features"""
    data = load_breast_cancer()
    return data.data, data.target, {
        "name": "Breast Cancer Wisconsin (Diagnostic)",
        "samples": len(data.data),
        "features": data.data.shape[1],
        "classes": 2,
        "class_names": list(data.target_names)
    }


# ============================================================================
# DATASET 2: Iris (Classic ML Dataset)
# ============================================================================

def load_iris_data():
    """Load iris dataset - 150 samples, 4 features"""
    data = load_iris()
    return data.data, data.target, {
        "name": "Iris Classification",
        "samples": len(data.data),
        "features": data.data.shape[1],
        "classes": 3,
        "class_names": list(data.target_names)
    }


# ============================================================================
# DATASET 3: Synthetic Data (for testing/demo)
# ============================================================================

def load_synthetic_data():
    """Generate synthetic dataset - 1000 samples, 10 features"""
    from sklearn.datasets import make_classification
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )
    return X, y, {
        "name": "Synthetic Binary Classification",
        "samples": 1000,
        "features": 10,
        "classes": 2,
        "class_names": ["Class 0", "Class 1"]
    }

def load_from_csv(file_path_or_df):
    """
    Load data from a CSV file or DataFrame
    Assumes the last column is the target/label
    """
    import pandas as pd
    if isinstance(file_path_or_df, str):
        df = pd.read_csv(file_path_or_df)
    else:
        df = file_path_or_df
        
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    
    # Dynamic metadata
    metadata = {
        "name": "Custom Uploaded Dataset",
        "samples": len(df),
        "features": X.shape[1],
        "classes": len(np.unique(y)),
        "class_names": [str(c) for c in np.unique(y)]
    }
    return X, y, metadata


# ============================================================================
# MAIN LOADER FUNCTION - The Key to Simulator Flexibility
# ============================================================================

def load_dataset(dataset_type: str = None, client_id: int = None, num_clients: int = 3):
    """
    Load and split any dataset for federated learning
    
    Args:
        dataset_type: "breast_cancer", "iris", or "synthetic"
        client_id: ID of client (0, 1, 2...). If None, returns full dataset
        num_clients: Total number of clients
    
    Returns:
        train_loader, test_loader: DataLoaders for training and testing
    
    Example:
        # Switch to different dataset:
        train_loader, test_loader = load_dataset("iris")
        train_loader, test_loader = load_dataset("synthetic")
    """
    
    dataset_type = dataset_type or DATASET_TYPE
    
    # Load appropriate dataset
    loaders = {
        "breast_cancer": load_breast_cancer_data,
        "iris": load_iris_data,
        "synthetic": load_synthetic_data,
        "custom": lambda: load_from_csv("data/custom_dataset.csv") if os.path.exists("data/custom_dataset.csv") else load_synthetic_data()
    }
    
    if dataset_type not in loaders:
        raise ValueError(f"Unknown dataset: {dataset_type}. Available: {list(loaders.keys())}")
    
    X, y, metadata = loaders[dataset_type]()
    
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
    
    return train_loader, test_loader, metadata


# Keep backward compatibility
def load_breast_cancer_dataset(client_id=None, num_clients=3):
    """Backward compatible function for breast cancer dataset"""
    train_loader, test_loader, _ = load_dataset("breast_cancer", client_id, num_clients)
    return train_loader, test_loader


def get_dataset_info(dataset_type: str = None):
    """Get info about dataset"""
    dataset_type = dataset_type or DATASET_TYPE
    
    loaders = {
        "breast_cancer": load_breast_cancer_data,
        "iris": load_iris_data,
        "synthetic": load_synthetic_data,
    }
    
    if dataset_type not in loaders:
        raise ValueError(f"Unknown dataset: {dataset_type}")
    
    _, _, metadata = loaders[dataset_type]()
    return metadata
