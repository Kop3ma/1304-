#!/usr/bin/env python3

# MyApp Manager - Install-App
# Version: 3.0
# Author: KOP3MA

import os
import sys
import shutil
import subprocess
import zipfile
import re
from datetime import datetime

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
WHITE = '\033[1;37m'
NC = '\033[0m'

CONFIG_FILE = os.path.expanduser("~/.myapp_config")

SYSTEM = ""
RC_FILE = ""
BIN_DIR = ""
PYTHON_CMD = ""
PYTHON_VERSION = ""

# OpenWrt Configuration
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
    "gdown"
]

# Detect System
def detect_system():
    global SYSTEM, RC_FILE, BIN_DIR
    if os.path.isdir("/data/data/com.termux") or os.environ.get("PREFIX"):
        SYSTEM = "termux"
        RC_FILE = os.path.expanduser("~/.bashrc")
        BIN_DIR = os.environ.get("PREFIX", "") + "/bin"
    else:
        SYSTEM = "linux"
        RC_FILE = os.path.expanduser("~/.bashrc")
        BIN_DIR = os.path.expanduser("~/.local/bin")

# Detect Python
def detect_python():
    global PYTHON_CMD, PYTHON_VERSION
    
    for cmd in ["python3", "python"]:
        if shutil.which(cmd):
            PYTHON_CMD = cmd
            PYTHON_VERSION = subprocess.getoutput(f"{cmd} --version").split()[1]
            print(f"{GREEN}✅ Python detected: {PYTHON_CMD} {PYTHON_VERSION}{NC}")
            return
    print(f"{RED}❌ Python not found! Installing...{NC}")
    if SYSTEM == "termux":
        os.system("pkg install python -y")
        PYTHON_CMD = "python"
    else:
        os.system("sudo apt install python3 -y")
        PYTHON_CMD = "python3"

# Check Path
def check_path(path):
    if not os.path.isdir(path):
        print(f"{RED}⚠ Warning: Path '{path}' doesn't exist!{NC}")
        create = input(f"{YELLOW}Create it? (y/n): {NC}")
        if create.lower() == "y":
            os.makedirs(path, exist_ok=True)
            print(f"{GREEN}✅ Path created{NC}")
        else:
            return False
    return True

# Utility Functions
def pause():
    input(f"{YELLOW}\nPress Enter to continue...{NC}")

def indented_print(text, prefix="=>>> "):
    print(f"  {prefix}{text}")

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
        print(f"{RED}❌ Command failed: {e}{NC}")
        return False

# Header
def show_header():
    os.system("clear" if shutil.which("clear") else "printf '\033c'")
    print(f"{PURPLE}╔════════════════════════════════════╗{NC}")
    print(f"{PURPLE}║{GREEN}    WELCOME BACK @KOP3MA    {PURPLE}║{NC}")
    print(f"{PURPLE}╠════════════════════════════════════╣{NC}")
    print(f"{PURPLE}║{YELLOW} System:{NC} {SYSTEM:<26}{PURPLE}║{NC}")
    print(f"{PURPLE}║{YELLOW} Python:{NC} {PYTHON_CMD} {PYTHON_VERSION:<18}{PURPLE}║{NC}")
    print(f"{PURPLE}╚════════════════════════════════════╝{NC}")
    print()

# Menu
def show_menu():
    print(f"{CYAN}╔════════════════════════════════════╗{NC}")
    print(f"{CYAN}║{WHITE}           MAIN MENU            {CYAN}║{NC}")
    print(f"{CYAN}╠════════════════════════════════════╣{NC}")
    print(f"{CYAN}║{NC} {GREEN}[1]{NC} ➕ Create new alias        {CYAN}║{NC}")
    print(f"{CYAN}║{NC} {PURPLE}[2]{NC} 👁️ View/Manage Aliases    {CYAN}║{NC}")
    print(f"{CYAN}║{NC} {BLUE}[3]{NC} ⚙️ Settings                {CYAN}║{NC}")
    print(f"{CYAN}║{NC} {GREEN}[4]{NC} 🚀 Run myapp               {CYAN}║{NC}")
    print(f"{CYAN}║{NC} {YELLOW}[5]{NC} 📦 OpenWrt Tools           {CYAN}║{NC}")
    print(f"{CYAN}║{NC} {RED}[6]{NC} ❌ Exit                    {CYAN}║{NC}")
    print(f"{CYAN}╚════════════════════════════════════╝{NC}")
    print()
    return input(f"{GREEN}➤ Choose an option [1-6]: {NC}")

# OpenWrt Menu
def show_openwrt_menu():
    while True:
        show_header()
        print(f"{YELLOW}╔════════════════════════════════════╗{NC}")
        print(f"{YELLOW}║{WHITE}        OPENWRT TOOLS          {YELLOW}║{NC}")
        print(f"{YELLOW}╠════════════════════════════════════╣{NC}")
        print(f"{YELLOW}║{NC} {GREEN}[1]{NC} 📦 Install Python packages   {YELLOW}║{NC}")
        print(f"{YELLOW}║{NC} {BLUE}[2]{NC} 📥 Download from Drive      {YELLOW}║{NC}")
        print(f"{YELLOW}║{NC} {PURPLE}[3]{NC} 🚀 Create init.d service    {YELLOW}║{NC}")
        print(f"{YELLOW}║{NC} {CYAN}[4]{NC} ⚙️ Manage Python service    {YELLOW}║{NC}")
        print(f"{YELLOW}║{NC} {RED}[5]{NC} 🔎 List/Kill processes       {YELLOW}║{NC}")
        print(f"{YELLOW}║{NC} {WHITE}[6]{NC} 🗑️ Remove service           {YELLOW}║{NC}")
        print(f"{YELLOW}║{NC} {RED}[0]{NC} 🔙 Back to Main Menu        {YELLOW}║{NC}")
        print(f"{YELLOW}╚════════════════════════════════════╝{NC}")
        print()
        
        choice = input(f"{GREEN}➤ Select an option [0-6]: {NC}").strip()
        
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
            break
        else:
            print(f"{RED}❌ Invalid option{NC}")
            pause()

# OpenWrt Functions
def install_packages():
    show_header()
    print(f"{BLUE}╔════════════════════════════════════╗{NC}")
    print(f"{BLUE}║{WHITE}    INSTALL PYTHON PACKAGES     {BLUE}║{NC}")
    print(f"{BLUE}╚════════════════════════════════════╝{NC}")
    print()
    
    print(f"{YELLOW}🔄 Running opkg update...{NC}")
    run_command(["opkg", "update"])
    
    for pkg in PYTHON_PACKAGES:
        print(f"{CYAN}📦 Installing {pkg} ...{NC}")
        run_command(["pip3", "install", "--no-cache-dir", "--timeout", "120", "--retries", "10", pkg])
    
    print(f"{GREEN}✅ All packages installed{NC}")
    pause()

def download_project():
    show_header()
    print(f"{BLUE}╔════════════════════════════════════╗{NC}")
    print(f"{BLUE}║{WHITE}    DOWNLOAD FROM GOOGLE DRIVE  {BLUE}║{NC}")
    print(f"{BLUE}╚════════════════════════════════════╝{NC}")
    print()
    
    try:
        import gdown
    except ImportError:
        print(f"{RED}❌ gdown not installed! Run Option 1 first.{NC}")
        pause()
        return
    
    print(f"{YELLOW}📎 Enter Google Drive link or File ID:{NC}")
    print("Example: https://drive.google.com/file/d/ABC123/view")
    print("Or just: ABC123")
    url_input = input(f"{GREEN}> {NC}").strip()
    
    if not url_input:
        print(f"{RED}❌ No input!{NC}")
        pause()
        return
    
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
        print(f"{RED}❌ Could not find File ID{NC}")
        pause()
        return
    
    print(f"{GREEN}✅ File ID: {file_id}{NC}")
    
    current_dir = os.getcwd()
    zip_file = os.path.join(current_dir, "project.zip")
    
    print(f"{CYAN}📂 Downloading to: {current_dir}{NC}")
    print(f"{YELLOW}⏳ Please wait...{NC}")
    
    try:
        gdrive_url = f"https://drive.google.com/uc?id={file_id}"
        downloaded = gdown.download(gdrive_url, output=zip_file, quiet=False)
        
        if not os.path.exists(zip_file):
            print(f"{RED}❌ Download failed!{NC}")
            pause()
            return
        
        file_size = os.path.getsize(zip_file) / (1024*1024)
        print(f"{GREEN}✅ Downloaded: {os.path.basename(zip_file)} ({file_size:.2f} MB){NC}")
        
        print(f"{YELLOW}📁 Where to extract files?{NC}")
        print("Press Enter to extract here")
        extract_path = input(f"{GREEN}Extract to: {NC}").strip()
        
        if not extract_path:
            extract_path = current_dir
        
        if not os.path.exists(extract_path):
            os.makedirs(extract_path, exist_ok=True)
            print(f"{GREEN}📁 Created folder: {extract_path}{NC}")
        
        print(f"{CYAN}🗜 Extracting to: {extract_path}{NC}")
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                file_count = len(zip_ref.namelist())
                zip_ref.extractall(extract_path)
                print(f"{GREEN}✅ Extracted {file_count} files{NC}")
        except Exception as e:
            print(f"{RED}❌ Extract error: {e}{NC}")
        
        print(f"{YELLOW}🗑 Delete the ZIP file?{NC}")
        print("Press Enter for YES, type 'n' for NO")
        delete_choice = input(f"{GREEN}Delete? (Enter=Yes, n=No): {NC}").strip().lower()
        
        if delete_choice == '' or delete_choice == 'y' or delete_choice == 'yes':
            os.remove(zip_file)
            print(f"{GREEN}✅ ZIP file deleted{NC}")
        else:
            print(f"{YELLOW}⚠️ ZIP file kept{NC}")
            
    except Exception as e:
        print(f"{RED}❌ Error: {e}{NC}")
    
    pause()

def create_init_service():
    show_header()
    print(f"{BLUE}╔════════════════════════════════════╗{NC}")
    print(f"{BLUE}║{WHITE}      CREATE INIT.D SERVICE      {BLUE}║{NC}")
    print(f"{BLUE}╚════════════════════════════════════╝{NC}")
    print()
    
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
    print(f"{GREEN}✅ Service created and started!{NC}")
    pause()

def manage_service():
    while True:
        show_header()
        print(f"{CYAN}╔════════════════════════════════════╗{NC}")
        print(f"{CYAN}║{WHITE}       MANAGE PYTHON SERVICE     {CYAN}║{NC}")
        print(f"{CYAN}╠════════════════════════════════════╣{NC}")
        print(f"{CYAN}║{NC} {GREEN}[1]{NC} ▶️  Start service            {CYAN}║{NC}")
        print(f"{CYAN}║{NC} {RED}[2]{NC} ⏹️  Stop service             {CYAN}║{NC}")
        print(f"{CYAN}║{NC} {YELLOW}[3]{NC} 🔄 Restart service          {CYAN}║{NC}")
        print(f"{CYAN}║{NC} {BLUE}[4]{NC} 📊 Show status              {CYAN}║{NC}")
        print(f"{CYAN}║{NC} {RED}[0]{NC} 🔙 Back                    {CYAN}║{NC}")
        print(f"{CYAN}╚════════════════════════════════════╝{NC}")
        print()
        
        choice = input(f"{GREEN}➤ Select an option: {NC}").strip()
        
        if choice == "1":
            run_command([INIT_FILE, "start"])
        elif choice == "2":
            run_command([INIT_FILE, "stop"])
        elif choice == "3":
            run_command([INIT_FILE, "restart"])
        elif choice == "4":
            ret = subprocess.run(["pgrep", "-af", "app.py"], capture_output=True, text=True)
            if ret.stdout.strip():
                print(f"{GREEN}⚙️ Service is running:{NC}")
                print(ret.stdout.strip())
            else:
                print(f"{RED}❌ Service is not running{NC}")
        elif choice == "0":
            break
        pause()

def list_and_kill_processes():
    show_header()
    print(f"{RED}╔════════════════════════════════════╗{NC}")
    print(f"{RED}║{WHITE}     LIST & KILL PROCESSES       {RED}║{NC}")
    print(f"{RED}╚════════════════════════════════════╝{NC}")
    print()
    
    ret = subprocess.run(["pgrep", "-af", "python3"], capture_output=True, text=True)
    lines = [l for l in ret.stdout.strip().split("\n") if l]
    
    if lines:
        for l in lines:
            print(f"{YELLOW}{l}{NC}")
        
        kill_id = input(f"{RED}Enter PID to kill (or press Enter to skip): {NC}").strip()
        if kill_id:
            run_command(["kill", "-9", kill_id])
            print(f"{GREEN}✅ PID {kill_id} killed{NC}")
    else:
        print(f"{YELLOW}❌ No Python processes found{NC}")
    
    pause()

def remove_service():
    show_header()
    print(f"{RED}╔════════════════════════════════════╗{NC}")
    print(f"{RED}║{WHITE}         REMOVE SERVICE          {RED}║{NC}")
    print(f"{RED}╚════════════════════════════════════╝{NC}")
    print()
    
    if os.path.exists(INIT_FILE):
        run_command([INIT_FILE, "stop"])
        run_command([INIT_FILE, "disable"])
        
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
            print(f"{GREEN}🗑 Log file removed{NC}")
        
        os.remove(INIT_FILE)
        print(f"{GREEN}🗑 init.d service file removed{NC}")
    
    print(f"{GREEN}✅ Service cleanup completed{NC}")
    pause()

# Create Alias
def create_alias():
    show_header()
    
    cmd_name = input(f"{YELLOW}▶ Alias name [default: myapp]: {NC}") or "myapp"
    project_path = input(f"{YELLOW}▶ Project path [default: /sdcard/last]: {NC}") or "/sdcard/last"
    
    if not check_path(project_path):
        return
    
    python_file = input(f"{YELLOW}▶ Python file [default: app.py]: {NC}") or "app.py"
    
    if not os.path.isfile(os.path.join(project_path, python_file)):
        print(f"{RED}⚠ Warning: {python_file} not found in {project_path}{NC}")
        if input(f"{YELLOW}Continue anyway? (y/n): {NC}").lower() != "y":
            return
    
    port = input(f"{YELLOW}▶ Port (optional): {NC}")
    extra_args = input(f"{YELLOW}▶ Extra arguments (optional): {NC}")
    
    cmd = f"{PYTHON_CMD} {python_file}"
    if port:
        cmd += f" --port {port}"
    if extra_args:
        cmd += f" {extra_args}"
    
    alias_cmd = f"alias {cmd_name}='cd {project_path} && {cmd}'"
    
    with open(RC_FILE, "a") as f:
        f.write(alias_cmd + "\n")
    
    os.makedirs(BIN_DIR, exist_ok=True)
    script_file = os.path.join(BIN_DIR, cmd_name)
    
    with open(script_file, "w") as f:
        f.write(f"""#!/bin/bash

cd "{project_path}"
{cmd}
""")
    
    os.chmod(script_file, 0o755)
    
    print(f"{GREEN}✅ Alias '{cmd_name}' created successfully!{NC}")
    print(f"{GREEN}✅ Script created at: {script_file}{NC}")
    print(f"{GREEN}✅ Command: {cmd}{NC}")
    
    if input(f"{YELLOW}Run now? (y/n): {NC}").lower() == "y":
        subprocess.call(cmd_name, shell=True)
    
    pause()

# View & Manage Aliases
def view_manage_aliases():
    while True:
        show_header()
        print(f"{CYAN}╔════════════════════════════════════╗{NC}")
        print(f"{CYAN}║{WHITE}       ALL ALIASES IN SYSTEM     {CYAN}║{NC}")
        print(f"{CYAN}╠════════════════════════════════════╣{NC}")
        print(f"{CYAN}║{NC} 📋 Current aliases:{NC}")
        print(f"{CYAN}╚════════════════════════════════════╝{NC}")
        print()
        
        os.system("alias | head -20")
        
        if os.path.isfile(RC_FILE):
            print(f"\n{GREEN}► In {RC_FILE}:{NC}")
            os.system(f"grep -E '^[[:space:]]*alias' {RC_FILE} | head -20")
        
        if os.path.isdir(BIN_DIR):
            print(f"\n{GREEN}► Scripts in {BIN_DIR}:{NC}")
            os.system(f"ls -1 {BIN_DIR}")
        
        print(f"\n{YELLOW}Options:{NC}")
        print(f"{RED}[d NAME]{NC} Delete specific alias")
        print(f"{RED}[da]{NC} Delete ALL aliases")
        print(f"{RED}[b]{NC} Back")
        
        cmd = input(f"{GREEN}➤ Enter command: {NC}")
        
        if cmd.startswith("d "):
            name = cmd.split()[1]
            os.system(f"sed -i '/alias {name}=/d' {RC_FILE}")
            os.system(f"unalias {name} 2>/dev/null")
            
            script_path = os.path.join(BIN_DIR, name)
            if os.path.exists(script_path):
                os.remove(script_path)
            
            print(f"{GREEN}✅ Deleted!{NC}")
        
        elif cmd == "da":
            confirm = input(f"{YELLOW}Type 'DELETE' to confirm: {NC}")
            if confirm == "DELETE":
                backup = RC_FILE + ".backup." + datetime.now().strftime("%Y%m%d_%H%M%S")
                shutil.copy(RC_FILE, backup)
                os.system(f"sed -i '/^[[:space:]]*alias /d' {RC_FILE}")
                os.system("unalias -a 2>/dev/null")
                
                for file in os.listdir(BIN_DIR):
                    os.remove(os.path.join(BIN_DIR, file))
                
                print(f"{GREEN}✅ All aliases deleted!{NC}")
        
        elif cmd == "b":
            break

# Settings
def show_settings():
    show_header()
    print(f"{GREEN}► System Info:{NC}")
    print("OS:", SYSTEM)
    print("Python:", PYTHON_CMD, PYTHON_VERSION)
    print("RC File:", RC_FILE)
    print("Bin Dir:", BIN_DIR)
    print()
    os.system("alias | head -10")
    print("\nPATH:")
    for i, p in enumerate(os.environ["PATH"].split(":"), 1):
        print(i, p)
    pause()

# Run App
def run_app():
    show_header()
    run_cmd = input(f"{YELLOW}▶ Enter command to run: {NC}")
    if run_cmd:
        print(f"{GREEN}Running: {run_cmd}{NC}")
        subprocess.call(run_cmd, shell=True)
    pause()

# Main
detect_system()
detect_python()

while True:
    show_header()
    choice = show_menu()
    
    if choice == "1":
        create_alias()
    elif choice == "2":
        view_manage_aliases()
    elif choice == "3":
        show_settings()
    elif choice == "4":
        run_app()
    elif choice == "5":
        show_openwrt_menu()
    elif choice == "6":
        print(f"{GREEN}Goodbye! 👋{NC}")
        sys.exit(0)
    else:
        print(f"{RED}Invalid option!{NC}")
