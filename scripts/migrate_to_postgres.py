#!/usr/bin/env python3
"""
File path: scripts/migrate_to_postgres.py
Purpose: Convenience wrapper — delegates to backend/scripts/migrate_to_postgres.py.
         Run from the project root: python scripts/migrate_to_postgres.py --source ... --target ...
"""
import subprocess
import sys
import os

script = os.path.join(os.path.dirname(__file__), "..", "backend", "scripts", "migrate_to_postgres.py")
result = subprocess.run([sys.executable, os.path.abspath(script)] + sys.argv[1:])
sys.exit(result.returncode)
