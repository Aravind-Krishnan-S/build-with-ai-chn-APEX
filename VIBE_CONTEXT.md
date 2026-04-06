# 🧠 VIBE-SYNC PROJECT CONTEXT

## 🏗 Architecture & Stack
- **Core:** Python CLI (using `typer` and `rich`)
- **AI Backend (Decoupled Mode):** 
    - **Primary Engine:** AI Studio (Gemini API) via `.env` key.
    - **Add-on (Optional):** Vertex AI (GCP) enabled via `USE_VERTEX_AI=true`.
    - **Automatic Fallback:** If Vertex AI fails (403, billing, auth), the tool automatically downgrades to Core AI Studio without interrupting the developer workflow.
- **Automation:** Git `post-commit` hook for instant context updates.
- **MCP Server:** Native `FastMCP` implementation for agentic context retrieval.

## 🚦 Current Progress
- **Completed Features:**
    - [x] AI Bridge with **Automatic Fallback** logic.
    - [x] Git `post-commit` hook integration.
    - [x] GCP Isolation in the AI Studio path.
    - [x] Final decoupled architectural refactor.
    - [x] Created `src/vibe_sync/trimmer.py` for token tracking (`tiktoken`).
    - [x] Implemented history compression logic to replace large logs with AI-generated architectural milestones.

## 🐛 Known Issues
- **GCP Billing:** Vertex AI remains an optional "add-on" until billing is linked to the project (currently triggers a non-blocking warning).
- **API Quota:** Free-tier Gemini API key prone to 429 errors under heavy load.

## ➡️ The Next Move
- Launch the Vibe-Sync Context Server on Cloud Run to enable cross-device "telepathy" between coding sessions.
