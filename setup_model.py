import os
import subprocess
import sys

MODEL_PATH = os.path.abspath('out/model.pt')
MODEL_URL = os.environ.get('MODEL_DOWNLOAD_URL')

os.makedirs('out', exist_ok=True)

if os.path.exists(MODEL_PATH):
    print(f"✓ Model already exists at {MODEL_PATH}")
    sys.exit(0)

if MODEL_URL:
    print(f"Attempting to download model from {MODEL_URL}...")
    try:
        import urllib.request
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print(f"✓ Downloaded model to {MODEL_PATH}")
        sys.exit(0)
    except Exception as e:
        print(f"[WARN] Failed to download model: {e}")
        print("Falling back to generating a dummy model...")

# Fallback: generate dummy model
print("Generating dummy model using generate_sample_model.py...")
subprocess.check_call([sys.executable, 'generate_sample_model.py'])
print("✓ Dummy model generated.")
