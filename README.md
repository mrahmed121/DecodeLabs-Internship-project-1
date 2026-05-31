🤖 DecodeBot Personal — VVIP Professional Edition
DecodeLabs AI Engineering Internship — Week 4
Project 4: Enterprise Conversational AI Agent
Track: AI Engineering Intern | Batch: 2026
📋 Table of Contents
Project Overview
Key Features
Technical Stack
Architecture Diagram
Project Structure
Installation & Setup
Configuration (.env)
How to Run
CLI Mode
Web UI Mode
Admin Commands
Self-Test Suite
Logging & Audit
Screenshots
Learning Outcomes
Acknowledgements
🎯 Project Overview
DecodeBot Personal is a production-grade, rule-based conversational AI agent built with enterprise-level architecture. Unlike simple chatbots, this system features:
Multi-tier intent classification (Exact → Regex → Contains → Fallback)
Contextual session memory with bounded history rotation
Dynamic profile management with import/export capabilities
Dual-mode deployment (Interactive CLI + Flask Web UI)
Comprehensive audit logging for compliance and debugging
The bot maintains a personalized identity system and responds intelligently to greetings, identity queries, status checks, and administrative commands.
✨ Key Features
Table
Feature	Implementation	Status
🔐 Secure Config	python-dotenv + Environment Variables	✅
🛡️ Error Shielding	Custom Exception Hierarchy + Top-Level Try-Except	✅
🎨 Terminal UI	Unicode Box-Drawing + Safe ANSI Colors (Auto-Detect)	✅
📝 Auto-Logging	Dual-Channel: Console + Rotating File (app.log)	✅
⚡ Performance	Pre-compiled Regex Cache + O(1) Phrase Map + Type Hints	✅
🧠 Intent Engine	4-Tier Matching: Exact → Regex → Contains → Fallback	✅
💾 Profile CRUD	JSON Persistence with Atomic Write Pattern	✅
🌐 Web UI	Embedded Flask SPA with Dark Theme	✅
🧪 Self-Tests	Built-in Regression Suite (8 Test Cases)	✅
📊 Session Audit	Confidence Tracking + Turn History + Summary	✅
🛠️ Technical Stack
plain
Python 3.10+
├── Standard Library
│   ├── re, json, random, argparse, logging, logging.handlers
│   ├── sys, textwrap, pathlib, datetime, dataclasses
│   └── typing (Dict, List, Tuple, Optional, Final, etc.)
│
├── Third-Party
│   ├── python-dotenv    → Secure configuration management
│   └── flask            → Optional web UI (pip install flask)
│
└── Design Patterns
    ├── Singleton Logger
    ├── Factory (ProfileManager)
    ├── Strategy (Intent Matching Tiers)
    └── Command (Admin Processor)
🏗️ Architecture Diagram
plain
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌─────────────┐      ┌─────────────┐                     │
│  │   CLI Mode  │      │  Web UI     │                     │
│  │  (Terminal) │      │  (Flask)    │                     │
│  └──────┬──────┘      └──────┬──────┘                     │
│         │                    │                             │
│         └────────┬───────────┘                             │
│                  │                                          │
│         ┌────────▼──────────┐                              │
│         │  Admin Processor  │ ← /profile-show, /profile-set │
│         └────────┬──────────┘                              │
│                  │                                          │
│         ┌────────▼──────────┐                              │
│         │   Intent Engine   │ ← 4-Tier Classification       │
│         │  (Rule-Based NLP) │                               │
│         └────────┬──────────┘                              │
│                  │                                          │
│    ┌─────────────┼─────────────┐                         │
│    │             │             │                             │
│ ┌──▼──┐    ┌───▼───┐   ┌────▼────┐                       │
│ │Profile│    │Session │   │  Logger │                       │
│ │Manager│    │Manager │   │ (Dual)  │                       │
│ └───────┘    └───────┘   └─────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
📁 Project Structure
plain
DecodeLabs-Week4-DecodeBot/
│
├── 📄 README.md                          ← You are here
├── 📄 decodebot_vvip.py                  ← Main application (single file)
├── 📄 .env                               ← Environment configuration (DO NOT UPLOAD TO GITHUB!)
├── 📄 .gitignore                         ← Excludes .env, logs/, *.log
├── 📄 requirements.txt                   ← Python dependencies
│
├── 📂 logs/
│   └── 📄 app.log                        ← Auto-generated audit trail
│
├── 📄 user_profile.json                  ← Auto-generated profile storage
│
└── 📂 assets/
    ├── 📸 screenshot_cli.png             ← Terminal execution screenshot
    ├── 📸 screenshot_web.png           ← Web UI screenshot
    └── 📸 screenshot_selftest.png      ← Self-test results screenshot
⚙️ Installation & Setup
Step 1: Clone or Download
bash
git clone https://github.com/yourusername/DecodeLabs-Week4-DecodeBot.git
cd DecodeLabs-Week4-DecodeBot
Step 2: Create Virtual Environment (Recommended)
bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install python-dotenv

# Optional (for Web UI)
pip install flask
Or use requirements:
bash
pip install -r requirements.txt
Step 4: Create .env File
Create a file named .env in the same directory as decodebot_vvip.py:
env
# ── Logging ───────────────────────────
LOG_LEVEL=INFO
LOG_FILE=app.log
LOG_DIR=logs

# ── Session ───────────────────────────
MAX_HISTORY=20
ROTATING_MAX_BYTES=2000000
ROTATING_BACKUP_COUNT=3

# ── Profile ───────────────────────────
PROFILE_FILE=user_profile.json

# ── Web Server ────────────────────────
WEB_HOST=127.0.0.1
WEB_PORT=5000
WEB_DEBUG=False

# ── Identity (Personalization) ────────
IDENTITY_NAME=Ahmed
IDENTITY_SPOUSE=Mariyum
IDENTITY_DISPLAY_NAME=MARIYUM KA AHMED
⚠️ IMPORTANT: Add .env to your .gitignore file so it never gets uploaded to GitHub!
gitignore
# .gitignore
.env
logs/
*.log
__pycache__/
venv/
🚀 How to Run
🖥️ Mode 1: Interactive CLI (Default)
bash
python decodebot_vvip.py
Sample Interaction:
plain
╔══════════════════════════════════════════════════════════════════════════════╗
║               DECODEBOT PERSONAL — VVIP EDITION                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Type your message and press Enter.                                          ║
║  Admin commands start with /  |  Type "bye" or "exit" to quit.               ║
╠══════════════════════════════════════════════════════════════════════════════╣
➤ You: hi
➤ Bot: My name is Ahmed, but my absolute identity is 'MARIYUM KA AHMED'...

➤ You: /profile-show
➤ Bot: Current Profile:
  {
    "user_name": "Ahmed",
    "spouse_name": "Mariyum",
    ...
  }

➤ You: bye
➤ Bot: Goodbye! Have a great day.
🌐 Mode 2: Web UI (Requires Flask)
bash
python decodebot_vvip.py --web
Then open your browser to: http://127.0.0.1:5000
Features:
Dark-themed single-page chat interface
Real-time intent and confidence display
Mobile-responsive design
🧪 Mode 3: Self-Test (Regression Suite)
bash
python decodebot_vvip.py --selftest
Output:
plain
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SELF-TEST REGRESSION SUITE                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [PASS] | Input: 'Hi'                     | Expected: greeting    | Got: greeting    ║
║  [PASS] | Input: 'bye'                    | Expected: goodbye   | Got: goodbye   ║
║  [PASS] | Input: "What's your name?"      | Expected: identity  | Got: identity  ║
║  [PASS] | Input: 'How are you?'           | Expected: status    | Got: status    ║
║  [PASS] | Input: 'Tell me about me'       | Expected: tell_me_..| Got: tell_me_..║
║  [PASS] | Input: 'qwertyuiop12345'      | Expected: fallback  | Got: fallback  ║
║  [PASS] | Input: 'help'                   | Expected: help      | Got: help      ║
║  [PASS] | Input: 'thanks a lot'           | Expected: thanks    | Got: thanks    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Results: 8/8 passed (100%)                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
🔧 Mode 4: Debug Logging
bash
python decodebot_vvip.py --debug
⌨️ Admin Commands
While chatting, type commands starting with /:
Table
Command	Description	Example
/help	Show all available commands	/help
/profile-show	Display current profile as JSON	/profile-show
/profile-set key=value	Update a profile field	/profile-set notes=New note
/profile-export path.json	Export profile to file	/profile-export backup.json
/profile-import path.json	Import profile from file	/profile-import backup.json
/session-summary	Show session statistics	/session-summary
📝 Logging & Audit
Every conversation turn is automatically logged to logs/app.log:
plain
[2026-05-31 14:32:01] [INFO] [main:489] Logging infrastructure initialized
[2026-05-31 14:32:05] [DEBUG] [match:312] Exact match | Intent: greeting | Input: Hi
[2026-05-31 14:32:05] [INFO] [run:245] chat_turn | intent=greeting | conf=1.00 | user=Hi
[2026-05-31 14:32:08] [INFO] [process:198] Admin command received | Action: /profile-show
Log Features:
✅ RotatingFileHandler — Auto-rotates when file exceeds 2MB (keeps 3 backups)
✅ Dual Channel — INFO+ to console, DEBUG+ to file
✅ Full Audit Trail — Timestamps, function names, line numbers, session IDs
✅ Input/Output Capture — Every user message and bot response recorded
📸 Screenshots
Add your execution screenshots in the /assets/ folder:
Table
Screenshot	Description
Terminal CLI interaction
Flask Web UI in browser
Regression test results
app.log audit trail
🎓 Learning Outcomes
Through this project, I have demonstrated:
✅ Enterprise Architecture — Separation of concerns (UI, Engine, Profile, Session, Admin)
✅ Secure Configuration — Zero hardcoded values; full .env externalization
✅ Defensive Programming — Custom exception hierarchy with graceful degradation
✅ Professional Logging — Structured, rotating, dual-channel audit system
✅ State Management — Bounded session history with FIFO rotation
✅ CLI Design — Unicode box-drawing with safe, auto-detecting ANSI colors
✅ Web Integration — Optional Flask backend with embedded SPA frontend
✅ Testing Discipline — Built-in regression suite for CI/CD readiness
✅ Type Safety — Comprehensive type hints across all functions and classes
✅ Documentation — Docstrings for every class, method, and module
🙏 Acknowledgements
DecodeLabs — For providing this structured internship and learning opportunity
Python Software Foundation — For the robust standard library
Pallets Projects (Flask) — For the lightweight web framework
python-dotenv — For secure configuration management
📬 Contact
For any queries regarding this project:
Intern Name: [M AHMED ALI ]
Email: [muhammadahmedali607@gmail.com ]
LinkedIn: [  www.linkedin.com/in/muhammad-ahmed-ali-123125406]
GitHub: [https://github.com/mrahmed121]
<div align="center">
⭐ DecodeLabs AI Engineering Internship — Week 4 ⭐
Submitted as part of the official internship program.
</div>
