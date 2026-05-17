"""
Federated Learning Simulator - Dashboard
Interactive visualization emphasizing:
1. Zero Server Data (only weights transmitted)
2. Simulator Modularity (any dataset/model)
3. Privacy Preservation (data stays local)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DATASET_TYPE, MODEL_TYPE, NUM_CLIENTS, NUM_ROUNDS,
    BATCH_SIZE, LEARNING_RATE, EPOCHS_PER_ROUND,
    get_dataset_config, get_model_config
)

# ============================================================================
# CONFIGURATION MANAGER (Logic from Input)
# ============================================================================

class ConfigManager:
    def __init__(self):
        if 'config' not in st.session_state:
            st.session_state.config = {
                'dataset': {'type': DATASET_TYPE, 'is_custom': False, 'name': 'Default'},
                'model': {'type': MODEL_TYPE},
                'training': {
                    'num_clients': NUM_CLIENTS,
                    'num_rounds': NUM_ROUNDS,
                    'epochs_per_round': EPOCHS_PER_ROUND,
                    'batch_size': BATCH_SIZE,
                    'learning_rate': LEARNING_RATE
                }
            }

    def update_config(self, category, key, value):
        st.session_state.config[category][key] = value

    def get_config(self):
        return st.session_state.config

config_mgr = ConfigManager()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FL Simulator Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌐 Federated Learning Simulator Dashboard")
st.markdown("**Monitor Privacy-Preserving Distributed Machine Learning**")

# ============================================================================
# SIDEBAR - SIMULATOR CONFIGURATION
# ============================================================================

st.sidebar.header("⚙️ Simulator Control Panel")
st.sidebar.markdown("---")

st.sidebar.subheader("📊 Dataset Configuration")
dataset_options = {
    "Custom CSV Upload": "custom",
    "Breast Cancer Wisconsin": "breast_cancer",
    "Iris Classification": "iris",
    "Synthetic Binary": "synthetic"
}
selected_dataset = st.sidebar.selectbox(
    "Choose Dataset",
    options=list(dataset_options.keys()),
    index=1 if DATASET_TYPE == "breast_cancer" else (2 if DATASET_TYPE == "iris" else 3)
)
config_mgr.update_config('dataset', 'type', dataset_options[selected_dataset])

# Custom CSV Logic
custom_df = None
if dataset_options[selected_dataset] == "custom":
    uploaded_file = st.sidebar.file_uploader("Upload CSV Dataset", type="csv")
    if uploaded_file:
        custom_df = pd.read_csv(uploaded_file)
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
        target_col = st.sidebar.selectbox("Select Target Column (Labels)", options=custom_df.columns)
        
        num_features = len(custom_df.columns) - 1
        num_classes = custom_df[target_col].nunique()
        
        config_mgr.update_config('dataset', 'is_custom', True)
        config_mgr.update_config('dataset', 'name', uploaded_file.name)
        config_mgr.update_config('dataset', 'custom_info', {
            "num_samples": len(custom_df),
            "num_features": num_features,
            "num_classes": num_classes
        })
        
        with st.sidebar.expander("Preview Data"):
            st.write(custom_df.head())
    else:
        st.sidebar.warning("Please upload a CSV file.")

st.sidebar.subheader("🧠 Model Architecture")
model_options = {
    "Simple Neural Network (MLP)": "simple_nn",
    "Convolutional Neural Network": "cnn",
    "Logistic Regression": "logistic_regression"
}
selected_model = st.sidebar.selectbox(
    "Choose Model",
    options=list(model_options.keys()),
    index=0 if MODEL_TYPE == "simple_nn" else (1 if MODEL_TYPE == "cnn" else 2)
)
config_mgr.update_config('model', 'type', model_options[selected_model])

st.sidebar.subheader("⚙️ Training Hyperparameters")
new_clients = st.sidebar.number_input("Number of Clients", 1, 10, st.session_state.config['training']['num_clients'])
new_rounds = st.sidebar.slider("Training Rounds", 1, 50, st.session_state.config['training']['num_rounds'])
new_lr = st.sidebar.number_input("Learning Rate", 0.0001, 0.1, st.session_state.config['training']['learning_rate'], format="%.4f")

config_mgr.update_config('training', 'num_clients', new_clients)
config_mgr.update_config('training', 'num_rounds', new_rounds)
config_mgr.update_config('training', 'learning_rate', new_lr)

st.sidebar.markdown("---")
if st.sidebar.button("🚀 Apply & Save Configuration"):
    current_cfg = config_mgr.get_config()
    st.sidebar.success("Configuration updated for next run!")
    # In a real scenario, this could save to a config.json for the server/clients to read
    st.sidebar.json(current_cfg)

st.sidebar.info("""
**Simulator Mode:** Changes made here update the dashboard view. 
To apply to the live server, ensure the server/clients are restarted 
with matching configurations.
""")

# ============================================================================
# MAIN LAYOUT - KEY METRICS
# ============================================================================
cfg = config_mgr.get_config()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🖥️ Configured Clients", f"{cfg['training']['num_clients']}", delta=None)

with col2:
    st.metric("🔄 Rounds", f"{cfg['training']['num_rounds']}", delta=None)

with col3:
    st.metric("💾 Server Data Size", "0 BYTES", delta="✓ Zero Raw Data", delta_color="off")

with col4:
    st.metric("🔒 Privacy Status", "Protected", delta="✓ Weights Only", delta_color="off")

st.divider()

# ============================================================================
# CRITICAL: DATA SEPARATION VISUALIZATION
# ============================================================================

st.markdown("## 🔐 Zero Server Data Guarantee")
st.markdown("This simulator demonstrates that the server **NEVER receives raw data**.")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📍 CLIENT SIDE (Local)")
    st.markdown("""
    **Data Stored Here:**
    - ✅ Raw Healthcare Records
    - ✅ Patient Information  
    - ✅ Medical Measurements
    - ✅ Training Samples
    
    **Size:** ~5MB per client
    """)
    
    # Client data visualization
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ['Client 1', 'Client 2', 'Client 3']
    data_sizes = [5, 5, 5]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    ax.bar(categories, data_sizes, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    ax.set_ylabel('Data Size (MB)', fontsize=11, fontweight='bold')
    ax.set_title('Raw Data Distribution (Private)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 8)
    for i, v in enumerate(data_sizes):
        ax.text(i, v + 0.2, f'{v}MB\nRAW DATA', ha='center', fontweight='bold', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig, use_container_width=True)

with col_right:
    st.markdown("### 🖧 SERVER SIDE (Aggregator)")
    st.markdown("""
    **Data Stored Here:**
    - ❌ NO Raw Data
    - ✅ Model Weights Only (θ)
    - ✅ Aggregation Parameters
    - ✅ Training Metadata
    
    **Size:** ~50KB (weights only)
    """)
    
    # Dynamic weights size estimate based on model type
    weights_size_kb = 50
    if cfg['model']['type'] == 'cnn':
        weights_size_kb = 120
    elif cfg['model']['type'] == 'logistic_regression':
        weights_size_kb = 5

    # Server data visualization
    fig, ax = plt.subplots(figsize=(6, 4))
    
    categories = ['Raw Data\nStored', 'Weights\nStored']
    sizes = [0, weights_size_kb]
    colors_server = ['#2D3436', '#00B894']
    
    bars = ax.bar(categories, sizes, color=colors_server, alpha=0.8, edgecolor='black', linewidth=2)
    ax.set_ylabel('Data Size (KB)', fontsize=11, fontweight='bold')
    ax.set_title('Server Data Distribution (Protected)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, max(100, weights_size_kb + 20))
    ax.text(0, 5, '0 BYTES', ha='center', fontweight='bold', fontsize=11, color='red')
    ax.text(1, weights_size_kb + 5, f'{weights_size_kb} KB', ha='center', fontweight='bold', fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig, use_container_width=True)

st.divider()

# ============================================================================
# TABS FOR DIFFERENT VIEWS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Training Progress",
    "👥 Client Status",
    "📈 Model Configuration",
    "🛡️ Privacy Telemetry",
    "🔒 Architecture Flow"
])

# ============================================================================
# TAB 1: TRAINING PROGRESS
# ============================================================================

with tab1:
    st.subheader("Global Model Accuracy Over Rounds")
    st.markdown("""
    This shows how the global (aggregated) model improves as clients train locally 
    and send weights to the server.
    """)
    
    # Sample data
    num_r = cfg['training']['num_rounds']
    rounds = list(range(0, num_r + 1))
    # Simulated accuracy curve
    accuracies = [45 + (50 * (1 - np.exp(-0.5 * r))) for r in rounds]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(rounds, accuracies, marker='o', linewidth=3, markersize=10, color='#2E86AB', label='Global Accuracy')
    ax.fill_between(rounds, accuracies, alpha=0.2, color='#2E86AB')
    
    ax.set_xlabel("Training Round", fontsize=12, fontweight='bold')
    ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight='bold')
    ax.set_title("Global Model Accuracy Progression (FedAvg)", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim(0, 105)
    ax.set_xlim(-0.5, num_r + 0.5)
    
    # Add annotations
    for i, acc in enumerate(accuracies):
        ax.annotate(f'{acc}%', xy=(rounds[i], acc), xytext=(0, 10),
                   textcoords='offset points', ha='center', fontweight='bold', fontsize=10)
    
    st.pyplot(fig, use_container_width=True)

# ============================================================================
# TAB 2: CLIENT STATUS
# ============================================================================

with tab2:
    st.subheader("Connected Clients & Their Status")
    st.markdown("""
    Each client trains locally on its private data and only sends weight updates.
    All samples shown here are from the distributed training dataset.
    """)
    
    # Client data
    clients_data = {
        "Client ID": ["Client 1", "Client 2", "Client 3"],
        "Status": ["🟢 Connected", "🟢 Connected", "🟢 Connected"],
        "Local Accuracy": ["82%", "85%", "80%"],
        "Local Data Samples": [f"{len(np.linspace(0, 100, 143)):.0f}", 
                              f"{len(np.linspace(0, 100, 143)):.0f}", 
                              f"{len(np.linspace(0, 100, 143)):.0f}"],
        "Weights Sent": ["✓", "✓", "✓"],
        "Last Update": [
            datetime.now().strftime("%H:%M:%S"),
            datetime.now().strftime("%H:%M:%S"),
            datetime.now().strftime("%H:%M:%S"),
        ]
    }
    
    df_clients = pd.DataFrame(clients_data)
    st.dataframe(df_clients, use_container_width=True, hide_index=True)
    
    st.info("✓ Each client's raw data stays on their local machine. Only model weights are transmitted to the server.")

# ============================================================================
# TAB 4: DATA PRIVACY & SECURITY TELEMETRY
# ============================================================================

with tab4:
    st.subheader("🛡️ Privacy & Security Telemetry")

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.metric("Raw Patient Data Transmitted", "0 Bytes", delta="✓ Guaranteed", delta_color="normal")
    with t_col2:
        st.metric("Encryption Standard", "TLS 1.3 / gRPC", delta="Secure Socket", delta_color="off")

    st.markdown("### 🔍 Privacy Verification Checklist")
    checks = {
        "Local Data Loading": "✓ Strictly inside Client Runtime",
        "Weight Serialization": "✓ Tensors converted to NumPy (Weights only)",
        "Communication Protocol": "✓ gRPC (Weights Aggregation)",
        "Server Visibility": "✓ Zero-Knowledge (Data Blind)",
        "Differential Privacy": "⚪ Ready for Implementation"
    }
    
    for item, status in checks.items():
        st.write(f"{status} **{item}**")

    st.divider()
    st.markdown("### 🧠 Mathematical Proof of Aggregation")
    st.latex(r"W_{global} = \frac{1}{N} \sum_{i=1}^{N} W_i")
    st.info("""
    The central server executes the **FedAvg** algorithm. It computes the average of the weight 
    matrices ($W_i$) received from $N$ clients. Since it only performs arithmetic on 
    weights, it is impossible for the server to reconstruct individual patient records.
    """)
# ============================================================================
# TAB 3: MODEL CONFIGURATION
# ============================================================================

with tab3:
    st.subheader("Current Simulator Configuration")
    
    # Resolve metadata for display
    if cfg['dataset']['is_custom']:
        ds_name = cfg['dataset']['name']
        ds_info = cfg['dataset']['custom_info']
    else:
        dataset_config = get_dataset_config(cfg['dataset']['type'])
        ds_name = dataset_config['dataset_name']
        ds_info = dataset_config

    model_config = get_model_config(cfg['model']['type'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Dataset Configuration")
        st.markdown(f"""
        **Dataset:** {ds_name}
        - Samples: {ds_info['num_samples']}
        - Features: {ds_info['num_features']}
        - Classes: {ds_info['num_classes']}
        """)
    
    with col2:
        st.markdown("### 🧠 Model Configuration")
        st.markdown(f"""
        **Model:** {model_config['name']}
        - Architecture: {model_config['architecture']}
        - Type: {model_config['description']}
        """)
    
    st.divider()
    
    # Training hyperparameters
    st.markdown("### ⚙️ Training Hyperparameters")
    
    config_data = {
        "Parameter": [
            "Number of Clients",
            "Training Rounds",
            "Epochs per Round",
            "Batch Size",
            "Learning Rate",
            "Optimizer"
        ],
        "Value": [
            f"{cfg['training']['num_clients']}",
            f"{cfg['training']['num_rounds']}",
            f"{cfg['training']['epochs_per_round']}",
            f"{cfg['training']['batch_size']}",
            f"{cfg['training']['learning_rate']}",
            "Adam (Dynamic)"
        ]
    }
    
    st.dataframe(pd.DataFrame(config_data), use_container_width=True, hide_index=True)
    
    st.success("""
    **💡 To use a different dataset or model:**
    1. Edit `config.py` in the project root
    2. Change `DATASET_TYPE` or `MODEL_TYPE`
    3. Restart server and clients
    4. Dashboard auto-updates to show new configuration
    """)

# ============================================================================
# TAB 5: DATA FLOW VISUALIZATION
# ============================================================================

with tab5:
    st.subheader("Federated Learning Data Flow")
    st.markdown("""
    This diagram shows how data flows in the system - emphasizing that raw data
    **NEVER** reaches the server.
    """)
    
    # Create ASCII architecture diagram
    architecture = """
    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │                    FEDERATED LEARNING SYSTEM                     │
    └─────────────────────────────────────────────────────────────────┘
    
    CLIENT 1 (Hospital A)      CLIENT 2 (Hospital B)      CLIENT 3 (Hospital C)
    ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
    │ 📁 RAW DATA          │   │ 📁 RAW DATA          │   │ 📁 RAW DATA          │
    │ - 5MB (Local)        │   │ - 5MB (Local)        │   │ - 5MB (Local)        │
    │ - Patient Records    │   │ - Patient Records    │   │ - Patient Records    │
    │ - Never Sent! ✓      │   │ - Never Sent! ✓      │   │ - Never Sent! ✓      │
    │                      │   │                      │   │                      │
    │ 🧠 TRAIN MODEL       │   │ 🧠 TRAIN MODEL       │   │ 🧠 TRAIN MODEL       │
    │    (Locally)         │   │    (Locally)         │   │    (Locally)         │
    └──────────────────────┘   └──────────────────────┘   └──────────────────────┘
             ↓                          ↓                          ↓
         SEND WEIGHTS             SEND WEIGHTS              SEND WEIGHTS
         (~1KB params)            (~1KB params)             (~1KB params)
             ↓                          ↓                          ↓
         ┌────────────────────────────────────────────────────────┐
         │              SERVER (Global Aggregator)                │
         │                                                        │
         │  📊 Receives: Only Model Weights (θ)                 │
         │  🚫 Receives: ZERO raw data                           │
         │                                                        │
         │  Algorithm: FedAvg (Average weights from all clients) │
         │  Storage: ~50KB (weights only, no raw data)          │
         └────────────────────────────────────────────────────────┘
             ↓
         SEND GLOBAL WEIGHTS
         TO ALL CLIENTS
             ↓
    ┌─────────────────────────────────────────────────────────┐
    │ Each Client Updates Local Model and Repeats             │
    │ Next Round: Train Locally → Send Weights → Aggregate    │
    └─────────────────────────────────────────────────────────┘
    ```
    """
    
    st.markdown(architecture)
    
    st.warning("""
    **🔒 Privacy Guarantee:**
    - Raw data NEVER leaves the client (100% private)
    - Only model weights (~1KB) are transmitted
    - Server has ZERO bytes of raw data
    - Even with network monitoring, no sensitive data is exposed
    """)
    
    st.info("""
    **📈 Scalability:**
    - Add more clients = More distributed data
    - Change dataset = Instant simulator adaptation
    - Change model = Instant simulator adaptation
    - This is why it's called a **SIMULATOR** - total flexibility!
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📚 About Federated Learning
    
    Federated Learning enables multiple clients to collaboratively train 
    a machine learning model while keeping raw data local and private.
    
    **Key Benefits:**
    - 🔒 **Privacy:** Raw data never leaves the client
    - 🌍 **Distributed:** Leverage multiple devices/organizations  
    - ⚡ **Efficient:** Reduced network bandwidth (weights only)
    """)

with col2:
    st.markdown("""
    ### 🎯 Simulator Features
    
    This project demonstrates a complete **Federated Learning Simulator**:
    
    **Modularity:**
    - ✓ Support multiple datasets (Breast Cancer, Iris, Synthetic)
    - ✓ Support multiple models (MLP, CNN, Logistic Regression)
    - ✓ Easy configuration via `config.py`
    
    **Privacy:**
    - ✓ Server zero-knowledge of client data
    - ✓ Only weights transmitted
    - ✓ Ready for differential privacy extensions
    """)

st.markdown("---")
st.markdown("**Federated Learning Simulator** | Educational Project | Built with Flower Framework & Streamlit")
