#!/usr/bin/env python3
"""
File path: scripts/train_initial_models.py
Purpose: Convenience wrapper — delegates to backend/scripts/train_initial_models.py.
         Run from the project root: python scripts/train_initial_models.py
"""
import subprocess
import sys
import os

script = os.path.join(os.path.dirname(__file__), "..", "backend", "scripts", "train_initial_models.py")
result = subprocess.run([sys.executable, os.path.abspath(script)] + sys.argv[1:])
sys.exit(result.returncode)
