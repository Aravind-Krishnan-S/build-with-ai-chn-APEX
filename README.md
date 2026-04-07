<![CDATA[<div align="center">

# 🧠 Vibe-Sync

### Persistent Context Engine for AI Coding Agents

*Eliminate cold-start amnesia. Give your AI agent instant telepathy.*

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blueviolet)](https://modelcontextprotocol.io)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Ready-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com)

</div>

---

## The Problem

Every time you start a new session with an AI coding assistant, it suffers from **cold-start amnesia**. The agent has to blindly crawl your file tree, read dozens of files, and guess your architectural decisions — just to catch up to where you left off.

This wastes **hundreds of thousands of API tokens**, hits rate limits, and degrades the developer experience because the AI forgets the *vibe* of the project: the work in progress, the architectural choices, and the immediate next steps.

## The Solution

**Vibe-Sync** is an automated context preservation engine that maintains a living, AI-generated project summary (`VIBE_CONTEXT.md`). It ensures your AI agents immediately understand your project state the second they boot up — without wasting a single token on recursive directory exploration.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔄 **Automatic Git Integration** | A `post-commit` hook captures every commit's diff and updates project context automatically |
| 🤖 **AI-Powered Summarization** | Uses **Google Gemini** to intelligently rewrite project state from raw code diffs |
| 📡 **Native MCP Server** | Built with **FastMCP** — any modern AI IDE or agent can connect and call `get_latest_vibe()` |
| 💰 **Budget Mode** | Serves only the *Hot Path* and *Active Goals*, saving ~70% on context framing tokens |
| 📦 **Smart History Compression** | When context exceeds 2,000 tokens, the trimmer compresses granular logs into high-level milestones via Gemini Flash |
| ☁️ **Google Cloud Sync** | Push/pull context to **Google Cloud Storage** for cross-machine and team collaboration |
| 🚀 **One-Command Cloud Deployment** | Deploy the MCP server to **Google Cloud Run** with a single CLI command |
| 🛡️ **Multi-Model Fallback** | Gracefully falls back through Gemini models → Groq (Llama 3.3) to ensure zero downtime |
| 📋 **Project Bundler** | Bundle your entire codebase into a single markdown file for AI upload |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Developer                             │
│                    git commit -m "..."                        │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│              Git Post-Commit Hook                            │
│          (hooks.py — auto-installed)                          │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   vibe-sync commit                            │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ vibe_core.py│  │ ai_bridge.py │  │   trimmer.py        │ │
│  │ (git diff)  │→ │ (Gemini API) │→ │ (token compression) │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
│                                                              │
│  Output: VIBE_CONTEXT.md (updated)                           │
└──────────────────┬───────────────────────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
┌──────────────────┐  ┌──────────────────────────────────────┐
│  MCP Server      │  │  Google Cloud Storage                │
│  (server.py)     │  │  vibe-sync cloud-push / cloud-pull   │
│                  │  └──────────────────────────────────────┘
│  Tools:          │
│  • get_latest_vibe│
│  • read_vibe     │
│  • search_archive│
│  • vibe_commit   │
│  • ... (15 tools)│
└──────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│               AI Agent (Antigravity, Cursor, etc.)            │
│            Instant context — zero cold start                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Git** (for diff tracking and hooks)
- A **Gemini API key** ([Get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/vibe-sync.git
cd vibe-sync

# Install dependencies
pip install -r requirements.txt

# Or install as a package (editable mode)
pip install -e .
```

### Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Groq fallback
GROQ_API_KEY=your_groq_api_key_here

# Optional: Use Vertex AI instead of AI Studio
# USE_VERTEX_AI=true
# GOOGLE_CLOUD_PROJECT=your-gcp-project-id
```

---

## 📖 CLI Usage

### Initialize a Project

```bash
vibe-sync init
```

Creates a `VIBE_CONTEXT.md` file and `.vibe/config.json` in the current directory. The context file is automatically added to `.gitignore`.

### Sync Context with AI

```bash
vibe-sync commit -m "added user authentication"
```

Captures the latest git diff, sends it to Gemini, and rewrites `VIBE_CONTEXT.md` to reflect the current project state.

### Install Git Hook (Recommended)

```bash
vibe-sync install-hooks
```

Installs a `post-commit` hook so that **every `git commit`** automatically triggers a context sync. This is completely invisible to your workflow.

### Check Project Status

```bash
vibe-sync status
```

Displays a rich table showing project name, sync count, last commit, hook status, and cloud configuration.

### Bundle Project for AI Upload

```bash
vibe-sync bundle --output my_bundle.md
```

Concatenates all source files into a single markdown document, useful for uploading to AI assistants that don't support MCP.

### Push to Antigravity Brain

```bash
vibe-sync push antigravity
```

Copies `VIBE_CONTEXT.md` and a `memory.json` file into Antigravity's persistent brain directory (`~/.gemini/antigravity/brain/`).

### Test MCP Connectivity

```bash
vibe-sync mcp-test
```

Runs a diagnostic suite to verify the MCP server module, FastMCP installation, tool registration, and Antigravity configuration.

---

## ☁️ Google Cloud Integration

### Configure Cloud Storage

```bash
vibe-sync cloud-init --bucket my-vibe-bucket --project my-gcp-project
```

### Push Context to Cloud

```bash
vibe-sync cloud-push
```

Uploads `VIBE_CONTEXT.md` and `.vibe/config.json` to a GCS bucket under a project-specific prefix.

### Pull Context from Cloud

```bash
vibe-sync cloud-pull
```

Downloads the latest context from GCS, overwriting local files — perfect for syncing across machines.

### Deploy MCP Server to Cloud Run

```bash
vibe-sync deploy --project my-gcp-project --region us-central1
```

Builds a Docker container and deploys the MCP server to Google Cloud Run. The server automatically reads from GCS when the `GCS_BUCKET` environment variable is set.

```bash
# Preview the deploy command without executing
vibe-sync deploy --dry-run
```

---

## 🔌 MCP Server Integration

Vibe-Sync ships with a native **Model Context Protocol (MCP)** server built on [FastMCP](https://github.com/jlowin/fastmcp). This allows any MCP-compatible AI agent to connect and read project context natively.

### Available MCP Tools

| Tool | Description |
|---|---|
| `get_latest_vibe` | Returns a **budget mode** summary — Hot Path + Active Goals only (~70% token savings) |
| `read_vibe` | Returns the full `VIBE_CONTEXT.md` contents |
| `search_archive` | Searches `.vibe/history_log.json` for specific historical context |
| `vibe_init` | Initialize a new project remotely |
| `vibe_commit` | Trigger an AI-powered context sync |
| `vibe_install_hooks` | Install post-commit hooks |
| `vibe_bundle` | Bundle project source into a single markdown file |
| `vibe_status` | Show project status and sync history |
| `vibe_push` | Push context to Antigravity's brain |
| `vibe_mcp_test` | Run MCP connectivity diagnostics |
| `vibe_cloud_init` | Configure GCS bucket |
| `vibe_cloud_push` | Push context to GCS |
| `vibe_cloud_pull` | Pull context from GCS |
| `vibe_deploy` | Deploy MCP server to Cloud Run |

### Connecting to the MCP Server

Add the following to your AI agent's MCP configuration file:

```json
{
  "mcpServers": {
    "vibe-sync": {
      "command": "python",
      "args": ["path/to/vibe-sync/server.py"],
      "env": {},
      "timeout": 30
    }
  }
}
```

The server automatically detects `VIBE_CONTEXT.md` by searching upward from the working directory. If the file doesn't exist, it **auto-initializes** the project.

---

## 🔄 How The Trimmer Works

Over time, `VIBE_CONTEXT.md` naturally grows as progress accumulates. The built-in trimmer prevents context bloat:

1. **Token Monitoring** — Uses `tiktoken` to count tokens in the context file
2. **Threshold Check** — If the file exceeds **2,000 tokens**, compression triggers
3. **AI Compression** — Sends detailed logs to Gemini 1.5 Flash, which compresses ~20 granular steps into 5 high-level architectural milestones
4. **Archival** — Raw, original logs are safely archived to `.vibe/history_log.json`
5. **On-Demand Retrieval** — The `search_archive` MCP tool lets agents query historical logs if they need specific details

---

## 🛡️ AI Model Fallback Chain

Vibe-Sync implements a resilient multi-model pipeline:

```
Vertex AI (Enterprise, if enabled)
    ↓ fallback
Gemini API (AI Studio — multiple model variants)
    ↓ fallback
Groq API (Llama 3.3 70B Versatile)
```

This ensures context updates never fail due to a single API issue.

---

## 📁 Project Structure

```
vibe-sync/
├── main.py              # CLI entry point (Typer app with all commands)
├── server.py            # MCP server (FastMCP, exposes 15+ tools)
├── vibe_core.py         # Core logic: context creation, git diff extraction
├── ai_bridge.py         # AI integration: Gemini, Vertex AI, Groq fallback
├── config.py            # .vibe/config.json management and sync tracking
├── hooks.py             # Git post-commit hook installer (cross-platform)
├── cloud.py             # Google Cloud Storage upload/download/listing
├── deploy.py            # Cloud Run deployment helper
├── models.py            # Pydantic UniversalState schema (markdown ↔ object)
├── src/
│   └── vibe_sync/
│       ├── __init__.py  # Package init
│       └── trimmer.py   # Token-based context compression
├── Dockerfile           # Container image for Cloud Run deployment
├── pyproject.toml       # Package configuration and dependencies
├── requirements.txt     # Python dependencies
├── mcp_config_snippet.json  # Example MCP configuration
├── GEMINI.md            # Agent rules for Gemini CLI
├── CLAUDE.md            # Agent rules for Claude/Codex
├── ANTIGRAVITY.md       # Agent rules for Antigravity
└── .env                 # API keys (not committed)
```

---

## 🧰 Tech Stack

| Component | Technology |
|---|---|
| **CLI Framework** | [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/) |
| **AI Engine** | [Google Gemini](https://ai.google.dev/) (primary) / [Groq](https://groq.com/) (fallback) |
| **MCP Server** | [FastMCP](https://github.com/jlowin/fastmcp) |
| **Data Validation** | [Pydantic](https://docs.pydantic.dev/) |
| **Git Integration** | [GitPython](https://gitpython.readthedocs.io/) |
| **Token Counting** | [tiktoken](https://github.com/openai/tiktoken) |
| **Cloud Storage** | [Google Cloud Storage](https://cloud.google.com/storage) |
| **Deployment** | [Google Cloud Run](https://cloud.google.com/run) + Docker |
| **Environment** | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the AI-assisted development era**

*Read the Vibe → Do your work → Save the Vibe*

</div>
]]>
