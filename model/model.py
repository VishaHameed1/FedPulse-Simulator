"""
Federated Learning Simulator - Model Architecture Module
Supports multiple model types for flexibility
This demonstrates that the simulator can work with ANY model architecture
"""

import torch
import torch.nn as nn

# ============================================================================
# MODEL 1: Simple Neural Network (3-Layer MLP)
# ============================================================================

class SimpleNN(nn.Module):
    """
    Simple Neural Network for classification tasks
    Default model: 3-layer fully-connected network with dropout
    """
    
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


# ============================================================================
# MODEL 2: Convolutional Neural Network
# ============================================================================

class SimpleCNN(nn.Module):
    """
    Convolutional Neural Network for image classification
    Useful for image datasets - demonstrates model flexibility
    """
    
    def __init__(self, input_size=30, num_classes=2):
        super(SimpleCNN, self).__init__()
        # For tabular data, we reshape to 1D conv
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        
        # Calculate size after convolutions
        size_after_conv = input_size // 4  # Two maxpools
        
        self.fc1 = nn.Linear(64 * size_after_conv, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        # Reshape for conv layers: (batch, features) -> (batch, 1, features)
        x = x.unsqueeze(1)
        
        x = self.relu(self.conv1(x))
        x = self.pool(x)
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


# ============================================================================
# MODEL 3: Logistic Regression
# ============================================================================

class LogisticRegressionModel(nn.Module):
    """
    Simple Logistic Regression classifier
    Demonstrates that even simple models work with federated learning
    """
    
    def __init__(self, input_size=30, num_classes=2):
        super(LogisticRegressionModel, self).__init__()
        self.linear = nn.Linear(input_size, num_classes)
    
    def forward(self, x):
        return self.linear(x)


# ============================================================================
# FACTORY FUNCTION - The Key to Simulator Flexibility
# ============================================================================

def get_model(model_type: str = "simple_nn", input_size: int = 30, num_classes: int = 2):
    """
    Factory function to create any model
    
    Args:
        model_type: "simple_nn", "cnn", or "logistic_regression"
        input_size: Number of input features
        num_classes: Number of output classes
    
    Returns:
        PyTorch model instance
    
    Example:
        # To switch models, just change model_type:
        model = get_model("cnn", input_size=30, num_classes=2)
        model = get_model("logistic_regression", input_size=30, num_classes=2)
    """
    
    models = {
        "simple_nn": SimpleNN,
        "cnn": SimpleCNN,
        "logistic_regression": LogisticRegressionModel,
    }
    
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}. Available: {list(models.keys())}")
    
    return models[model_type](input_size=input_size, num_classes=num_classes)


if __name__ == "__main__":
    # Demo: Show model flexibility
    print("Federated Learning Simulator - Model Support\n")
    
    for model_name in ["simple_nn", "cnn", "logistic_regression"]:
        model = get_model(model_name, input_size=30, num_classes=2)
        print(f"✓ {model_name.upper()}: {sum(p.numel() for p in model.parameters())} parameters")
    
    print("\n💡 Any of these models can be used with the simulator!")
    print("   Change MODEL_TYPE in config.py to switch models instantly.")
