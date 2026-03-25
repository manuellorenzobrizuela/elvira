<h1 align="center">Elvira</h1>

<p align="center">
  Voice interface for Claude Code — hear responses, speak commands.
  <br>
  Neural TTS (Microsoft Edge) + Windows dictation for hands-free coding.
</p>

---

## What is this?

Elvira adds a voice layer to [Claude Code](https://docs.anthropic.com/en/docs/claude-code) in VSCode. Claude's responses are read aloud using Microsoft's neural voice engine. Combined with Windows dictation (`Win+H`), you can have full voice conversations with Claude while coding.

**No API keys. No accounts. No cost.** Uses Microsoft Edge TTS (free neural voices) and Windows native dictation.

## Demo

```
You: [speak] "Explícame qué hace este endpoint"
Claude: [types response on screen]
Elvira: [reads response aloud with neural voice]
You: [speak] "Cambia el status code a 404"
Claude: [makes the change]
Elvira: "Hecho. He cambiado el status code a 404 en la línea 42."
```

## How it works

1. **You speak** → `Win+H` activates Windows dictation → your words become text in Claude Code
2. **Claude responds** → text appears on screen as usual
3. **Elvira reads** → a Claude Code hook captures the response, filters out code/markdown, and reads the conversational text aloud
4. **Toggle** → `Ctrl+Shift+H` to enable/disable voice

### Smart filtering

Elvira only reads what matters. It automatically skips:
- Code blocks and inline code
- Terminal commands, imports, paths
- Markdown tables, links, formatting
- JSON objects, HTML tags
- Technical symbols that sound bad when narrated

## Installation

### Prerequisites

- Windows 10/11
- Python 3.8+
- VSCode with Claude Code
- Internet connection (Edge TTS generates audio online)

### Setup

```bash
# 1. Install edge-tts
pip install edge-tts

# 2. Clone this repo
git clone https://github.com/manuellorenzobrizuela/elvira.git

# 3. Copy hooks to Claude config
mkdir -p ~/.claude/hooks
cp elvira/tts-response.py ~/.claude/hooks/
cp elvira/tts-response.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/tts-response.sh
```

### Configure Claude Code hook

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/tts-response.sh",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### Configure toggle shortcut

Add to VSCode `keybindings.json`:

```json
{
  "key": "ctrl+shift+h",
  "command": "workbench.action.tasks.runTask",
  "args": "Toggle Claude TTS"
}
```

See [CLAUDE.md](CLAUDE.md) for the full `tasks.json` configuration.

## Available voices

```bash
python -m edge_tts --list-voices | grep "es-ES"
```

| Voice | Gender | Default |
|-------|--------|---------|
| es-ES-ElviraNeural | Female | Yes |
| es-ES-AlvaroNeural | Male | |
| es-ES-XimenaNeural | Female | |

Change the voice in `tts-response.py` (`--voice` parameter). Any [Edge TTS voice](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support) works — English, German, French, etc.

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Voice | `tts-response.py` line 133 | `es-ES-ElviraNeural` |
| Speed | `tts-response.py` `--rate` | `+15%` |
| Max length | `tts-response.py` line 33 | 1000 chars |
| Toggle | `~/.claude/hooks/tts-enabled` | File exists = ON |

## Architecture

```
[You speak] → Win+H dictation → Claude Code input
                                       ↓
                                 Claude responds
                                       ↓
                              Hook: Stop event fires
                                       ↓
                    tts-response.sh → tts-response.py
                                       ↓
                         Filter markdown/code → clean text
                                       ↓
                         edge-tts → MP3 (neural voice)
                                       ↓
                       PowerShell MediaPlayer → speaker
```

3 files. No dependencies beyond `edge-tts`. No daemon. No background process. Runs only when Claude finishes a response.

## License

MIT

## Author

Built for hands-free coding with Claude Code.
