"""
projects.py — ENVIX Project Presets

This file defines "project presets": one-click starter projects that get
created INSIDE a folder the user chooses, as opposed to stacks.py which
installs languages/tools SYSTEM-WIDE.

Each preset describes:
  "label"      -> Friendly name shown in the GUI
  "languages"  -> List of TOOLS keys that must be installed system-wide
                  first (e.g. "node", "python"). These are checked/installed
                  using the EXISTING installer.py logic — nothing new here.
  "files"      -> Dict of {relative_path: file_content} starter files that
                  get written into the new project folder.
  "commands"   -> List of shell commands to run INSIDE the new project
                  folder after the files are written (e.g. "npm install").
                  These install dependencies/frameworks LOCALLY to the
                  project, never system-wide.

Keeping this as plain data (no functions) keeps it easy to read and easy
to extend — adding a new preset is just adding a new dict entry.
"""

PROJECTS = {

    # ── Web Dev: plain HTML/CSS/JS starter ────────────────────────────────────
    "web": {
        "label": "Web Dev",
        "desc": "Plain HTML, CSS & JS starter — ready to open and edit",
        "languages": ["node", "git", "vscode"],
        "files": {
            "index.html": (
                "<!DOCTYPE html>\n"
                "<html lang=\"en\">\n"
                "<head>\n"
                "  <meta charset=\"UTF-8\">\n"
                "  <title>My Web Project</title>\n"
                "  <link rel=\"stylesheet\" href=\"style.css\">\n"
                "</head>\n"
                "<body>\n"
                "  <h1>Hello, ENVIX!</h1>\n"
                "  <p>Your web project is ready. Start editing index.html.</p>\n"
                "  <script src=\"main.js\"></script>\n"
                "</body>\n"
                "</html>\n"
            ),
            "style.css": (
                "body {\n"
                "  font-family: sans-serif;\n"
                "  background: #0f0f11;\n"
                "  color: #f0f0f5;\n"
                "  text-align: center;\n"
                "  padding-top: 80px;\n"
                "}\n"
            ),
            "main.js": (
                "// Your JavaScript starts here\n"
                "console.log('Project created by ENVIX');\n"
            ),
        },
        "commands": [],   # plain HTML/CSS/JS needs no install step
    },

    # ── Backend (Python / FastAPI) ─────────────────────────────────────────────
    "backend_python": {
        "label": "Backend (Python)",
        "desc": "FastAPI starter with a virtual environment",
        "languages": ["python", "git", "vscode"],
        "files": {
            "main.py": (
                "from fastapi import FastAPI\n\n"
                "app = FastAPI()\n\n"
                "@app.get(\"/\")\n"
                "def read_root():\n"
                "    return {\"message\": \"Hello from FastAPI, via ENVIX\"}\n"
            ),
            "requirements.txt": (
                "fastapi\n"
                "uvicorn\n"
            ),
        },
        # 1. Create a virtual environment named "venv"
        # 2. Install requirements.txt INSIDE that venv (not system-wide)
        "commands": [
            "python -m venv venv",
            r"venv\Scripts\pip install -r requirements.txt",
        ],
    },

    # ── Backend (Node / Express) ────────────────────────────────────────────────
    "backend_node": {
        "label": "Backend (Node)",
        "desc": "Express starter with dotenv and nodemon",
        "languages": ["node", "git", "vscode"],
        "files": {
            "server.js": (
                "// Load environment variables from .env\n"
                "require('dotenv').config();\n"
                "const express = require('express');\n\n"
                "const app = express();\n"
                "const PORT = process.env.PORT || 3000;\n\n"
                "app.get('/', (req, res) => {\n"
                "  res.send('Hello from Express, via ENVIX');\n"
                "});\n\n"
                "app.listen(PORT, () => {\n"
                "  console.log(`Server running on http://localhost:${PORT}`);\n"
                "});\n"
            ),
            ".env": "PORT=3000\n",
            "package.json": (
                "{\n"
                "  \"name\": \"backend-node-project\",\n"
                "  \"version\": \"1.0.0\",\n"
                "  \"main\": \"server.js\",\n"
                "  \"scripts\": {\n"
                "    \"start\": \"node server.js\",\n"
                "    \"dev\": \"nodemon server.js\"\n"
                "  }\n"
                "}\n"
            ),
        },
        # package.json already exists above, so "npm install" just needs
        # the packages added to it — simplest reliable approach for a
        # beginner-friendly tool is to install them directly by name.
        "commands": [
            "npm install express dotenv",
            "npm install -D nodemon",
        ],
    },

    # ── Fullstack (React + Express + MongoDB) ───────────────────────────────────
    "fullstack": {
        "label": "Fullstack",
        "desc": "React (Vite) frontend + Express backend, in one folder",
        "languages": ["node", "git", "vscode"],
        "files": {
            # Backend lives in /server, frontend starter lives in /client.
            # We hand-write a minimal client instead of running the
            # interactive "npm create vite" wizard, which would hang
            # waiting for keyboard input when launched from the GUI.
            "server/server.js": (
                "require('dotenv').config();\n"
                "const express = require('express');\n"
                "const app = express();\n"
                "const PORT = process.env.PORT || 5000;\n\n"
                "app.get('/api/hello', (req, res) => {\n"
                "  res.json({ message: 'Hello from the Express API' });\n"
                "});\n\n"
                "app.listen(PORT, () => console.log(`API running on port ${PORT}`));\n"
            ),
            "server/.env": "PORT=5000\nMONGO_URI=mongodb://localhost:27017/myapp\n",
            "server/package.json": (
                "{\n"
                "  \"name\": \"server\",\n"
                "  \"version\": \"1.0.0\",\n"
                "  \"main\": \"server.js\",\n"
                "  \"scripts\": { \"start\": \"node server.js\", \"dev\": \"nodemon server.js\" }\n"
                "}\n"
            ),
            "client/index.html": (
                "<!DOCTYPE html>\n<html><head><title>Fullstack App</title></head>\n"
                "<body><h1>Frontend client (React via Vite goes here)</h1>\n"
                "<p>Run inside /client: npm install, then npm run dev</p>\n"
                "</body></html>\n"
            ),
            "README.md": (
                "# Fullstack Project (created by ENVIX)\n\n"
                "- /server -> Express API (MongoDB-ready, see server/.env)\n"
                "- /client -> Frontend starter (set up your React/Vite app here)\n\n"
                "To finish the client setup, run inside /client:\n"
                "    npm create vite@latest .\n"
            ),
        },
        # Only the server dependencies are installed automatically since
        # client scaffolding (Vite) is interactive — the README explains
        # the one manual step needed to finish it.
        "commands": [
            "cd server && npm install express dotenv mongoose",
            "cd server && npm install -D nodemon",
        ],
    },

    # ── AI / ML ─────────────────────────────────────────────────────────────────
    "ai_ml": {
        "label": "AI / ML",
        "desc": "NumPy, pandas, scikit-learn & Jupyter in a virtual environment",
        "languages": ["python", "git", "vscode"],
        "files": {
            "main.py": (
                "import numpy as np\n"
                "import pandas as pd\n"
                "from sklearn.linear_model import LinearRegression\n\n"
                "print('NumPy version:', np.__version__)\n"
                "print('pandas version:', pd.__version__)\n"
                "print('Project created by ENVIX — ready for AI/ML work.')\n"
            ),
            "requirements.txt": (
                "numpy\n"
                "pandas\n"
                "scikit-learn\n"
                "jupyter\n"
            ),
        },
        "commands": [
            "python -m venv venv",
            r"venv\Scripts\pip install -r requirements.txt",
        ],
    },

    # ── Data Science ─────────────────────────────────────────────────────────────
    "data_science": {
        "label": "Data Science",
        "desc": "pandas, matplotlib & seaborn in a virtual environment",
        "languages": ["python", "git", "vscode"],
        "files": {
            "main.py": (
                "import pandas as pd\n"
                "import matplotlib.pyplot as plt\n"
                "import seaborn as sns\n\n"
                "print('Project created by ENVIX — ready for data analysis.')\n"
            ),
            "requirements.txt": (
                "pandas\n"
                "matplotlib\n"
                "seaborn\n"
            ),
        },
        "commands": [
            "python -m venv venv",
            r"venv\Scripts\pip install -r requirements.txt",
        ],
    },

    # ── Game Dev (pygame) ────────────────────────────────────────────────────────
    "game_dev": {
        "label": "Game Dev",
        "desc": "Pygame starter window, ready to run",
        "languages": ["python", "git", "vscode"],
        "files": {
            "main.py": (
                "import pygame\n\n"
                "pygame.init()\n"
                "screen = pygame.display.set_mode((640, 480))\n"
                "pygame.display.set_caption('My Game — made with ENVIX')\n\n"
                "running = True\n"
                "while running:\n"
                "    for event in pygame.event.get():\n"
                "        if event.type == pygame.QUIT:\n"
                "            running = False\n\n"
                "    screen.fill((15, 15, 17))\n"
                "    pygame.display.flip()\n\n"
                "pygame.quit()\n"
            ),
            "requirements.txt": "pygame\n",
        },
        "commands": [
            "python -m venv venv",
            r"venv\Scripts\pip install -r requirements.txt",
        ],
    },
}
