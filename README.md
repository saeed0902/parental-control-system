# Parental Control Pro

A professional, timer-based parental control application built with Streamlit.  
It uses your system’s hosts file to block or allow specified websites for a set duration, with automatic backups and restoration.

---

## 🔍 Table of Contents

- [Features](#-features)  
- [Demo](#-demo)  
- [Tech Stack](#-tech-stack)  
- [Getting Started](#-getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [Running the App](#running-the-app)  
- [Usage](#-usage)  
- [Configuration](#-configuration)  
- [Security & Permissions](#-security--permissions)  
- [Troubleshooting](#-troubleshooting)  
- [Contributing](#-contributing)  
- [License](#-license)  

---

## 🚀 Features

- **Secure Authentication** — username/password login & user registration  
- **Block Mode** — block specific websites for a timer duration  
- **Allow Mode** — allow only specified websites (block all others)  
- **Automatic Backups** — hosts file backed up before each change  
- **Auto-Restore** — reverts hosts file and flushes DNS when time is up or on stop  
- **Modern UI** — fully styled with CSS for a polished look  
- **Multi-Platform** — supports Windows, macOS & Linux hosts file paths  

---

## 📸 Demo

![Login Page]![DFG](https://github.com/user-attachments/assets/ca095fa4-2708-46b2-8b60-20e51b936432)

![Control Panel](![image](https://github.com/user-attachments/assets/d568d159-e5ba-470e-8f3b-d1defa7eb8dc)


---

## 🛠 Tech Stack

- **Language:** Python 3.8+  
- **Framework:** [Streamlit](https://streamlit.io/)  
- **Database:** SQLite (`users.db`)  
- **Utilities:** `psutil`, `hashlib`, `sqlite3`, `subprocess`

---

## 🏁 Getting Started

### Prerequisites

- Python 3.8 or higher  
- Git  
- Administrator (Windows) or `sudo` (macOS/Linux) privileges  

### Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/<your-username>/parental-control-pro.git
   cd parental-control-pro
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

```bash
streamlit run app.py
```

- On Windows: open your command prompt **as Administrator**  
- On macOS/Linux: prefix with `sudo`, or grant write permission to `/etc/hosts`

The app will open in your browser at `http://localhost:8501`.

---

## 🎛 Usage

1. **Register / Login**  
   - Create an account or use the default admin (`admin` / `admin123`).  
2. **Select Mode**  
   - **Block Mode**: add domains to block.  
   - **Allow Mode**: toggle “Allow Mode” and list domains to permit.  
3. **Set Duration**  
   - Choose from presets or enter custom minutes.  
4. **Start Control**  
   - The app backs up your hosts file, applies changes, and flushes DNS.  
5. **Stop Control**  
   - Manually stop early, or wait for the timer to auto-restore.

---

## ⚙ Configuration

- **DEFAULT ADMIN**  
  - Username: `admin`  
  - Password: `admin123`  
- **Hosts Marker**  
  - Lines added to hosts are tagged with `# Added by ParentalControlApp v2.0`

- **Backup Folder**  
  - Created at `~/.parental_control_backups`  

---

## 🔒 Security & Permissions

- **Hosts File** modification requires elevated privileges.  
- **Windows**: run command prompt as Administrator.  
- **macOS/Linux**: run with `sudo`.  
- The app automatically checks for admin/root rights and stops with an error if missing.

---

## ❓ Troubleshooting

- **“Permission denied”** → ensure you launched the app with admin/root.  
- **Changes not applying** → try manually flushing your DNS:  
  - Windows: `ipconfig /flushdns`  
  - macOS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`  
  - Linux: `sudo systemd-resolve --flush-caches`  

---

## 🤝 Contributing

1. Fork the repository  
2. Create a new branch (`git checkout -b feature/my-feature`)  
3. Commit your changes (`git commit -m 'Add feature'`)  
4. Push to the branch (`git push origin feature/my-feature`)  
5. Open a Pull Request  

---

## 📄 License

This project is licensed under the MIT License.  
See [LICENSE](LICENSE) for details.
