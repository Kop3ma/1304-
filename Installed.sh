#!/bin/bash

# 🚀 MyApp Manager - Install-App
# Version: 2.0
# Author: KOP3MA

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Config file
CONFIG_FILE="$HOME/.myapp_config"

# ==============================================
# هوشمندی: تشخیص خودکار سیستم و پایتون
# ==============================================

detect_system() {
    if [ -d "/data/data/com.termux" ] || [ -n "$PREFIX" ]; then
        SYSTEM="termux"
        RC_FILE="$HOME/.bashrc"
        BIN_DIR="$PREFIX/bin"
    else
        SYSTEM="linux"
        RC_FILE="$HOME/.bashrc"
        BIN_DIR="$HOME/.local/bin"
    fi
}

detect_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    else
        echo -e "${RED}❌ Python not found! Installing...${NC}"
        if [ "$SYSTEM" = "termux" ]; then
            pkg install python -y
            PYTHON_CMD="python"
        else
            sudo apt install python3 -y
            PYTHON_CMD="python3"
        fi
    fi
    echo -e "${GREEN}✅ Python detected: $PYTHON_CMD $PYTHON_VERSION${NC}"
}

check_path() {
    if [ ! -d "$1" ]; then
        echo -e "${RED}⚠ Warning: Path '$1' doesn't exist!${NC}"
        echo -ne "${YELLOW}Create it? (y/n): ${NC}"
        read create
        if [ "$create" = "y" ]; then
            mkdir -p "$1"
            echo -e "${GREEN}✅ Path created${NC}"
        else
            return 1
        fi
    fi
    return 0
}

# ==============================================
# نمایش هدر
# ==============================================

show_header() {
    if command -v clear &> /dev/null; then
        clear
    else
        printf "\033c"
    fi
    echo -e "${BLUE}┌──────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${GREEN}      MyApp Manager v2.0 - KOP3MA     ${BLUE}│${NC}"
    echo -e "${BLUE}├──────────────────────────────────────┤${NC}"
    echo -e "${BLUE}│${YELLOW}  System:${NC} $SYSTEM                      ${BLUE}│${NC}"
    echo -e "${BLUE}│${YELLOW}  Python:${NC} $PYTHON_CMD $PYTHON_VERSION           ${BLUE}│${NC}"
    echo -e "${BLUE}└──────────────────────────────────────┘${NC}"
    echo ""
}

# ==============================================
# منوی اصلی
# ==============================================

show_menu() {
    echo -e "${CYAN}╔════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           MAIN MENU               ║${NC}"
    echo -e "${CYAN}╠════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}  ${GREEN}[1]${NC} ➕ Create new alias        ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${PURPLE}[2]${NC} 👁️  View/Manage Aliases   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}[3]${NC} ⚙️  Settings              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${GREEN}[4]${NC} 🚀 Run myapp              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${RED}[5]${NC} ❌ Exit                    ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════╝${NC}"
    echo ""
    echo -ne "${GREEN}➤ Choose an option [1-5]: ${NC}"
}

# ==============================================
# گزینه ۱: ساخت alias جدید (کامل و هوشمند)
# ==============================================

create_alias() {
    show_header
    echo -e "${BLUE}┌──────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${GREEN}         CREATE NEW ALIAS              ${BLUE}│${NC}"
    echo -e "${BLUE}└──────────────────────────────────────┘${NC}"
    echo ""
    
    # اسم alias
    echo -ne "${YELLOW}▶ Alias name [default: myapp]: ${NC}"
    read CMD_NAME
    CMD_NAME=${CMD_NAME:-myapp}
    
    # مسیر پروژه
    echo -ne "${YELLOW}▶ Project path [default: /sdcard/last]: ${NC}"
    read PROJECT_PATH
    PROJECT_PATH=${PROJECT_PATH:-/sdcard/last}
    
    # بررسی مسیر
    check_path "$PROJECT_PATH"
    
    # فایل پایتون
    echo -ne "${YELLOW}▶ Python file [default: app.py]: ${NC}"
    read PYTHON_FILE
    PYTHON_FILE=${PYTHON_FILE:-app.py}
    
    # بررسی فایل
    if [ ! -f "$PROJECT_PATH/$PYTHON_FILE" ]; then
        echo -e "${RED}⚠ Warning: $PYTHON_FILE not found in $PROJECT_PATH${NC}"
        echo -ne "${YELLOW}Continue anyway? (y/n): ${NC}"
        read continue
        [ "$continue" != "y" ] && return
    fi
    
    # پورت
    echo -ne "${YELLOW}▶ Port (optional, press Enter to skip): ${NC}"
    read PORT
    
    # آرگومان‌های اضافی
    echo -ne "${YELLOW}▶ Extra arguments (optional): ${NC}"
    read EXTRA_ARGS
    
    # ساخت دستور نهایی
    CMD="$PYTHON_CMD $PYTHON_FILE"
    [ -n "$PORT" ] && CMD="$CMD --port $PORT"
    [ -n "$EXTRA_ARGS" ] && CMD="$CMD $EXTRA_ARGS"
    
    # ساخت alias
    alias_cmd="alias $CMD_NAME='cd $PROJECT_PATH && $CMD'"
    
    # اضافه به bashrc
    echo "$alias_cmd" >> "$RC_FILE"
    
    # ساخت اسکریپت
    mkdir -p "$BIN_DIR"
    script_file="$BIN_DIR/$CMD_NAME"
    
    cat > "$script_file" << EOF
#!/bin/bash
cd "$PROJECT_PATH"
$CMD
EOF
    
    chmod +x "$script_file"
    source "$RC_FILE" 2>/dev/null
    
    echo ""
    echo -e "${GREEN}✅ Alias '$CMD_NAME' created successfully!${NC}"
    echo -e "${GREEN}✅ Script created at: $script_file${NC}"
    echo -e "${GREEN}✅ Command: $CMD${NC}"
    echo ""
    
    # پیشنهاد اجرا
    echo -ne "${YELLOW}Run now? (y/n): ${NC}"
    read run_now
    [ "$run_now" = "y" ] && eval "$CMD_NAME"
    
    echo ""
    echo -ne "${YELLOW}Press Enter to continue...${NC}"
    read
}

# ==============================================
# گزینه ۲: مشاهده و مدیریت aliasها
# ==============================================

view_manage_aliases() {
    while true; do
        show_header
        echo -e "${BLUE}┌──────────────────────────────────────┐${NC}"
        echo -e "${BLUE}│${PURPLE}         VIEW & MANAGE ALIASES         ${BLUE}│${NC}"
        echo -e "${BLUE}└──────────────────────────────────────┘${NC}"
        echo ""
        
        # جمع‌آوری همه aliasها
        echo -e "${CYAN}📋 ALL ALIASES IN SYSTEM:${NC}"
        echo "─────────────────────────────────────"
        
        # از جلسه جاری
        if alias &>/dev/null; then
            echo -e "${GREEN}► Current Session:${NC}"
            alias | sed 's/alias //' | nl -w3 -s'. ' | head -20
        fi
        
        # از bashrc
        if [ -f "$RC_FILE" ]; then
            echo ""
            echo -e "${GREEN}► In $RC_FILE:${NC}"
            grep -E "^[[:space:]]*alias" "$RC_FILE" | sed 's/alias //' | nl -w3 -s'. ' | head -20
        fi
        
        # از bin directory
        if [ -d "$BIN_DIR" ]; then
            echo ""
            echo -e "${GREEN}► Scripts in $BIN_DIR:${NC}"
            ls -1 "$BIN_DIR" 2>/dev/null | nl -w3 -s'. '
        fi
        
        echo ""
        echo "─────────────────────────────────────"
        echo -e "${YELLOW}Options:${NC}"
        echo -e "  ${RED}[d NAME]${NC} Delete specific alias (e.g., d myapp)"
        echo -e "  ${RED}[da]${NC}    Delete ALL aliases"
        echo -e "  ${RED}[b]${NC}     Back to main menu"
        echo ""
        echo -ne "${GREEN}➤ Enter command: ${NC}"
        read cmd
        
        case $cmd in
            d*)
                name=$(echo "$cmd" | cut -d' ' -f2)
                if [ -n "$name" ]; then
                    echo -e "${YELLOW}Deleting '$name'...${NC}"
                    # از bashrc
                    sed -i "/alias $name=/d" "$RC_FILE"
                    # از جلسه جاری
                    unalias "$name" 2>/dev/null
                    # از bin
                    rm -f "$BIN_DIR/$name" 2>/dev/null
                    echo -e "${GREEN}✅ Deleted!${NC}"
                fi
                sleep 1
                ;;
            da)
                echo ""
                echo -e "${RED}╔════════════════════════════════╗${NC}"
                echo -e "${RED}║  DELETE ALL ALIASES?          ║${NC}"
                echo -e "${RED}╚════════════════════════════════╝${NC}"
                echo -ne "${YELLOW}Type 'DELETE' to confirm: ${NC}"
                read confirm
                if [ "$confirm" = "DELETE" ]; then
                    # پشتیبان‌گیری
                    cp "$RC_FILE" "$RC_FILE.backup.$(date +%Y%m%d_%H%M%S)"
                    # پاک کردن همه aliasها از bashrc
                    sed -i '/^[[:space:]]*alias /d' "$RC_FILE"
                    # پاک کردن از جلسه جاری
                    unalias -a 2>/dev/null
                    # پاک کردن همه اسکریپت‌ها
                    rm -f "$BIN_DIR"/* 2>/dev/null
                    echo -e "${GREEN}✅ All aliases deleted!${NC}"
                fi
                sleep 2
                ;;
            b)
                break
                ;;
        esac
    done
}

# ==============================================
# گزینه ۳: تنظیمات
# ==============================================

show_settings() {
    show_header
    echo -e "${BLUE}┌──────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${CYAN}            SETTINGS                   ${BLUE}│${NC}"
    echo -e "${BLUE}└──────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${GREEN}► System Info:${NC}"
    echo "  OS: $SYSTEM"
    echo "  Python: $PYTHON_CMD $PYTHON_VERSION"
    echo "  RC File: $RC_FILE"
    echo "  Bin Dir: $BIN_DIR"
    echo ""
    
    echo -e "${GREEN}► Active Aliases:${NC}"
    alias | head -10
    echo ""
    
    echo -e "${GREEN}► PATH:${NC}"
    echo "$PATH" | tr ':' '\n' | nl
    echo ""
    
    echo -ne "${YELLOW}Press Enter to continue...${NC}"
    read
}

# ==============================================
# اجرای برنامه
# ==============================================

run_app() {
    show_header
    echo -e "${BLUE}┌──────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${GREEN}            RUN MYAPP                  ${BLUE}│${NC}"
    echo -e "${BLUE}└──────────────────────────────────────┘${NC}"
    echo ""
    
    echo -ne "${YELLOW}▶ Enter command to run: ${NC}"
    read run_cmd
    
    if [ -n "$run_cmd" ]; then
        echo ""
        echo -e "${GREEN}Running: $run_cmd${NC}"
        echo "────────────────────────────────"
        eval "$run_cmd"
    fi
    
    echo ""
    echo -ne "${YELLOW}Press Enter to continue...${NC}"
    read
}

# ==============================================
# برنامه اصلی
# ==============================================

# تشخیص اولیه
detect_system
detect_python

# حلقه اصلی
while true; do
    show_header
    show_menu
    read choice
    
    case $choice in
        1) create_alias ;;
        2) view_manage_aliases ;;
        3) show_settings ;;
        4) run_app ;;
        5) 
            echo -e "${GREEN}Goodbye! 👋${NC}"
            exit 0 
            ;;
        *)
            echo -e "${RED}Invalid option!${NC}"
            sleep 1
            ;;
    esac
done
