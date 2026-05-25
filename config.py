"""
Federated Learning Simulator - Configuration Module
Central place to configure dataset, model, and training parameters
This makes the project a true "Simulator" that can adapt to any dataset/model
"""

# ============================================================================
# SIMULATOR CONFIGURATION
# Change these values to switch datasets, models, or training parameters
# ============================================================================

# Dataset Configuration
# Options: "breast_cancer", "iris", "synthetic"
DATASET_TYPE = "iris"

# Model Configuration  
# Options: "simple_nn", "cnn", "logistic_regression"
MODEL_TYPE = "cnn"

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================

# Number of federated clients (hospitals/organizations)
NUM_CLIENTS = 3

# Number of training rounds
NUM_ROUNDS = 10

# Local training epochs per round
EPOCHS_PER_ROUND = 1

# Batch size for client training
BATCH_SIZE = 32

# Learning rate
LEARNING_RATE = 0.001

# Server address and port
SERVER_ADDRESS = "127.0.0.1:9000"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

# ============================================================================
# MODEL ARCHITECTURE CONFIGURATION
# ============================================================================

# For Breast Cancer dataset (30 features, 2 classes)
BREAST_CANCER_CONFIG = {
    "input_size": 30,
    "num_classes": 2,
    "dataset_name": "Breast Cancer Wisconsin (Diagnostic)",
    "num_samples": 569,
    "num_features": 30,
}

# For Iris dataset (4 features, 3 classes)
IRIS_CONFIG = {
    "input_size": 4,
    "num_classes": 3,
    "dataset_name": "Iris Classification",
    "num_samples": 150,
    "num_features": 4,
}

# For Synthetic dataset (10 features, 2 classes)
SYNTHETIC_CONFIG = {
    "input_size": 10,
    "num_classes": 2,
    "dataset_name": "Synthetic Binary Classification",
    "num_samples": 1000,
    "num_features": 10,
}

def get_dataset_config(dataset_type: str = None):
    """Get configuration for specified dataset"""
    dataset_type = dataset_type or DATASET_TYPE
    
    configs = {
        "breast_cancer": BREAST_CANCER_CONFIG,
        "iris": IRIS_CONFIG,
        "synthetic": SYNTHETIC_CONFIG,
    }
    
    if dataset_type not in configs:
        raise ValueError(f"Unknown dataset: {dataset_type}. Available: {list(configs.keys())}")
    
    return configs[dataset_type]

def get_model_config(model_type: str = None):
    """Get configuration for specified model"""
    model_type = model_type or MODEL_TYPE
    
    configs = {
        "simple_nn": {
            "name": "Simple Neural Network (3-Layer MLP)",
            "architecture": "128 -> 64 -> output",
            "description": "Standard fully-connected neural network",
        },
        "cnn": {
            "name": "Convolutional Neural Network",
            "architecture": "Conv -> Conv -> FC -> output",
            "description": "CNN for image/spatial data",
        },
        "logistic_regression": {
            "name": "Logistic Regression",
            "architecture": "Direct mapping to output",
            "description": "Simple linear classifier",
        },
    }
    
    if model_type not in configs:
        raise ValueError(f"Unknown model: {model_type}. Available: {list(configs.keys())}")
    
    return configs[model_type]

# Verify configuration on import
if __name__ == "__main__":
    print("✓ Configuration validated")
    print(f"Current Setup:")
    print(f"  Dataset: {DATASET_TYPE}")
    print(f"  Model: {MODEL_TYPE}")
    print(f"  Clients: {NUM_CLIENTS}")
    print(f"  Rounds: {NUM_ROUNDS}")
