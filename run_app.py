"""
ScamShield AI - Unified Single-Port Application Launcher
Serves the complete React cybersecurity dashboard, URL scanner, REST APIs,
and interactive Swagger documentation on a single unified URL: http://127.0.0.1:8000
"""

import os
import sys
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")

def main():
    # 1. Build frontend if dist doesn't exist
    if not os.path.exists(INDEX_HTML):
        print("[*] Building frontend assets for unified hosting...")
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, shell=True, check=True)

    # 2. Determine python binary
    venv_python = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
    python_bin = venv_python if os.path.exists(venv_python) else sys.executable

    print("\n" + "=" * 65)
    print("  🛡️  ScamShield AI — Unified Single Localhost Server")
    print("=" * 65)
    print("  • Complete Dashboard (UI):     http://127.0.0.1:8000")
    print("  • Message Scam Scanner:        http://127.0.0.1:8000")
    print("  • URL Phishing Scanner:        http://127.0.0.1:8000")
    print("  • Interactive API Docs:        http://127.0.0.1:8000/docs")
    print("  • System Health Check:         http://127.0.0.1:8000/api/health")
    print("=" * 65 + "\n")

    # 3. Start unified backend
    subprocess.run([python_bin, "run.py"], cwd=BACKEND_DIR)

if __name__ == "__main__":
    main()
