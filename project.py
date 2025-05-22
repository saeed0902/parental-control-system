import streamlit as st
import platform
import os
import shutil
import datetime
import time
import subprocess
import psutil
import hashlib
import sqlite3
import re
import uuid

# --- Database Setup for Authentication ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  email TEXT UNIQUE)''')
    # Add default admin if not exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                 ('admin', hashed_password, 'admin@parentalcontrol.com'))
    conn.commit()
    conn.close()

init_db()

# --- Authentication Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def register_user(username, password, email):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                 (username, hash_password(password), email))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        st.error("Username or email already exists")
        return False

def reset_password(email, new_password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", 
             (hash_password(new_password), email))
    if c.rowcount > 0:
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

# --- Custom CSS for Modern UI ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* Main Container */
        .main {
            background: radial-gradient(circle at center, #1e3a8a 0%, #06b6d4 100%);
            padding: 2rem;
            min-height: 100vh;
            background-size: cover;
            background-attachment: fixed;
        }
        
        /* Auth Pages */
        .auth-container {
            max-width: 450px;
            padding: 2.5rem;
            margin: 2rem auto;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            border-radius: 20px;
            background: #ffffff;
            transition: transform 0.3s ease;
        }
        .auth-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.35);
        }
        .auth-title {
            text-align: center;
            color: #1e3a8a;
            margin-bottom: 2rem;
            font-size: 2rem;
            font-weight: 600;
        }
        
        /* Cards */
        .custom-card {
            padding: 2rem;
            background: linear-gradient(145deg, #ffffff, #f0f4f8);
            border-radius: 16px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2), 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            transition: all 0.3s ease;
            border: 1px solid rgba(200, 200, 200, 0.2);
        }
        .custom-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 6px 12px rgba(0,0,0,0.15);
            background: linear-gradient(145deg, #f8fafc, #e8eef4);
        }
        .custom-card h1, .custom-card h2, .custom-card h3 {
            color: #1e3a8a;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .custom-card p, .custom-card div {
            color: #1f2937;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #1e3a8a 0%, #06b6d4 100%) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
            background: linear-gradient(90deg, #3b82f6 0%, #22d3ee 100%) !important;
        }
        .primary-btn {
            background: linear-gradient(90deg, #1e3a8a 0%, #06b6d4 100%) !important;
        }
        
        /* Progress Bar */
        .stProgress>div>div>div {
            background: linear-gradient(90deg, #1e3a8a 0%, #06b6d4 100%);
            border-radius: 8px;
        }
        
        /* Tabs */
        .stTabs>div>div>button {
            border-radius: 12px !important;
            margin: 0 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            color: #f3f4f6 !important;
            background: rgba(255,255,255,0.1) !important;
            transition: all 0.3s ease !important;
        }
        .stTabs>div>div>button:hover {
            background: rgba(255,255,255,0.2) !important;
            color: #ffffff !important;
        }
        .stTabs>div>div>button[data-baseweb="tab-highlight"] {
            background: #06b6d4 !important;
            color: #ffffff !important;
        }
        
        /* Status Indicators */
        .status-running {
            color: #22d3ee;
            font-weight: 600;
            font-size: 1.2rem;
        }
        .status-stopped {
            color: #f87171;
            font-weight: 600;
            font-size: 1.2rem;
        }
        
        /* Input Fields */
        .stTextInput>div>div>input {
            border-radius: 10px !important;
            padding: 12px !important;
            border: 1px solid #d1d8e0 !important;
            background: #f8fafc !important;
            color: #1f2937 !important;
        }
        .stTextInput>div>div>input:focus {
            border-color: #06b6d4 !important;
            box-shadow: 0 0 8px rgba(6, 182, 212, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Parental Control System Functions ---
REDIRECT_IP = "127.0.0.1"
HOSTS_MARKER = "# Added by ParentalControlApp v2.0"
BACKUP_FOLDER_NAME = ".parental_control_backups"

def get_hosts_path():
    if platform.system() == "Windows":
        system_root = os.environ.get('SYSTEMROOT', 'C:\\Windows')
        return os.path.join(system_root, 'System32', 'drivers', 'etc', 'hosts')
    else:
        return "/etc/hosts"

def get_backup_dir():
    home_dir = os.path.expanduser("~")
    backup_dir = os.path.join(home_dir, BACKUP_FOLDER_NAME)
    try:
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    except OSError as e:
        st.error(f"❌ Error creating backup directory: {e}")
        return None

def check_admin_rights():
    try:
        if platform.system() == "Windows":
            test_path = os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'System32', 'config')
            os.listdir(test_path)
            return True
        else:
            return os.geteuid() == 0
    except (PermissionError, OSError):
        return False
    except Exception:
        return False

def backup_hosts(hosts_path):
    backup_dir = get_backup_dir()
    if not backup_dir: return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"hosts.backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_filename)
    try:
        shutil.copy2(hosts_path, backup_path)
        st.toast(f"✅ Backup created: {os.path.basename(backup_path)}")
        return backup_path
    except Exception as e:
        st.error(f"❌ Backup Error: {e}")
        return None

def restore_hosts(hosts_path, backup_path):
    if not backup_path or not os.path.exists(backup_path):
        st.error("❌ Restore Error: Backup file not found.")
        return False
    try:
        shutil.copy2(backup_path, hosts_path)
        st.toast("✅ Hosts file restored from backup.")
        return True
    except Exception as e:
        st.error(f"❌ Restore Error: {e}")
        return False

def remove_marked_entries(hosts_path):
    if not os.path.exists(hosts_path):
        st.error(f"❌ Hosts file not found!")
        return False

    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        original_lines_count = len(lines)
        filtered_lines = [line for line in lines if HOSTS_MARKER not in line]

        if len(filtered_lines) < original_lines_count:
            cleaned_lines = [line.rstrip() for line in filtered_lines if line.strip()]
            with open(hosts_path, 'w', encoding='utf-8') as f:
                 f.write("\n".join(cleaned_lines) + "\n")
            st.toast("✅ Marked entries removed.")
        else:
            st.info("ℹ No application-specific entries found to remove.")

        return True
    except Exception as e:
        st.error(f"❌ Error removing entries: {e}")
        return False

def block_sites(hosts_path, sites_to_block):
    if not sites_to_block:
        st.warning("⚠ No sites specified to block.")
        return True

    blocked_count = 0
    lines_to_add_final = []
    try:
        existing_lines = set()
        if os.path.exists(hosts_path):
             try:
                with open(hosts_path, 'r', encoding='utf-8-sig') as f:
                    existing_lines = set(line.strip() for line in f)
             except Exception as e:
                 st.warning(f"⚠ Could not read existing hosts file: {e}")

        for site in sites_to_block:
            site = site.strip().lower().replace('http://', '').replace('https://', '')
            if site and '/' not in site and '.' in site:
                entry_base = f"{REDIRECT_IP}\t{site}\t{HOSTS_MARKER}"
                entry_www = f"{REDIRECT_IP}\twww.{site}\t{HOSTS_MARKER}"

                is_new = False
                if entry_base not in existing_lines:
                    lines_to_add_final.append(entry_base)
                    is_new = True
                if entry_www not in existing_lines:
                    lines_to_add_final.append(entry_www)
                    is_new = True

                if is_new:
                     blocked_count += 1
            elif site:
                 st.warning(f"⚠ Skipping invalid entry: '{site}'")

        if not lines_to_add_final:
            if sites_to_block:
                 st.info("ℹ All specified valid sites are already blocked.")
            return True

        all_lines = []
        if os.path.exists(hosts_path):
             try:
                with open(hosts_path, 'r', encoding='utf-8-sig') as f:
                    all_lines = f.readlines()
             except Exception as e:
                  st.error(f"❌ Failed to read hosts file: {e}")
                  return False

        if all_lines and not all_lines[-1].endswith('\n'):
            all_lines.append('\n')
        elif not all_lines:
             all_lines.append('\n')

        for line in lines_to_add_final:
             all_lines.append(line + '\n')

        with open(hosts_path, 'w', encoding='utf-8') as f:
             f.writelines(all_lines)

        st.success(f"✅ Added {blocked_count} new site(s) to block list.")
        return True

    except Exception as e:
        st.error(f"❌ Error blocking sites: {e}")
        return False

def allow_sites(hosts_path, sites_to_allow, block_all=True):
    if not sites_to_allow:
        st.warning("⚠ No sites specified to allow.")
        return True

    allowed_count = 0
    try:
        existing_lines = set()
        if os.path.exists(hosts_path):
             try:
                with open(hosts_path, 'r', encoding='utf-8-sig') as f:
                    existing_lines = set(line.strip() for line in f)
             except Exception as e:
                 st.warning(f"⚠ Could not read existing hosts file: {e}")

        common_domains_to_block = [
            "facebook.com", "instagram.com", "twitter.com", "tiktok.com", 
            "youtube.com", "reddit.com", "netflix.com", "amazon.com",
            "ebay.com", "pinterest.com", "snapchat.com", "twitch.tv",
            "discord.com", "roblox.com", "tumblr.com", "quora.com",
            "imgur.com", "dailymotion.com", "vimeo.com", "linkedin.com"
        ]
        
        domains_to_block = []
        
        if block_all:
            tlds = [".com", ".org", ".net", ".io", ".co", ".edu"]
            domains_to_block = [f"*{tld}" for tld in tlds]
            domains_to_block.extend(common_domains_to_block)
        else:
            domains_to_block = common_domains_to_block
        
        for allowed_site in sites_to_allow:
            allowed_site = allowed_site.strip().lower()
            if allowed_site:
                domains_to_block = [domain for domain in domains_to_block 
                                   if not domain.endswith(allowed_site) and domain != allowed_site]
        
        lines_to_add_final = []
        
        for site in domains_to_block:
            site = site.strip().lower().replace('http://', '').replace('https://', '')
            if site and '.' in site:
                entry_base = f"{REDIRECT_IP}\t{site}\t{HOSTS_MARKER}"
                entry_www = f"{REDIRECT_IP}\twww.{site}\t{HOSTS_MARKER}"

                is_new = False
                if entry_base not in existing_lines:
                    lines_to_add_final.append(entry_base)
                    is_new = True
                if entry_www not in existing_lines:
                    lines_to_add_final.append(entry_www)
                    is_new = True

                if is_new:
                     allowed_count += 1

        if not lines_to_add_final:
            st.info("ℹ No new sites to block in allow mode.")
            return True

        all_lines = []
        if os.path.exists(hosts_path):
             try:
                with open(hosts_path, 'r', encoding='utf-8-sig') as f:
                    all_lines = f.readlines()
             except Exception as e:
                  st.error(f"❌ Failed to read hosts file: {e}")
                  return False

        if all_lines and not all_lines[-1].endswith('\n'):
            all_lines.append('\n')
        elif not all_lines:
             all_lines.append('\n')

        for line in lines_to_add_final:
             all_lines.append(line + '\n')

        with open(hosts_path, 'w', encoding='utf-8') as f:
             f.writelines(all_lines)

        st.success(f"✅ Allowing only {len(sites_to_allow)} site(s), blocking all others.")
        return True

    except Exception as e:
        st.error(f"❌ Error in allow mode: {e}")
        return False

def flush_dns():
    system = platform.system()
    command = ""
    message = "Attempting DNS Flush..."
    success = False
    manual_action = ""

    try:
        if system == "Windows":
            command = ["ipconfig", "/flushdns"]
            result = subprocess.run(command, capture_output=True, text=True, check=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            if "Successfully flushed" in result.stdout:
                 success = True
                 message = "✅ Windows DNS Cache Flushed!"
            else:
                 message = f"⚠ Windows DNS flush command ran, but output unexpected"

        elif system == "Darwin":
            manual_action = "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
            message = "⚠ On macOS, please run DNS flush manually in Terminal."
            success = True

        elif system == "Linux":
             manual_action = ("sudo systemd-resolve --flush-caches\n"
                             "sudo resolvectl flush-caches\n"
                             "sudo /etc/init.d/nscd restart\n"
                             "sudo /etc/init.d/dnsmasq restart")
             message = "⚠ On Linux, please run appropriate DNS flush command manually."
             success = True

        else:
             message = f"ℹ DNS flush command not known for system: {system}"
             success = True

    except Exception as e:
        message = f"❌ Error during DNS flush: {e}"

    st.toast(message)
    if manual_action:
        st.info(f"Manual DNS Flush command for {system}:\n\n{manual_action}\n")
    return success

# --- Authentication Pages ---
def login_page():
    inject_custom_css()
    with st.container():
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z" fill="#1e3a8a"/>
                <path d="M12 11C13.66 11 15 9.66 15 8V5C15 3.34 13.66 2 12 2C10.34 2 9 3.34 9 5V8C9 9.66 10.34 11 12 11Z" fill="#06b6d4"/>
                <path d="M12 11C13.1 11 14 10.1 14 9V5C14 3.9 13.1 3 12 3C10.9 3 10 3.9 10 5V9C10 10.1 10.9 11 12 11Z" fill="#ffffff" opacity="0.8"/>
            </svg>
            <h2 class='auth-title'>Parental Control Pro</h2>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Login", key="login_btn"):
            if validate_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Forgot Password?", key="forgot_btn"):
                st.session_state.show_forgot = True
                st.rerun()
        with col2:
            if st.button("Create Account", key="register_btn"):
                st.session_state.show_register = True
                st.rerun()

def register_page():
    inject_custom_css()
    with st.container():
        st.markdown("<h2 class='auth-title'>📝 Create Account</h2>", unsafe_allow_html=True)
        
        email = st.text_input("Email")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        
        if st.button("Register", key="register_submit"):
            if new_password != confirm_password:
                st.error("Passwords don't match")
            elif not validate_email(email):
                st.error("Invalid email format")
            elif register_user(new_username, new_password, email):
                st.success("Registration successful! Please login")
                st.session_state.show_register = False
                st.rerun()
        
        if st.button("Back to Login", key="back_to_login"):
            st.session_state.show_register = False
            st.rerun()

def forgot_password_page():
    inject_custom_css()
    with st.container():
        st.markdown("<h2 class='auth-title'>🔑 Reset Password</h2>", unsafe_allow_html=True)
        
        email = st.text_input("Registered Email")
        new_password = st.text_input("New Password", type='password')
        
        if st.button("Reset Password", key="reset_pass"):
            if reset_password(email, new_password):
                st.success("Password updated successfully!")
                st.session_state.show_forgot = False
                st.rerun()
            else:
                st.error("Email not found")
        
        if st.button("Back to Login", key="forgot_back"):
            st.session_state.show_forgot = False
            st.rerun()

# --- Main App UI ---
def main_app():
    inject_custom_css()

    # Header with Logout
    col1, col2 = st.columns([4,1])
    with col1:
        st.title("🛡 Parental Control Pro")
        st.caption(f"Logged in as: {st.session_state.username}")
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()

    # Check Admin Rights
    if 'admin_rights_checked' not in st.session_state:
        with st.spinner("Checking permissions..."):
            st.session_state.has_admin = check_admin_rights()
            st.session_state.admin_rights_checked = True

    if not st.session_state.has_admin:
        st.error("🚨 *Administrator privileges are required!*")
        st.warning("Please run this app with admin rights (Windows) or using sudo (Mac/Linux).")
        st.stop()

    # Initialize Session State
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'duration_seconds' not in st.session_state:
        st.session_state.duration_seconds = 3600
    if 'backup_file_path' not in st.session_state:
        st.session_state.backup_file_path = None
    if 'sites_to_block' not in st.session_state:
        st.session_state.sites_to_block = ["facebook.com", "instagram.com", "twitter.com", "tiktok.com", "youtube.com", "www.youtube.com", "reddit.com"]
    if 'error_message' not in st.session_state:
         st.session_state.error_message = ""
    if 'last_duration_minutes' not in st.session_state:
         st.session_state.last_duration_minutes = 60
    if 'allowed_mode' not in st.session_state:
        st.session_state.allowed_mode = False
    if 'allowed_sites' not in st.session_state:
        st.session_state.allowed_sites = ["google.com", "wikipedia.org", "khan-academy.org"]
    if 'block_all_except_allowed' not in st.session_state:
        st.session_state.block_all_except_allowed = True

    # Main App Layout with Tabs
    tab_control, tab_settings, tab_info = st.tabs([
        "🚦 Control Panel",
        "⚙ Settings & Website Lists",
        "ℹ Info & Help"
    ])

    # Tab 1: Control Panel
    with tab_control:
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.header("Current Status")

            if st.session_state.running:
                elapsed_time = time.time() - st.session_state.start_time
                remaining_time = st.session_state.duration_seconds - elapsed_time

                if remaining_time > 0:
                    st.markdown("<p class='status-running'>Status: Running 🟢</p>", unsafe_allow_html=True)
                    minutes, seconds = divmod(remaining_time, 60)
                    st.metric(label="⏳ Time Remaining", value=f"{int(minutes)} min {int(seconds)} sec")
                    progress = max(0.0, min(1.0, elapsed_time / st.session_state.duration_seconds))
                    st.progress(progress)
                    
                    if st.session_state.allowed_mode:
                        st.info(f"🔓 *Allow Mode*: Only {len(st.session_state.allowed_sites)} sites allowed until timer ends")
                    else:
                        st.info(f"🔒 *Block Mode*: {len(st.session_state.sites_to_block)} sites blocked until timer ends")

                    time.sleep(5)
                    st.rerun()

                else:
                    st.warning("⏰ Time limit reached! Automatically stopping control...")
                    hosts_file = get_hosts_path()
                    restore_success = False
                    with st.spinner("Automatically removing modified entries..."):
                        restore_success = remove_marked_entries(hosts_file)
                        if restore_success:
                             with st.spinner("Flushing DNS Cache..."):
                                 flush_dns()

                    if restore_success:
                        st.success("✅ Control stopped automatically.")
                        st.balloons()
                    else:
                        st.error("❌ Failed to automatically stop control!")
                        if st.session_state.backup_file_path:
                             st.info(f"ℹ Last known backup file: {st.session_state.backup_file_path}")
                        st.session_state.error_message = "Time limit reached, but auto-restore failed."

                    st.session_state.running = False
                    st.session_state.start_time = None
                    st.session_state.duration_seconds = st.session_state.last_duration_minutes * 60

                    time.sleep(3)
                    st.rerun()

            else:
                st.markdown("<p class='status-stopped'>Status: Stopped 🔴</p>", unsafe_allow_html=True)
                
                if st.session_state.allowed_mode:
                    st.write("Current Mode: *Allow Mode* 🔓")
                    st.write(f"Will allow {len(st.session_state.allowed_sites)} specified sites for the set duration.")
                else:
                    st.write("Current Mode: *Block Mode* 🔒") 
                    st.write(f"Will block {len(st.session_state.sites_to_block)} specified sites for the set duration.")
                    
                st.write("Configure settings in the 'Settings & Website Lists' tab and click 'Start Control'.")
                if st.session_state.error_message:
                     st.error(f"🚨 Last Error: {st.session_state.error_message}")
                st.caption(f"Last set duration was {st.session_state.last_duration_minutes} minutes.")
            
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.subheader("Actions")
            col1, col2 = st.columns(2)

            with col1:
                button_text = "🚀 Start Control" if not st.session_state.running else "Running..."
                if st.button(button_text, disabled=st.session_state.running, type="primary", key="start_control"):
                    st.session_state.error_message = ""
                    hosts_file = get_hosts_path()

                    current_duration_minutes = st.session_state.last_duration_minutes

                    if st.session_state.allowed_mode:
                        current_sites_list = st.session_state.allowed_sites
                        block_all = st.session_state.block_all_except_allowed
                        
                        if not current_sites_list:
                            st.warning("⚠ Please enter at least one valid domain to allow in the Settings tab.")
                            st.session_state.error_message = "No domains entered for allow mode."
                        elif not hosts_file:
                            st.error("❌ Cannot find hosts file path.")
                            st.session_state.error_message = "Hosts file path not found."
                        else:
                            st.info(f"ℹ Using hosts file: {hosts_file}")
                            backup_success = False
                            with st.spinner("Creating backup..."):
                                backup_path = backup_hosts(hosts_file)
                                if backup_path:
                                    st.session_state.backup_file_path = backup_path
                                    backup_success = True

                            if backup_success:
                                allow_success = False
                                with st.spinner(f"Setting up allow mode for {len(current_sites_list)} site(s)..."):
                                    allow_success = allow_sites(hosts_file, current_sites_list, block_all)
                                
                                if allow_success:
                                    with st.spinner("Flushing DNS Cache..."):
                                        flush_dns()

                                    st.session_state.start_time = time.time()
                                    st.session_state.duration_seconds = current_duration_minutes * 60
                                    st.session_state.running = True
                                    st.success(f"✅ Allow mode started for {current_duration_minutes} minutes!")
                                    st.balloons()
                                    time.sleep(1.5)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to modify hosts file for allowing. Attempting restore...")
                                    st.session_state.error_message = "Failed to set up allow mode."
                                    if st.session_state.backup_file_path:
                                        with st.spinner("Restoring from backup..."):
                                            restore_hosts(hosts_file, st.session_state.backup_file_path)
                            else:
                                st.error("❌ Cannot start allow mode without a successful backup.")
                                st.session_state.error_message = "Backup creation failed."
                    else:
                        current_sites_list = st.session_state.sites_to_block
                        
                        if not current_sites_list:
                            st.warning("⚠ Please enter at least one valid domain to block in the Settings tab.")
                            st.session_state.error_message = "No domains entered."
                        elif not hosts_file:
                             st.error("❌ Cannot find hosts file path.")
                             st.session_state.error_message = "Hosts file path not found."
                        else:
                             st.info(f"ℹ Using hosts file: {hosts_file}")
                             backup_success = False
                             with st.spinner("Creating backup..."):
                                  backup_path = backup_hosts(hosts_file)
                                  if backup_path:
                                       st.session_state.backup_file_path = backup_path
                                       backup_success = True

                             if backup_success:
                                  block_success = False
                                  with st.spinner(f"Blocking {len(current_sites_list)} site(s)..."):
                                       block_success = block_sites(hosts_file, current_sites_list)

                                  if block_success:
                                       with st.spinner("Flushing DNS Cache..."):
                                           flush_dns()

                                       st.session_state.start_time = time.time()
                                       st.session_state.duration_seconds = current_duration_minutes * 60
                                       st.session_state.running = True
                                       st.success(f"✅ Blocking started for {current_duration_minutes} minutes!")
                                       st.balloons()
                                       time.sleep(1.5)
                                       st.rerun()
                                  else:
                                       st.error("❌ Failed to modify hosts file for blocking. Attempting restore...")
                                       st.session_state.error_message = "Failed to block sites."
                                       if st.session_state.backup_file_path:
                                            with st.spinner("Restoring from backup..."):
                                                 restore_hosts(hosts_file, st.session_state.backup_file_path)
                             else:
                                  st.error("❌ Cannot start blocking without a successful backup.")
                                  st.session_state.error_message = "Backup creation failed."

            with col2:
                button_text = "⏹ Stop Control" if st.session_state.running else "Not Running"
                if st.button(button_text, disabled=not st.session_state.running, key="stop_control"):
                    st.session_state.error_message = ""
                    st.warning("⏳ Stopping the control process...")
                    hosts_file = get_hosts_path()
                    restore_success = False

                    with st.spinner("Removing modified entries..."):
                         restore_success = remove_marked_entries(hosts_file)
                         if restore_success:
                              with st.spinner("Flushing DNS Cache..."):
                                 flush_dns()

                    if restore_success:
                        st.session_state.running = False
                        st.session_state.start_time = None
                        st.session_state.duration_seconds = st.session_state.last_duration_minutes * 60
                        st.success("✅ Control stopped successfully.")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("❌ Failed to stop control properly. Hosts file might need manual cleanup!")
                        if st.session_state.backup_file_path:
                             st.info(f"ℹ Last known backup file: {st.session_state.backup_file_path}")
                        st.session_state.error_message = "Failed to stop control properly."
            
            st.markdown("</div>", unsafe_allow_html=True)

    # Tab 2: Settings & Website Lists
    with tab_settings:
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.header("⚙ Settings")
            
            st.subheader("Mode Selection")
            mode_col1, mode_col2 = st.columns(2)
            
            with mode_col1:
                if st.toggle("Enable Allow Mode", 
                            value=st.session_state.allowed_mode,
                            disabled=st.session_state.running,
                            key="allow_mode_toggle"):
                    st.session_state.allowed_mode = True
                else:
                    st.session_state.allowed_mode = False
            
            with mode_col2:
                if st.session_state.allowed_mode:
                    if st.toggle("Block everything except allowed sites", 
                               value=st.session_state.block_all_except_allowed,
                               disabled=st.session_state.running,
                               key="block_all_toggle"):
                        st.session_state.block_all_except_allowed = True
                    else:
                        st.session_state.block_all_except_allowed = False
            
            st.subheader("Control Duration")
            
            duration_options = {
                "15 minutes": 15,
                "30 minutes": 30,
                "1 hour": 60,
                "1.5 hours": 90,
                "2 hours": 120,
                "3 hours": 180,
                "4 hours": 240
            }
            
            duration_col1, duration_col2 = st.columns([3, 2])
            
            with duration_col1:
                duration_key = st.selectbox(
                    "Select duration:",
                    options=list(duration_options.keys()),
                    index=list(duration_options.values()).index(st.session_state.last_duration_minutes) if st.session_state.last_duration_minutes in duration_options.values() else 2,
                    disabled=st.session_state.running,
                    key="duration_select"
                )
                if not st.session_state.running and duration_key in duration_options:
                    st.session_state.last_duration_minutes = duration_options[duration_key]
                    st.session_state.duration_seconds = st.session_state.last_duration_minutes * 60
            
            with duration_col2:
                custom_minutes = st.number_input(
                    "Or custom (minutes):",
                    min_value=1,
                    max_value=480,
                    value=st.session_state.last_duration_minutes if st.session_state.last_duration_minutes not in duration_options.values() else 60,
                    step=5,
                    disabled=st.session_state.running,
                    key="custom_duration"
                )
                if not st.session_state.running and custom_minutes > 0:
                    st.session_state.last_duration_minutes = int(custom_minutes)
                    st.session_state.duration_seconds = st.session_state.last_duration_minutes * 60
            
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            if st.session_state.allowed_mode:
                st.subheader("🔓 Allowed Websites")
                st.caption("Enter the domains you want to allow during the control period. One domain per line.")
                
                sites_text = st.text_area(
                    "Domains to Allow (one per line):",
                    value="\n".join(st.session_state.allowed_sites),
                    height=200,
                    disabled=st.session_state.running,
                    key="allowed_sites_area"
                )
                
                if not st.session_state.running:
                    sites_list = [site.strip() for site in sites_text.split('\n') if site.strip()]
                    st.session_state.allowed_sites = sites_list
                
                if st.button("➕ Add Common Educational Sites", disabled=st.session_state.running, key="add_educational"):
                    educational_sites = [
                        "google.com", "wikipedia.org", "khanacademy.org", "britannica.com",
                        "edx.org", "coursera.org", "udemy.com", "scholastic.com",
                        "nationalgeographic.com", "nasa.gov", "pbs.org", "howstuffworks.com"
                    ]
                    
                    current_sites = set(st.session_state.allowed_sites)
                    for site in educational_sites:
                        if site not in current_sites:
                            st.session_state.allowed_sites.append(site)
                    
                    st.success(f"✅ Added educational sites to the allowed list.")
                    time.sleep(1)
                    st.rerun()
            
            else:
                st.subheader("🔒 Blocked Websites")
                st.caption("Enter the domains you want to block during the control period. One domain per line.")
                
                sites_text = st.text_area(
                    "Domains to Block (one per line):",
                    value="\n".join(st.session_state.sites_to_block),
                    height=200,
                    disabled=st.session_state.running,
                    key="blocked_sites_area"
                )
                
                if not st.session_state.running:
                    sites_list = [site.strip() for site in sites_text.split('\n') if site.strip()]
                    st.session_state.sites_to_block = sites_list
                
                if st.button("➕ Add Common Social Media", disabled=st.session_state.running, key="add_social"):
                    social_sites = [
                        "facebook.com", "instagram.com", "twitter.com", "tiktok.com", 
                        "youtube.com", "reddit.com", "snapchat.com", "tumblr.com",
                        "pinterest.com", "discord.com", "twitch.tv"
                    ]
                    
                    current_sites = set(st.session_state.sites_to_block)
                    for site in social_sites:
                        if site not in current_sites:
                            st.session_state.sites_to_block.append(site)
                    
                    st.success(f"✅ Added social media sites to the block list.")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    # Tab 3: Info & Help
    with tab_info:
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.header("ℹ Application Info & Help")
            
            st.subheader("About this Application")
            st.markdown("""
            *Parental Control Pro* is an advanced application that uses the system's hosts file 
            to temporarily block or allow access to specified websites with a professional interface.
            
            *Key Features*:
            - 🔒 Secure login system with user accounts
            - ⏱ Timer-based control with automatic restoration
            - 🔄 Two modes: Block specific sites or Allow only specific sites
            - 💾 Automatic backups and easy restoration
            - 🎨 Modern, professional user interface
            """)
            
            st.subheader("How It Works")
            st.markdown("""
            1. *Authentication*: Secure login system protects access to controls
            2. *Hosts File*: Temporarily modifies system hosts file to redirect domains
            3. *Backup*: Creates automatic backups before any changes
            4. *Timer*: Runs for specified duration then auto-restores
            5. *DNS Cache*: Attempts to flush DNS for immediate effect
            """)
            
            st.subheader("Frequently Asked Questions")
            
            with st.expander("Why do I need admin rights?"):
                st.markdown("""
                The hosts file is a protected system file. Modifying it requires:
                - *Windows*: Run as Administrator
                - *Mac/Linux*: Use sudo
                """)
            
            with st.expander("Changes not taking effect?"):
                st.markdown("""
                1. Try closing and reopening your browser
                2. Flush DNS cache manually if needed
                3. Restart your computer in rare cases
                """)
            
            with st.expander("Will this affect all users?"):
                st.markdown("""
                Yes, the hosts file is system-wide so changes affect all users and browsers.
                """)
            
            with st.expander("What if the app crashes?"):
                st.markdown("""
                Don't worry! The app:
                1. Creates backups automatically
                2. Can restore from last backup
                3. Marks all changes for easy identification
                """)
            
            st.warning("""
            ⚠ *Note*: This is a focus tool, not comprehensive parental control software.
            For complete protection, consider commercial solutions.
            """)
            
            st.divider()
            st.caption("Parental Control Pro v2.0 • Secure • Professional")
            hosts_path = get_hosts_path()
            if hosts_path:
                st.caption(f"System hosts file: {hosts_path}")
            backup_dir = get_backup_dir()
            if backup_dir:
                st.caption(f"Backups directory: {backup_dir}")
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- Main Execution ---
if __name__ == "__main__":
    # This must be the FIRST Streamlit command
    st.set_page_config(
        page_title="Parental Control Pro",
        page_icon="🛡",
        layout="centered",
        initial_sidebar_state="auto"
    )
    
    # Then the rest of your execution flow
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        if st.session_state.get('show_register'):
            register_page()
        elif st.session_state.get('show_forgot'):
            forgot_password_page()
        else:
            login_page()
    else:
        main_app()