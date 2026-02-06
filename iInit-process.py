#!/usr/bin/env python3

import os
import subprocess
import sys
import time
import zipfile
import re

# =======================
# 🟢 Configuration
# =======================
PROJECT_DIR = "/last"
APP_FILE = os.path.join(PROJECT_DIR, "app.py")
INIT_FILE = "/etc/init.d/minerpanel"
LOG_FILE = "/tmp/minerpanel.log"

PYTHON_PACKAGES = [
    "flask",
    "requests",
    "beautifulsoup4",
    "pytz",
    "jdatetime",
    "urllib3"
]

# =======================
# 🟢 Utility Functions
# =======================
def print_logo():
    print("""
██  ██  ███   ██████  ██████  ███  ███
█ █ █ █ █ █  █      █ █      █ █  █ █
█  █  █ ███  █  ██  █ █  ██  █  █ ███
█     █ █ █  █   ██ █ █   ██ █     █ █
█     █ █ █   ██████  ██████ █     █ █

            KOP3MA
""")

def pause():
    input("\nPress Enter to continue...")

def indented_print(text, prefix="=>>> "):
    print(f"    {prefix}{text}")

def run_command(cmd_list, show_output=True):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        if show_output:
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print(result.stderr.strip())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

# =======================
# 🟢 Option 1: Download project from Google Drive
# =======================
def download_project():
    print_logo()
    print("="*60)
    print("📥 Download project from Google Drive")
    print("="*60)
    indented_print("Enter File ID or full Google Drive link:")
    user_input = input("    > ").strip()

    if not user_input:
        indented_print("No File ID or link entered!", prefix="=>>> ❌ ")
        pause()
        return

    user_input = user_input.strip().lstrip('/').strip()

    file_id = None

    # استخراج File ID
    patterns = [
        r'([a-zA-Z0-9_-]{33})',                     # ID خام
        r'/d/([a-zA-Z0-9_-]{33})(?:/|\?|$)',        # /d/ID/
        r'file/d/([a-zA-Z0-9_-]{33})',              # file/d/ID
        r'id=([a-zA-Z0-9_-]{33})',                  # id=ID
        r'uc\?[^"]*id=([a-zA-Z0-9_-]{33})',         # uc?id=...
    ]

    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            file_id = match.group(1)
            break

    if not file_id:
        indented_print("Could not extract valid File ID.", prefix="=>>> ❌ ")
        indented_print("Examples:")
        indented_print(" - 1k1TS7j5jv05xo_mBqU1kitYPyOIJDkJv")
        indented_print(" - https://drive.google.com/file/d/1k1TS7j5jv05xo_mBqU1kitYPyOIJDkJv/view")
        pause()
        return

    indented_print(f"Using File ID: {file_id}")

    file_path = os.path.join(PROJECT_DIR, "project.zip")
    if not os.path.exists(PROJECT_DIR):
        os.makedirs(PROJECT_DIR, exist_ok=True)

    print("🔄 Downloading...")
    # استفاده از confirm=t برای دور زدن ویروس اسکن گوگل
    gdrive_url = f"https://drive.google.com/uc?export=download&confirm=t&id={file_id}"
    ret = run_command(["wget", "-O", file_path, "--no-check-certificate", gdrive_url])
    if ret:
        print(f"✅ Download completed: {file_path}")
    else:
        print("❌ Download failed - check if file is 'Anyone with the link'")
        pause()
        return

    print("🗜 Extracting...")
    try:
        if file_path.lower().endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(PROJECT_DIR)
            print("✅ Extraction complete")
        else:
            print("⚠️ Not a zip file")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")

    if os.path.exists(file_path):
        os.remove(file_path)
        print("🗑 Downloaded file removed")

    pause()

# =======================
# 🟢 Option 2: Install Python packages
# =======================
def install_packages():
    print_logo()
    print("="*60)
    print("🔧 Installing Python packages...")
    print("="*60)

    print("🔄 Running opkg update...")
    run_command(["opkg", "update"])

    for pkg in PYTHON_PACKAGES:
        print(f"📦 Installing {pkg} ...")
        run_command(["pip3", "install", "--no-cache-dir", "--timeout", "120", "--retries", "10", pkg])
    print("✅ All packages installed")
    pause()

# =======================
# 🟢 Option 3: Create init.d service & start
# =======================
def create_init_service():
    print_logo()
    print("="*60)
    print("🚀 Creating init.d service...")
    print("="*60)

    init_content = f"""#!/bin/sh /etc/rc.common

START=95
STOP=10
USE_PROCD=1

PROG=/usr/bin/python3
APP={APP_FILE}
WORKDIR={PROJECT_DIR}
LOGFILE={LOG_FILE}

start_service() {{
    echo "🌐 Starting minerpanel service..."
    rm -f $LOGFILE
    procd_open_instance
    procd_set_param command $PROG $APP
    procd_set_param cwd $WORKDIR
    procd_set_param respawn 3600 5 5
    procd_set_param env PYTHONUNBUFFERED=1
    procd_close_instance
    echo "✅ Service started, logging to $LOGFILE"
}}

stop_service() {{
    pid=$(pgrep -f "$APP")
    if [ -n "$pid" ]; then
        kill -9 $pid
        echo "🛑 Service stopped"
    else
        echo "⚠️ Service not running"
    fi
}}
"""
    with open(INIT_FILE, "w") as f:
        f.write(init_content)
    run_command(["chmod", "+x", INIT_FILE])
    run_command([INIT_FILE, "enable"])
    run_command([INIT_FILE, "start"])
    print("✅ Service created and started!")
    pause()

# =======================
# 🟢 Option 4: Manage Python service
# =======================
def manage_service():
    while True:
        print_logo()
        print("="*60)
        print("⚙️ Manage Python Service")
        print("[1] Start service")
        print("[2] Stop service")
        print("[3] Restart service")
        print("[4] Show status")
        print("[0] Back to main menu")
        choice = input("Select an option: ").strip()
        if choice == "1":
            run_command([INIT_FILE, "start"])
        elif choice == "2":
            run_command([INIT_FILE, "stop"])
        elif choice == "3":
            run_command([INIT_FILE, "restart"])
        elif choice == "4":
            ret = subprocess.run(["pgrep","-af","app.py"], capture_output=True, text=True)
            if ret.stdout.strip():
                print("⚙️ Service is running:")
                print(ret.stdout.strip())
            else:
                print("❌ Service is not running")
        elif choice == "0":
            break
        pause()

# =======================
# 🟢 Option 5: List & kill Python processes
# =======================
def list_and_kill_processes():
    print_logo()
    print("="*60)
    print("🔎 Active Python processes")
    print("="*60)

    ret = subprocess.run(["pgrep","-af","python3"], capture_output=True, text=True)
    lines = [l for l in ret.stdout.strip().split("\n") if l]
    if lines:
        for l in lines:
            print(l)
        kill_id = input("\nEnter PID to kill (or press Enter to skip): ").strip()
        if kill_id:
            run_command(["kill","-9", kill_id])
            print(f"✅ PID {kill_id} killed")
    else:
        print("❌ No Python processes found")
    pause()

# =======================
# 🟢 Option 6: Remove service / cleanup
# =======================
def remove_service():
    print_logo()
    print("="*60)
    print("🗑 Removing minerpanel service...")
    print("="*60)

    if os.path.exists(INIT_FILE):
        run_command([INIT_FILE, "stop"])
        run_command([INIT_FILE, "disable"])

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print("🗑 Log file removed")

    if os.path.exists(INIT_FILE):
        os.remove(INIT_FILE)
        print("🗑 init.d service file removed")

    print("✅ Service cleanup completed")
    pause()

# =======================
# 🟢 Main Menu
# =======================
def main_menu():
    while True:
        print_logo()
        print("="*60)
        indented_print("1  Download project from Google Drive")
        indented_print("2  Install Python packages")
        indented_print("3  Create init.d service & start")
        indented_print("4  Manage Python service")
        indented_print("5  List & kill Python processes")
        indented_print("6  Remove service / cleanup")
        indented_print("0  Exit")
        choice = input("    Select an option: ").strip()
        if choice == "1":
            download_project()
        elif choice == "2":
            install_packages()
        elif choice == "3":
            create_init_service()
        elif choice == "4":
            manage_service()
        elif choice == "5":
            list_and_kill_processes()
        elif choice == "6":
            remove_service()
        elif choice == "0":
            print("👋 Exiting...")
            sys.exit(0)
        else:
            print("❌ Invalid option")
            pause()

# =======================
# 🟢 Entry Point
# =======================
if __name__ == "__main__":
    main_menu()
