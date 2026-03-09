<div align="center">

# 🤖 ProBharatAI

### Open-Source AI That Controls Your Computer With One Prompt

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**ProBharatAI is your personal AI desktop operator.** Use natural language to automate your computer, browser, job applications, and much more.

[Get Started](#-installation) · [Features](#-features) · [Documentation](#-documentation) · [Contributing](#-contributing)

</div>

---

## 🎯 What is ProBharatAI?

ProBharatAI is an **open-source AI desktop automation platform** that understands natural language and executes complex tasks on your computer.

```
You: "Search product manager jobs on LinkedIn, apply to first 20 easy apply jobs,
      track results, send Telegram notification"

ProBharatAI: ✅ Done! Applied to 18 jobs. Summary sent to Telegram.
```

### How It Works

```
User Prompt → AI Planner → Task Breakdown → Tool Execution → Results + Notification
```

---

## ✨ Features

### 🌐 Browser Automation
- Navigate, click, type, scrape, screenshot
- Supports Chrome, Edge, Firefox via Playwright
- Smart form filling and data extraction

### 💼 Job Automation
- LinkedIn, Naukri, Indeed support
- Auto-search, resume matching, one-click apply
- Track applications in CSV, SQLite, or Google Sheets

### 🖥️ Computer Control
- Open apps, run commands, manage files
- Keyboard/mouse automation via PyAutoGUI
- Cross-platform: Windows, macOS, Linux

### 📱 Telegram Notifications
- Real-time task updates
- Job application summaries
- Approve/reject actions remotely

### 🧠 Multi-LLM Support
- OpenAI GPT-4o
- Anthropic Claude
- Google Gemini
- Groq (ultra-fast)
- Ollama (fully local, zero cost)
- OpenRouter (multi-model)

### 🔐 Security
- Approval required before critical actions
- Approve from UI or Telegram
- Full action logging

---

## 🚀 Installation

### One Command Install

**Windows:**
```bash
git clone https://github.com/probharatai/probharatai.git
cd probharatai
scripts\install.bat
```

**Mac / Linux:**
```bash
curl -s https://raw.githubusercontent.com/probharatai/probharatai/main/scripts/install.sh | bash
```

### Manual Install

```bash
# Clone
git clone https://github.com/probharatai/probharatai.git
cd probharatai

# Backend
cd backend
pip install -r requirements.txt
python -m playwright install chromium

# Frontend
cd ../frontend
npm install

# Configure
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

---

## ⚡ Quick Start

```bash
# Start ProBharatAI
python cli.py start

# Check status
python cli.py status

# Run a prompt
python cli.py run "Search AI jobs on LinkedIn"
```

**Dashboard:** http://localhost:3000
**API:** http://localhost:8000

---

## 💡 Example Prompts

```
Apply to product manager jobs on LinkedIn
Download all invoices from Gmail
Scrape competitor pricing and save to CSV
Generate a lead list for SaaS startups in India
Open Chrome and search for AI startups
Send job application summary to Telegram
Search remote Python developer jobs on Indeed
Rename all files in Downloads folder
```

---

## 📱 Telegram Setup

1. Open Telegram, search for **@BotFather**
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Add token in ProBharatAI Settings

Your bot will send you:
```
🤖 ProBharatAI Update:
✅ Applied to 12 jobs today
🏢 Top company: Stripe
💼 Role: Product Manager
```

---

## 🏗️ Architecture

```
probharatai/
├── backend/
│   ├── agents/          # AI Planner, Executor, Memory
│   ├── tools/           # Browser, System, Filesystem, Jobs, Telegram
│   ├── llm/             # OpenAI, Claude, Groq, Gemini, Ollama adapters
│   ├── api/             # REST API routes
│   ├── database/        # SQLite models
│   ├── main.py          # Flask server
│   └── config.py        # Configuration
├── frontend/            # React PWA + Tailwind
│   └── src/
│       ├── pages/       # Dashboard, Chat, Jobs, Logs, Settings
│       └── api.js       # API client
├── scripts/             # Install & start scripts
├── cli.py               # CLI tool
└── README.md
```

---

## 📖 Documentation

| Topic | Description |
|-------|-------------|
| [Installation](scripts/) | Setup guides for all platforms |
| [Configuration](backend/.env.example) | Environment variables reference |
| [API Reference](backend/api/) | REST API documentation |
| [Contributing](CONTRIBUTING.md) | How to contribute |
| [Roadmap](ROADMAP.md) | Future plans |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 🗺️ Roadmap

- [x] Core agent system
- [x] Browser automation (Playwright)
- [x] Multi-LLM support
- [x] Job automation (LinkedIn, Naukri, Indeed)
- [x] Telegram integration
- [x] React PWA dashboard
- [ ] Plugin marketplace
- [ ] AI workflow marketplace
- [ ] Google Sheets integration
- [ ] Email automation
- [ ] Voice commands
- [ ] Mobile app

See full [ROADMAP.md](ROADMAP.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🌟 Star History

If you find ProBharatAI useful, please ⭐ star the repo!

---

<div align="center">

**Built with ❤️ for the open-source community**

[⬆ Back to top](#-probharatai)

</div>
