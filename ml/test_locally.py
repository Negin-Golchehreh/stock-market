#!/usr/bin/env python3
import sys
import subprocess

# ── Auto-install dependencies ─────────────────────────────────
REQUIRED = ['pandas', 'numpy', 'scikit-learn', 'matplotlib', 'seaborn', 'xgboost', 'joblib']
for pkg in REQUIRED:
    try:
        __import__(pkg.replace('-', '_'))
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

print("✓ All dependencies ready\n")

# ── Run the ML pipeline ───────────────────────────────────────
exec(open('02_ml_pipeline.py').read())
