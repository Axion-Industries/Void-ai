#!/usr/bin/env python3
import os
import sys
import torch
import pickle

def verify_setup():
    """Verify all components are properly set up."""
    issues = []
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (
        python_version.major == 3 and python_version.minor < 7
    ):
        issues.append("Python version must be 3.7 or higher")
        issues.append(f"Python 3.7+ required, found {python_version.major}.{python_version.minor}")
    required_dirs = ["out", "data/void"]
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            issues.append(f"Missing required directory: {dir_path}")

    # Check required files
    required_files = {
        'out/model.pt': 'Model weights',
        'data/void/vocab.pkl': 'Vocabulary file',
        'data/void/meta.pkl': 'Meta configuration',
        'requirements.txt': 'Requirements file'
    }
    for file_path, description in required_files.items():
        if not os.path.isfile(file_path):
            issues.append(f"Missing required file: {description} at {file_path}")
    # Check PyTorch
    try:
        import torch
        print("CUDA available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("GPU device:", torch.cuda.get_device_name(0))
    except Exception as e:
        issues.append(f"PyTorch not installed or import failed: {e}")

    # Try loading vocab and meta
    if os.path.exists('data/void/vocab.pkl'):
        try:
            with open('data/void/vocab.pkl', 'rb') as f:
                pickle.load(f)
        except Exception as e:
            issues.append(f"Failed to load vocab.pkl: {e}")
    if os.path.exists('data/void/meta.pkl'):
        try:
            with open('data/void/meta.pkl', 'rb') as f:
                pickle.load(f)
        except Exception as e:
            issues.append(f"Failed to load meta.pkl: {e}")
    return issues


def main():
    print("=== Void AI Setup Verification ===")
    issues = verify_setup()
    if issues:
        print("[ERROR] Setup verification failed:")
        for issue in issues:
            print(f" - {issue}")
        sys.exit(1)
    else:
        print("[OK] All setup checks passed.")

if __name__ == '__main__':
    main()
