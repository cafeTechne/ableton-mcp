# Antigravity Ableton MCP (Windows/Codex Edition)

> **Note**: While this project was originally forked from [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp), it has been **completely re-architected** into a comprehensive production system.
>
> We have moved far beyond the original proof-of-concept, expanding the codebase by orders of magnitude to create an **actually useful tool for serious musicians**. This is not just a playback controller; it is an AI co-producer capable of understanding music theory, complex routing, and deep structural arrangement.

This project is specifically designed for:
*   **VS Code** with the **Codex** extension, or
*   **Google Antigravity** (the VS Code fork)

It connects **Ableton Live 11** to your agent using the Model Context Protocol (MCP), unlocking the full depth of the Live 11 API through a modular, robust backend.

---

## 🚀 The "Antigravity" Difference

The difference between this and the original repo is night and day:

### 1. From "Toy" to "Production Workbench"
*   **Complete Overhaul**: The original codebase was a lightweight experiment for Mac. This is a robust system optimized for Windows.
*   **Modular Architecture**: No monoliths. The system is cleanly separated:
    *   `MCP_Server/` (RPC layer)
    *   `mcp_tooling/` (Logic, Theory, Device Management)
    *   `AbletonMCP_Remote_Script/handlers/` (21 specialized API handler modules)
*   **Musician-Centric**: Every tool was redesigned with production workflow in mind—solving real problems like sidechain routing, precise EQing, and complex rack management.

### 2. Deep Live 11 API Integration
*   The original touched the surface; **we have mapped 220+ MCP tools** covering the entirety of the Live 11 API.
*   **Explicit Implementation**: The API is not "guessed" by the AI. It is explicitly written into 21 handler modules in our Remote Script (e.g., `handlers/device.py` at 66KB, `handlers/track.py` at 101KB).
*   **Robust Networking**: Rebuilt the socket communication layer from scratch to handle heavy data loads.

### 3. Agentic Music Theory Core
This is the biggest addition. The agent now "knows" music:
*   **Advanced Chord Progressions**: Understands functional harmony (Key, Scale, Mood, Voice Leading, Inversions).
*   **Intelligent Basslines**: Walking, Funk, Rock, Reggae styles that follow chord changes.
*   **Orchestration Modules**: Dedicated generators for Strings, Woodwinds, and Brass with genre profiles.
*   **Rhythm & Groove**: A **4.2MB library of drum patterns** covering house, hiphop, techno, jazz, and more.
*   **Song Blueprints**: Can scaffold entire song arrangements from a simple prompt.

---

## � By the Numbers

| Component | Original | Antigravity Version |
|:---|:---:|:---:|
| MCP Tools | ~20 | **220+** |
| Remote Script Handler Files | 1 | **21** |
| Server Tooling Modules | 1 | **25** |
| Agentic Workflow Docs | 0 | **30** |
| Drum Pattern Library | 0 | **4.2 MB** |

---

## 🛠 Prerequisites

*   **Ableton Live 11** (Suite suggested for full API access)
*   **Windows 10/11**
*   **Python 3.10+**
*   **VS Code** with **Codex** extension, or **Google Antigravity**
*   [`uv`](https://astral.sh/uv) package manager (installed and on PATH)

### Python Dependencies

This project requires two Python packages:

| Package | Purpose |
|:---|:---|
| `mcp[cli]>=1.3.0` | Model Context Protocol library |
| `fastmcp` | FastMCP framework for tool definitions |

**Install with uv (recommended):**
```bash
cd ableton-mcp
uv sync
```

**Or with pip:**
```bash
pip install mcp[cli]>=1.3.0 fastmcp
```

## 📦 Installation

### 1. Install the Remote Script
You can install the script manually or use our deployment tool.

**Option A: Automatic (Recommended)**
Run the deploy script from the repo root:
```powershell
python scripts/deploy.py
# Or, clear cached .pyc files first:
python scripts/deploy.py --clean
```
*This will automatically find your User Library and install/update the script.*

**Option B: Manual**
1.  Close Ableton Live.
2.  Navigate to: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\`
3.  Copy the `AbletonMCP_Remote_Script` folder from this repo into that location.

### 2. Configure Ableton Live
1.  Launch Ableton Live (or Relaunch it to ensure the script is loaded if it was running when you ran deploy.py).
2.  Go to **Options > Preferences > Link, Tempo & MIDI**.
3.  In the **Control Surface** list, find and select **AbletonMCP_Remote_Script**.
4.  Set **Input** and **Output** to **None**.
5.  *Verification*: You should see a status message in the bottom bar: `"AbletonMCP: Listening for commands..."`

### 3. Configure MCP Server
Add the following to your MCP settings configuration (e.g., in VS Code's `settings.json`):

```json
{
  "mcpServers": {
    "ableton-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "C:\\path\\to\\this\\repo",
        "ableton-mcp"
      ]
    }
  }
}
```
*Replace `C:\\path\\to\\this\\repo` with the actual absolute path.*

---

## 🤖 Agentic Workflows & Documentation

We have included comprehensive documentation to help agents navigate the codebase and the Ableton API.

### Agent Resources
| Resource | Purpose |
|:---|:---|
| `AGENTS.md` | **Master Guide**: Architecture, Critical Gotchas (EQ normalization!), and best practices. |
| `.agent/workflows/` | **30 Workflow Files**: Step-by-step guides for mixer ops, orchestration, chord generation, drum racks, and more. |
| `live_api_docs_download/` | Live 11 API XML docs for advanced/custom implementations. |

### Key Workflows (Slash Commands)
| Workflow | Description |
|:---|:---|
| `/load-device` | Load EQ, Compressor, instruments onto tracks |
| `/mixer-operations` | Control volume, pan, sends, mute/solo/arm |
| `/generate-chords` | Create chord progressions with music theory |
| `/orchestration` | Generate strings, brass, and woodwind parts |
| `/drum-patterns` | Generate drum patterns from library |
| `/song-blueprint` | Scaffold full song arrangements |
| `/automation` | Apply parameter automation ramps |

---

## 🎵 Usage Examples

With this setup, you can give high-level musical instructions:

**Composition:**
> "Generate a Jazz chord progression in C Minor, then create a walking bassline to match it."
> "Create a new MIDI track with a String Ensemble and generate a sad, cinematic melody."

**Arrangement:**
> "Create a song blueprint for a minimal techno track and lay out the empty clips."
> "Build the drum track for a Metro Boomin style hip-hop beat."

**Control:**
> "Solo the kick drum track and lower the volume by 3dB."
> "Add a Reverb to the snare track with a 2.5s decay time."

**Discovery:**
> "Search the browser for 'Grand Piano' and load the first result on track 1."

---

## 📂 Project Structure

```
.
├── AbletonMCP_Remote_Script/     # Runs INSIDE Ableton's Python
│   ├── __init__.py               # Entry point & Socket listener
│   └── handlers/                 # 21 modular API handlers
│       ├── track.py              # (101 KB) Track/Routing control
│       ├── device.py             # (66 KB) Device chain management
│       ├── clip.py               # (44 KB) Clip operations
│       └── ...
│
├── MCP_Server/                   # The MCP bridge
│   ├── server.py                 # 220+ MCP tool definitions
│   └── mcp_tooling/              # The Core Brain
│       ├── generators.py         # Music theory & MIDI generation
│       ├── chords.py             # 176+ chord progressions
│       ├── drummer.py            # 4.2MB drum pattern library access
│       ├── devices.py            # Smart device loading
│       └── theory.py             # Scales, intervals, voice leading
│
├── .agent/workflows/             # 30 agentic workflow documents
├── scripts/
│   ├── deploy.py                 # Auto-install Remote Script
│   └── doctor.ps1                # Health check utility
└── AGENTS.md                     # Master agent guide
```

---

## ⚠️ Critical Gotchas for Agents

These are documented in `AGENTS.md` but are important enough to highlight:

| Problem | ❌ Wrong | ✅ Correct |
|:---|:---|:---|
| EQ Frequency | `freq=180` (Hz) | `freq=0.299` (normalized) |
| EQ Gain | `gain=-3` (dB) | `gain=0.4` (normalized) |
| Track Detection | Hardcoded indices | Use `get_song_context` first! |

**Conversion Formulas:**
```python
# EQ Frequency (10 Hz - 22 kHz, logarithmic)
norm = log(freq_hz / 10) / log(2200)

# EQ Gain (-15 dB to +15 dB, linear)
norm = (db + 15) / 30
```

---

## 🩺 Troubleshooting

Run the doctor script from the repo root:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/doctor.ps1
```
This verifies: `uv`/Python availability, Remote Script folder, and TCP port status.

### Common Issues
*   **Connection Failed**: Ensure Ableton is running and the control surface is selected.
*   **No Sound / EQ Silence**: You likely sent raw Hz/dB values instead of normalized values.
*   **Script Not Loading After Changes**: After editing `AbletonMCP_Remote_Script`, you must restart Ableton completely (just toggling the control surface is NOT enough).

---

## Disclaimer
This project is an independent fork and not affiliated with Ableton. Use at your own risk during live performances!
