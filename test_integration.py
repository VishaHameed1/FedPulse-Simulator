#!/usr/bin/env python
"""
Integration test script for Federated Learning project
Tests that all components can be imported and initialized
"""

import sys
import importlib

def test_imports():
    """Test all required imports"""
    print("\n" + "="*60)
    print("🧪 Testing Imports")
    print("="*60)
    
    required_packages = {
        'torch': 'PyTorch',
        'flwr': 'Flower Framework',
        'sklearn': 'Scikit-learn',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'streamlit': 'Streamlit',
    }
    
    all_passed = True
    
    for package, name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {name} ({package})")
        except ImportError as e:
            print(f"✗ {name} ({package}) - NOT INSTALLED")
            all_passed = False
    
    return all_passed

def test_model():
    """Test model creation"""
    print("\n" + "="*60)
    print("🧠 Testing Model")
    print("="*60)
    
    try:
        sys.path.insert(0, '.')
        from model.model import get_model
        
        model = get_model()
        print(f"✓ Model created successfully")
        print(f"✓ Model type: {type(model).__name__}")
        
        # Test forward pass
        import torch
        dummy_input = torch.randn(1, 30)
        output = model(dummy_input)
        print(f"✓ Forward pass successful")
        print(f"✓ Output shape: {output.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_data_loader():
    """Test data loader"""
    print("\n" + "="*60)
    print("📊 Testing Data Loader")
    print("="*60)
    
    try:
        sys.path.insert(0, '.')
        from utils.data_loader import load_breast_cancer_dataset, get_dataset_info
        
        info = get_dataset_info()
        print(f"✓ Dataset info retrieved")
        print(f"  - Samples: {info['num_samples']}")
        print(f"  - Features: {info['num_features']}")
        print(f"  - Classes: {info['num_classes']}")
        
        train_loader, test_loader = load_breast_cancer_dataset(client_id=0, num_clients=3)
        print(f"✓ Data loaders created")
        print(f"  - Train batches: {len(train_loader)}")
        print(f"  - Test batches: {len(test_loader)}")
        
        return True
    except Exception as e:
        print(f"✗ Data loader test failed: {e}")
        return False

def test_training():
    """Test training utilities"""
    print("\n" + "="*60)
    print("⚡ Testing Training Utilities")
    print("="*60)
    
    try:
        sys.path.insert(0, '.')
        from utils.training import train_epoch, evaluate
        from utils.data_loader import load_breast_cancer_dataset
        from model.model import get_model
        import torch
        
        model = get_model()
        train_loader, test_loader = load_breast_cancer_dataset(client_id=0, num_clients=3)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Test training
        loss = train_epoch(model, train_loader, optimizer, epochs=1)
        print(f"✓ Training successful")
        print(f"  - Average loss: {loss:.4f}")
        
        # Test evaluation
        accuracy, val_loss = evaluate(model, test_loader)
        print(f"✓ Evaluation successful")
        print(f"  - Accuracy: {accuracy:.2f}%")
        print(f"  - Loss: {val_loss:.4f}")
        
        return True
    except Exception as e:
        print(f"✗ Training test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🌐 FEDERATED LEARNING - Integration Test")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Model", test_model),
        ("Data Loader", test_data_loader),
        ("Training", test_training),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ All tests passed! Your FL system is ready to run!")
        print("\n📌 Next steps:")
        print("1. Open 4 terminals")
        print("2. Terminal 1: python server/server.py")
        print("3. Terminal 2: python clients/client.py 0")
        print("4. Terminal 3: python clients/client.py 1")
        print("5. Terminal 4: python clients/client.py 2")
        return 0
    else:
        print("\n⚠️  Some tests failed. Install dependencies first:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
