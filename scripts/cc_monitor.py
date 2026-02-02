#!/usr/bin/env python3
"""Claude Code tmux session monitor.

Periodically checks running Claude Code tmux sessions for prompts that need
human/agent confirmation (e.g., "Do you want to proceed?", "Yes, I trust this folder").

When a confirmation is detected:
1. Attempts auto-answer if it's a safe pattern (e.g., proceed with tool use).
2. Otherwise, outputs a notification for OpenClaw to relay to Paul哥.

Usage:
  # One-shot check (for cron/heartbeat)
  python cc_monitor.py --once

  # Continuous monitoring (every 5 minutes)
  python cc_monitor.py --interval 300

  # Auto-answer mode (unattended)
  python cc_monitor.py --auto-answer --interval 300
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Default socket dir (same as claude_code_run.py)
DEFAULT_SOCKET_DIR = os.environ.get("CLAWDBOT_TMUX_SOCKET_DIR") or f"{os.environ.get('TMPDIR', '/tmp')}/clawdbot-tmux-sockets"
DEFAULT_SOCKET_NAME = "claude-code.sock"

# Patterns that indicate Claude Code is waiting for confirmation
CONFIRMATION_PATTERNS = [
    # Tool use confirmations
    (r"Do you want to proceed\?", "tool_confirm", "1"),  # Select "1. Yes"
    (r"1\.\s*Yes\s*\n\s*2\.\s*Yes,\s*and\s*don't\s*ask\s*again", "tool_confirm_menu", "2"),  # Auto-approve for workspace
    # Trust prompts
    (r"Yes,\s*I\s*trust\s*this\s*folder", "trust_folder", "1"),
    # Generic Y/N
    (r"\[Y/n\]\s*$", "yn_prompt", "Y"),
    (r"\[y/N\]\s*$", "yn_prompt_default_no", "n"),  # Don't auto-answer if default is No
    # Waiting for input (generic)
    (r"Press\s+Enter\s+to\s+continue", "press_enter", ""),
]

# Patterns that indicate Claude Code is actively working (not stuck)
WORKING_PATTERNS = [
    r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏",  # Spinner
    r"Reading|Writing|Executing|Analyzing|Planning",
    r"\.\.\.$",  # Trailing ellipsis (processing)
]

@dataclass
class SessionStatus:
    session_name: str
    socket_path: str
    last_output: str = ""
    waiting_for: Optional[str] = None
    pattern_type: Optional[str] = None
    suggested_answer: Optional[str] = None
    is_working: bool = False
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat())


def tmux_cmd(socket_path: str, *args: str) -> list[str]:
    return ["tmux", "-S", socket_path, *args]


def list_sessions(socket_path: str) -> list[str]:
    """List all tmux sessions on the given socket."""
    try:
        out = subprocess.check_output(
            tmux_cmd(socket_path, "list-sessions", "-F", "#{session_name}"),
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return [s.strip() for s in out.splitlines() if s.strip()]
    except subprocess.CalledProcessError:
        return []


def capture_pane(socket_path: str, session: str, lines: int = 100) -> str:
    """Capture the last N lines from a tmux pane."""
    target = f"{session}:0.0"
    try:
        out = subprocess.check_output(
            tmux_cmd(socket_path, "capture-pane", "-p", "-J", "-t", target, "-S", f"-{lines}"),
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out
    except subprocess.CalledProcessError:
        return ""


def send_keys(socket_path: str, session: str, keys: str, literal: bool = True) -> bool:
    """Send keystrokes to a tmux session."""
    target = f"{session}:0.0"
    try:
        cmd = tmux_cmd(socket_path, "send-keys", "-t", target)
        if literal and keys:
            cmd += ["-l", "--", keys]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Send Enter after the keys
        subprocess.check_call(
            tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_session(socket_path: str, session: str) -> SessionStatus:
    """Check a single session for confirmation prompts."""
    status = SessionStatus(session_name=session, socket_path=socket_path)
    
    output = capture_pane(socket_path, session, lines=50)
    status.last_output = output
    
    # Check if actively working
    for pattern in WORKING_PATTERNS:
        if re.search(pattern, output):
            status.is_working = True
            break
    
    # Check for confirmation patterns (only in last ~20 lines to avoid old matches)
    recent_output = "\n".join(output.splitlines()[-20:])
    
    for pattern, ptype, answer in CONFIRMATION_PATTERNS:
        if re.search(pattern, recent_output, re.IGNORECASE | re.MULTILINE):
            status.waiting_for = pattern
            status.pattern_type = ptype
            status.suggested_answer = answer
            status.is_working = False  # Override: it's waiting, not working
            break
    
    return status


def auto_answer(status: SessionStatus) -> bool:
    """Attempt to auto-answer a confirmation prompt."""
    if not status.waiting_for or not status.suggested_answer:
        return False
    
    # Safety: don't auto-answer if default is No
    if status.pattern_type == "yn_prompt_default_no":
        return False
    
    return send_keys(status.socket_path, status.session_name, status.suggested_answer)


def format_notification(status: SessionStatus) -> str:
    """Format a notification message for Paul哥."""
    lines = [
        f"⚠️ Claude Code 等待確認",
        f"Session: {status.session_name}",
        f"類型: {status.pattern_type}",
        "",
        "最後輸出 (截取):",
        "```",
        "\n".join(status.last_output.splitlines()[-15:]),
        "```",
        "",
        f"建議回答: {status.suggested_answer}" if status.suggested_answer else "需要手動處理",
    ]
    return "\n".join(lines)


def run_check(socket_dir: str, socket_name: str, auto_answer_mode: bool = False) -> list[SessionStatus]:
    """Run a single check cycle."""
    socket_path = str(Path(socket_dir) / socket_name)
    
    if not Path(socket_path).exists():
        return []
    
    sessions = list_sessions(socket_path)
    results = []
    
    for session in sessions:
        status = check_session(socket_path, session)
        
        if status.waiting_for:
            if auto_answer_mode:
                answered = auto_answer(status)
                if answered:
                    print(f"[cc_monitor] Auto-answered {status.pattern_type} in session {session}", file=sys.stderr)
                    status.waiting_for = None  # Clear after answering
                else:
                    # Couldn't auto-answer, need notification
                    results.append(status)
            else:
                results.append(status)
    
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Monitor Claude Code tmux sessions for confirmation prompts")
    
    ap.add_argument("--socket-dir", default=DEFAULT_SOCKET_DIR, help="tmux socket directory")
    ap.add_argument("--socket-name", default=DEFAULT_SOCKET_NAME, help="tmux socket file name")
    ap.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300 = 5 min)")
    ap.add_argument("--once", action="store_true", help="Run once and exit")
    ap.add_argument("--auto-answer", action="store_true", help="Automatically answer safe confirmation prompts")
    ap.add_argument("--json", action="store_true", help="Output results as JSON")
    ap.add_argument("--notify-file", help="Write notifications to this file (for OpenClaw pickup)")
    
    args = ap.parse_args()
    
    def do_check():
        results = run_check(args.socket_dir, args.socket_name, args.auto_answer)
        
        if results:
            if args.json:
                out = [
                    {
                        "session": s.session_name,
                        "pattern_type": s.pattern_type,
                        "suggested_answer": s.suggested_answer,
                        "checked_at": s.checked_at,
                        "last_lines": s.last_output.splitlines()[-15:],
                    }
                    for s in results
                ]
                print(json.dumps(out, ensure_ascii=False, indent=2))
            else:
                for status in results:
                    print(format_notification(status))
                    print("---")
            
            if args.notify_file:
                Path(args.notify_file).parent.mkdir(parents=True, exist_ok=True)
                with open(args.notify_file, "w") as f:
                    for status in results:
                        f.write(format_notification(status))
                        f.write("\n---\n")
        
        return len(results)
    
    if args.once:
        count = do_check()
        return 0 if count == 0 else 1
    
    # Continuous monitoring
    print(f"[cc_monitor] Starting continuous monitoring (interval: {args.interval}s, auto-answer: {args.auto_answer})", file=sys.stderr)
    
    while True:
        try:
            do_check()
        except Exception as e:
            print(f"[cc_monitor] Error: {e}", file=sys.stderr)
        
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
