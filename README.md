<div align="center">
  <h1><img src="https://api.iconify.design/lucide/terminal.svg?color=%23c084fc" width="32" height="32" /> CC-OpenClaw Skill</h1>
  <p><strong>Drive Claude Code CLI reliably from OpenClaw</strong></p>
  <p>A skill for OpenClaw that provides reliable headless and interactive execution of Claude Code, with monitoring scripts and battle-tested workflows.</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-purple" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

<p align="center">
  <strong>English</strong> • <a href="README_zh-TW.md">繁體中文</a> • <a href="README_zh-CN.md">简体中文</a>
</p>

---

### <img src="https://api.iconify.design/lucide/alert-circle.svg?color=%23f87171" width="18" height="18" /> The Problem

Claude Code CLI sometimes hangs waiting for confirmations, permission prompts, or user input. When running automated workflows, these hangs cause:
- Wasted time waiting for manual intervention
- Broken automation pipelines
- Frustrated users

### <img src="https://api.iconify.design/lucide/lightbulb.svg?color=%23fbbf24" width="18" height="18" /> The Solution

This skill provides:
- **Headless execution** with pseudo-TTY allocation (handles TTY quirks)
- **Interactive tmux mode** for slash commands and long-running tasks
- **Monitoring scripts** that auto-answer common confirmation prompts
- **Battle-tested workflows** for Spec Kit and OpenSpec

### <img src="https://api.iconify.design/lucide/download.svg?color=%2360a5fa" width="18" height="18" /> Installation

Copy the skill to your OpenClaw skills directory:

```bash
git clone https://github.com/Pauuulq87/cc-openclaw-skill.git ~/.openclaw/skills/cc-openclaw
```

Or add to your OpenClaw config:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["~/.openclaw/skills"]
    }
  }
}
```

### <img src="https://api.iconify.design/lucide/settings.svg?color=%2360a5fa" width="18" height="18" /> Prerequisites

- [Claude Code CLI](https://github.com/anthropics/claude-code) installed and authenticated
- Python 3.10+
- tmux (for interactive mode)

### <img src="https://api.iconify.design/lucide/play.svg?color=%2334d399" width="18" height="18" /> Usage

**Headless prompt:**
```bash
./scripts/claude_code_run.py -p "Summarize this project"
```

**With tool permissions:**
```bash
./scripts/claude_code_run.py \
  -p "Fix the failing tests" \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit"
```

**Interactive tmux mode:**
```bash
./scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session my-session \
  -p "Run the full workflow"
```

**Monitor for stuck prompts:**
```bash
python scripts/cc_monitor.py --once --auto-answer
```

### <img src="https://api.iconify.design/lucide/rocket.svg?color=%23a78bfa" width="18" height="18" /> Advanced

See `SKILL.md` for:
- Spec Kit end-to-end workflow
- OpenSpec workflow
- Context management best practices
- Operational gotchas

---

<div align="center">
  <p><strong>MIT License</strong> - Made with care for AI-powered developers.</p>
  <p><em>Thanks to all GitHub developers who share their wisdom and experience — you made this possible.</em></p>
  <p>Forked from <a href="https://github.com/win4r/claude-code-clawdbot-skill">win4r/claude-code-clawdbot-skill</a></p>
</div>
