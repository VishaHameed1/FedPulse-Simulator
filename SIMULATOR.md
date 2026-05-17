# Federated Learning Simulator

## 🎯 What Makes This a "Simulator"?

This project is a **complete Federated Learning Simulator** that demonstrates how distributed machine learning works while preserving privacy. Unlike hardcoded implementations, this simulator allows you to:

1. **Switch Datasets** - Use any medical, tabular, or custom dataset
2. **Switch Models** - Test with different architectures (MLP, CNN, Logistic Regression)
3. **Configure Training** - Adjust clients, rounds, and hyperparameters easily
4. **Visualize Privacy** - See exactly what data stays private vs. what's shared

---

## 📊 Supported Datasets

The simulator comes pre-configured with three datasets, but you can add any dataset:

### 1. **Breast Cancer Wisconsin** (Default - Healthcare)
- **Use Case**: Hospital federated learning scenario
- **Samples**: 569 patient records
- **Features**: 30 medical measurements
- **Classes**: 2 (Malignant/Benign)
- **Privacy Focus**: Healthcare data never leaves client

### 2. **Iris Classification** (Classic ML)
- **Use Case**: Simple multi-class classification
- **Samples**: 150 iris flowers
- **Features**: 4 sepal/petal measurements
- **Classes**: 3 iris species
- **Privacy Focus**: Botanical research data distribution

### 3. **Synthetic Binary** (Testing)
- **Use Case**: Quick testing and demos
- **Samples**: 1000 generated samples
- **Features**: 10 random features
- **Classes**: 2 balanced classes
- **Privacy Focus**: Dummy data for algorithm testing

---

## 🧠 Supported Models

The simulator supports multiple model architectures, proving it's flexible:

### 1. **Simple Neural Network (MLP)** [Default]
```
Input (30 features)
    ↓
Dense(128) + ReLU + Dropout
    ↓
Dense(64) + ReLU + Dropout
    ↓
Dense(2) → Output
```
**Best for**: General classification, baseline models

### 2. **Convolutional Neural Network (CNN)**
```
Input
    ↓
Conv1D(32) → MaxPool
    ↓
Conv1D(64) → MaxPool
    ↓
Flatten → Dense(128) → Dense(output)
```
**Best for**: Image data, spatial features, feature extraction

### 3. **Logistic Regression**
```
Input (30 features)
    ↓
Linear layer → Output
```
**Best for**: Baseline comparison, linear separability testing

---

## ⚙️ How to Configure the Simulator

All simulator settings are in **`config.py`**:

### Step 1: Choose a Dataset
```python
# config.py
DATASET_TYPE = "breast_cancer"  # Options: "breast_cancer", "iris", "synthetic"
```

### Step 2: Choose a Model
```python
# config.py
MODEL_TYPE = "simple_nn"  # Options: "simple_nn", "cnn", "logistic_regression"
```

### Step 3: Adjust Training Parameters
```python
# config.py
NUM_CLIENTS = 3
NUM_ROUNDS = 5
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS_PER_ROUND = 1
```

### Step 4: Restart Everything
```bash
# Terminal 1: Stop and restart server
python server/server.py

# Terminal 2-4: Stop and restart clients
python clients/client.py 0
python clients/client.py 1
python clients/client.py 2

# Terminal 5: View dashboard (optional)
streamlit run dashboard/app.py
```

---

## 🔄 Example: Switching from Breast Cancer to Iris

### Before (Breast Cancer setup):
```python
# config.py
DATASET_TYPE = "breast_cancer"
MODEL_TYPE = "simple_nn"
```
- Input size: 30 features
- Classes: 2 (Malignant/Benign)
- Simulator works with 569 patient records

### After (Iris setup):
```python
# config.py
DATASET_TYPE = "iris"
MODEL_TYPE = "simple_nn"  # Same model, different data!
```
- Input size: 4 features (automatically adjusted)
- Classes: 3 iris species (automatically adjusted)
- Simulator works with 150 iris flowers

**Result**: No code changes needed! The simulator automatically adapts:
- ✓ Data loader adjusts to iris data shape
- ✓ Model input/output layers auto-resize
- ✓ Clients still train locally with iris data
- ✓ Server still receives only weights
- ✓ Privacy guarantee remains 100%

---

## 🔐 Zero Server Data Guarantee

### What Data Flows Where:

**CLIENT SIDE (Private)**
```
Each Client's Local Machine:
├── Raw Data (Patient Records) → 5MB each
├── Training Data Samples
├── Test Data Samples
└── LOCAL MODEL (trained on private data)
    └── Sends only: Model Weights (~1KB)
```

**SERVER SIDE (Aggregator)**
```
Central Server:
├── Model Weights (θ) → 50KB total
├── Aggregation Algorithm (FedAvg)
└── Training Metadata
    └── ❌ NO raw data
    └── ❌ NO patient records
    └── ❌ NO sensitive information
```

**Communication Between Client & Server:**
```
Client 1 Data: 5MB ──────┐
Client 2 Data: 5MB ──────┤ (All stays local!)
Client 3 Data: 5MB ──────┘

Client 1 Weights: 1KB ──────┐
Client 2 Weights: 1KB ──────┼──→ Server ──→ FedAvg ──→ Global Model
Client 3 Weights: 1KB ──────┘
```

---

## 🚀 Running the Simulator

### Quick Start (Default Breast Cancer + MLP):
```bash
# Terminal 1: Start server
python server/server.py

# Terminal 2-4: Start clients (one each)
python clients/client.py 0
python clients/client.py 1
python clients/client.py 2

# Terminal 5: View dashboard
streamlit run dashboard/app.py
```

### Advanced: Run with Different Configuration
```bash
# Edit config.py
# Change DATASET_TYPE = "iris"
# Change MODEL_TYPE = "cnn"

# Then restart as normal
python server/server.py
python clients/client.py 0
python clients/client.py 1
python clients/client.py 2
```

---

## 📈 Dashboard Features

The interactive dashboard shows:

### 🔒 Zero Server Data Visualization
- Side-by-side comparison of client data vs. server data
- Clear proof: Server has 0 bytes of raw data
- Visual flow showing weights-only communication

### ⚙️ Simulator Configuration Panel
- Dropdown to see current dataset
- Dropdown to see current model
- Instructions on how to change them
- Auto-detected configuration

### 📊 Training Progress
- Global accuracy over rounds
- FedAvg algorithm in action
- Weight aggregation progression

### 👥 Client Status
- Connected clients and their status
- Local data samples per client
- Weight update confirmations

---

## 🧪 Example Use Cases

### Use Case 1: Healthcare Demo
```python
DATASET_TYPE = "breast_cancer"
MODEL_TYPE = "simple_nn"
NUM_CLIENTS = 3  # Representing 3 hospitals
```
**Message**: "Three hospitals collaborate without sharing patient data"

### Use Case 2: Multi-Model Comparison
```python
# Run 1:
DATASET_TYPE = "breast_cancer"
MODEL_TYPE = "simple_nn"

# Run 2:
DATASET_TYPE = "breast_cancer"
MODEL_TYPE = "cnn"

# Run 3:
DATASET_TYPE = "breast_cancer"
MODEL_TYPE = "logistic_regression"
```
**Message**: "Same data, different models - simulator shows flexibility"

### Use Case 3: Multi-Dataset Validation
```python
# Run 1: Breast Cancer
DATASET_TYPE = "breast_cancer"

# Run 2: Iris
DATASET_TYPE = "iris"

# Run 3: Synthetic
DATASET_TYPE = "synthetic"
```
**Message**: "Simulator works with any dataset architecture"

---

## 🔬 Technical Details

### How Model Auto-Resizing Works

```python
# In config.py - dataset determines model input
DATASET_TYPE = "iris"  # 4 features
dataset_config = get_dataset_config("iris")
input_size = dataset_config["input_size"]  # = 4

# In client.py - model auto-adjusts
model = get_model(
    model_type="simple_nn",
    input_size=4,  # ← Automatically set to iris features
    num_classes=3   # ← Automatically set to iris classes
)
```

### How Data Splitting Works

```
Total Iris Dataset: 150 samples
├── Training: 120 samples (80%)
│   ├── Client 0: 40 samples
│   ├── Client 1: 40 samples
│   └── Client 2: 40 samples
└── Testing: 30 samples (20%)
    └── Used by all clients for evaluation
```

Each client trains **ONLY** on its 40 local samples, never sees others' data!

---

## 📚 Learning Resources

- **Flower Framework**: https://flower.ai
- **Federated Learning Paper**: https://arxiv.org/abs/1602.05629 (McMahan et al.)
- **PyTorch Docs**: https://pytorch.org/docs/
- **Privacy in ML**: https://www.tensorflow.org/federated

---

## 🎓 What Students Can Learn

By studying this simulator, you'll understand:

1. **Federated Learning Fundamentals**
   - How clients train locally
   - How servers aggregate weights
   - The FedAvg algorithm

2. **Privacy Preservation**
   - Why only sending weights protects data
   - The difference between data and models
   - Real-world healthcare applications

3. **Distributed ML Systems**
   - Multi-client coordination
   - Weight synchronization
   - Model convergence in federation

4. **Code Modularity**
   - How to make flexible simulators
   - Configuration-driven applications
   - Easy model/dataset swapping

---

## 🔧 Extending the Simulator

### Add a New Dataset

```python
# 1. In utils/data_loader.py - add loader function
def load_custom_data():
    """Load your custom dataset"""
    X, y = load_your_data()  # Your data source
    return X, y, {
        "name": "Your Dataset",
        "samples": len(X),
        "features": X.shape[1],
        "classes": len(np.unique(y)),
        "class_names": ["Class A", "Class B"]
    }

# 2. In config.py - add configuration
CUSTOM_CONFIG = {
    "input_size": 20,
    "num_classes": 2,
    "dataset_name": "Your Dataset",
    "num_samples": 1000,
    "num_features": 20,
}

# 3. In data_loader.py - register in loaders dict
loaders = {
    "breast_cancer": load_breast_cancer_data,
    "iris": load_iris_data,
    "custom": load_custom_data,  # ← Add here
}

# 4. Use it!
DATASET_TYPE = "custom"
```

### Add a New Model

```python
# 1. In model/model.py - add model class
class CustomModel(nn.Module):
    def __init__(self, input_size=20, num_classes=2):
        super(CustomModel, self).__init__()
        # Your architecture
    
    def forward(self, x):
        # Your forward pass
        return x

# 2. In model.py - register in factory
models = {
    "simple_nn": SimpleNN,
    "cnn": SimpleCNN,
    "logistic_regression": LogisticRegressionModel,
    "custom": CustomModel,  # ← Add here
}

# 3. Use it!
MODEL_TYPE = "custom"
```

---

## ✅ Summary

This **Federated Learning Simulator** demonstrates:

| Feature | What It Shows |
|---------|---------------|
| **Zero Server Data** | Server has 0 bytes of raw patient data |
| **Modularity** | Easy swap of datasets, models, hyperparameters |
| **Privacy First** | Only weights transmitted, not sensitive data |
| **Real-World** | Hospital collaboration scenario |
| **Educational** | Learn FL, FedAvg, privacy preservation |

**The simulator proves**: Powerful distributed ML is possible while keeping data 100% private! 🔒

---

*Created as a final year project demonstrating Federated Learning & Healthcare Data Privacy*
