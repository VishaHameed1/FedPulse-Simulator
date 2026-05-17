import torch
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
