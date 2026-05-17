"""
Quick start guide for Federated Learning project
Run this to set up your development environment
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✓ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - Failed!")
        return False

def main():
    print("\n" + "="*60)
    print("🌐 FEDERATED LEARNING - Quick Start")
    print("="*60)
    
    # Step 1: Run setup.py
    print("\nStep 1️⃣  Creating project structure...")
    if not os.path.exists('model'):
        exec(open('setup.py').read())
    else:
        print("✓ Project structure already exists")
    
    # Step 2: Install dependencies
    print("\nStep 2️⃣  Installing dependencies...")
    if run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing packages"):
        print("✓ Dependencies installed!")
    
    # Step 3: Verify installation
    print("\nStep 3️⃣  Verifying installation...")
    try:
        import torch
        import flwr
        import streamlit
        print("✓ All packages verified!")
        print(f"  - PyTorch version: {torch.__version__}")
        print(f"  - Flower version: {flwr.__version__}")
    except ImportError as e:
        print(f"✗ Package verification failed: {e}")
    
    # Final instructions
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\n📌 To run the Federated Learning system:")
    print("\nOpen 4 terminals:")
    print("  Terminal 1: python server/server.py")
    print("  Terminal 2: python clients/client.py 0")
    print("  Terminal 3: python clients/client.py 1")
    print("  Terminal 4: python clients/client.py 2")
    print("\nOptional - View dashboard:")
    print("  streamlit run dashboard/app.py")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
