#!/usr/bin/env python3

import os
import subprocess
import sys
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
    "urllib3",
    "gdown"  # اضافه شد
]

# =======================
# 🟢 Utility Functions
# =======================
def print_logo():
    print("""
╔══════════════════════════╗
║        WELCOME BACK      ║
║         @KOP3MA          ║
╚══════════════════════════╝

                 K   K   OOO   PPPP   3   M   M   AAA
                 K  K   O   O  P   P  3   MM MM  A   A
                 KKK    O   O  PPPP   3   M M M  AAAAA
                 K  K   O   O  P      3   M   M  A   A
                 K   K   OOO   P     333  M   M  A   A
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
# 🟢 Option 1: Install Python packages
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
# 🟢 Option 2: Download project from Google Drive
# =======================
def download_project():
    print_logo()
    print("="*60)
    print("📥 Download project from Google Drive")
    print("="*60)
    
    # اول چک کنیم gdown نصب هست یا نه
    try:
        import gdown
    except ImportError:
        print("❌ gdown not installed! Run Option 1 first.")
        pause()
        return
    
    # گرفتن لینک
    print("\n📎 Enter Google Drive link or File ID:")
    print("Example: https://drive.google.com/file/d/ABC123/view")
    print("Or just: ABC123")
    url_input = input("> ").strip()
    
    if not url_input:
        print("❌ No input!")
        pause()
        return
    
    # استخراج File ID
    file_id = None
    patterns = [
        r'([a-zA-Z0-9_-]{33})',
        r'/d/([a-zA-Z0-9_-]{33})',
        r'id=([a-zA-Z0-9_-]{33})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_input)
        if match:
            file_id = match.group(1)
            break
    
    if not file_id:
        print("❌ Could not find File ID")
        pause()
        return
    
    print(f"✅ File ID: {file_id}")
    
    # دانلود در مسیر فعلی
    current_dir = os.getcwd()
    zip_file = os.path.join(current_dir, "project.zip")
    
    print(f"\n📂 Downloading to: {current_dir}")
    print("⏳ Please wait...")
    
    try:
        # دانلود با gdown
        gdrive_url = f"https://drive.google.com/uc?id={file_id}"
        downloaded = gdown.download(gdrive_url, output=zip_file, quiet=False)
        
        if not os.path.exists(zip_file):
            print("❌ Download failed!")
            pause()
            return
        
        file_size = os.path.getsize(zip_file) / (1024*1024)
        print(f"✅ Downloaded: {os.path.basename(zip_file)} ({file_size:.2f} MB)")
        
        # سوال برای مسیر اکسترکت
        print("\n📁 Where to extract files?")
        print("Press Enter to extract here")
        extract_path = input("Extract to: ").strip()
        
        if not extract_path:
            extract_path = current_dir  # انتر = همینجا
        
        # ایجاد پوشه اگر لازم باشه
        if not os.path.exists(extract_path):
            os.makedirs(extract_path, exist_ok=True)
            print(f"📁 Created folder: {extract_path}")
        
        # اکسترکت
        print(f"\n🗜 Extracting to: {extract_path}")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                file_count = len(zip_ref.namelist())
                zip_ref.extractall(extract_path)
                print(f"✅ Extracted {file_count} files")
        except Exception as e:
            print(f"❌ Extract error: {e}")
        
        # سوال برای حذف
        print("\n🗑 Delete the ZIP file?")
        print("Press Enter for YES, type 'n' for NO")
        delete_choice = input("Delete? (Enter=Yes, n=No): ").strip().lower()
        
        if delete_choice == '' or delete_choice == 'y' or delete_choice == 'yes':
            os.remove(zip_file)
            print("✅ ZIP file deleted")
        else:
            print("⚠️ ZIP file kept")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
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
        indented_print("1  Install Python packages")
        indented_print("2  Download project from Google Drive")
        indented_print("3  Create init.d service & start")
        indented_print("4  Manage Python service")
        indented_print("5  List & kill Python processes")
        indented_print("6  Remove service / cleanup")
        indented_print("0  Exit")
        choice = input("    Select an option: ").strip()
        if choice == "1":
            install_packages()
        elif choice == "2":
            download_project()
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
