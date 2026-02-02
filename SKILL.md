---
name: claude-code-openclaw
description: "Drive Claude Code (Anthropic) on this Mac via the `claude` CLI. Use when you need reliable headless `claude -p` execution (TTY quirks), Plan Mode, tool allowlists (`--allowedTools`), structured output (`--output-format json`), or when integrating Claude Code into OpenClaw workflows/cron/tmux. Includes a Python wrapper that allocates a pseudo-terminal and an optional tmux interactive mode for slash commands."
---

# Claude Code（OpenClaw）

Use the locally installed **Claude Code** CLI reliably.

This skill supports two execution styles:
- **Headless mode** (non-interactive): best for normal prompts and structured output.
- **Interactive mode (tmux)**: best when you want **zero copy/paste + live demo visuals** (OpenClaw can answer permission prompts and keep the session moving), and is required for **slash commands** like `/speckit.*`.

Operational rule (Paul哥定案):
- **凡是要讓般弱真正「對 CC 發號司令」且避免你提醒** → 優先用 **interactive tmux**。
- 只在「短、一次性、無需互動」時才用 headless。

Model rule (Paul哥定案):
- **規劃階段**：先把 CC 切到 **Opus 4.5**（用 `/model` 或 `--model`），再送 plan 指令。
- **實作階段**：切到 **Sonnet 4.5** 再開始動手改碼。

This skill is for **driving the Claude Code CLI**, not the Claude API directly.

## Quick checks

Verify installation:
```bash
claude --version
```

Run a minimal headless prompt (prints a single response):
```bash
./scripts/claude_code_run.py -p "Return only the single word OK."
```

## Core workflow

### 1) Run a headless prompt in a repo

```bash
cd /path/to/repo
/Users/pauuul/clawd/skills/claude-code-openclaw/scripts/claude_code_run.py \
  -p "Summarize this project and point me to the key modules." \
  --permission-mode plan
```

### 2) Allow tools (auto-approve)

Claude Code supports tool allowlists via `--allowedTools`.
Example: allow read/edit + bash:
```bash
./scripts/claude_code_run.py \
  -p "Run the test suite and fix any failures." \
  --allowedTools "Bash,Read,Edit"
```

### 3) Get structured output

```bash
./scripts/claude_code_run.py \
  -p "Summarize this repo in 5 bullets." \
  --output-format json
```

### 4) Add extra system instructions

```bash
./scripts/claude_code_run.py \
  -p "Review the staged diff for security issues." \
  --append-system-prompt "You are a security engineer. Be strict." \
  --allowedTools "Bash(git diff *),Bash(git status *),Read"
```

## Notes (important)

- **After correcting Claude Code's mistakes**: Always instruct Claude Code to run:
  > "Update your CLAUDE.md so you don't make that mistake again."
  
  This ensures Claude Code records lessons learned and avoids repeating the same errors.

- Claude Code sometimes expects a TTY.
- **Headless**: this wrapper uses `script(1)` to force a pseudo-terminal.
- **Slash commands** (e.g. `/speckit.*`) are best run in **interactive** mode; this wrapper can start an interactive Claude Code session in **tmux**.
- Use `--permission-mode plan` when you want read-only planning.
- Keep `--allowedTools` narrow (principle of least privilege), especially in automation.

## High‑leverage Claude Code tips (from the official docs)

### 1) Always give Claude a way to verify (tests/build/screenshots)

Claude performs dramatically better when it can verify its work.
Make verification explicit in the prompt, e.g.:
- “Fix the bug **and run tests**. Done when `npm test` passes.”
- “Implement UI change, **take a screenshot** and compare to this reference.”

### 2) Explore → Plan → Implement (use Plan Mode)

For multi-step work, start in plan mode to do safe, read-only analysis:
```bash
./scripts/claude_code_run.py -p "Analyze and propose a plan" --permission-mode plan
```
Then switch to execution (`acceptEdits`) once the plan is approved.

### 3) Manage context aggressively: /clear and /compact

Long, mixed-topic sessions degrade quality.
- Use `/clear` between unrelated tasks.
- Use `/compact Focus on <X>` when nearing limits to preserve the right details.

### 4) Rewind aggressively: /rewind (checkpoints)

Claude checkpoints before changes.
If an approach is wrong, use `/rewind` (or Esc Esc) to restore:
- conversation only
- code only
- both

This enables “try something risky → rewind if wrong” loops.

### 5) Prefer CLAUDE.md for durable rules; keep it short

Best practice is a concise CLAUDE.md (global or per-project) for:
- build/test commands Claude should use
- repo etiquette / style rules that differ from defaults
- non-obvious environment quirks

Overlong CLAUDE.md files get ignored.

### 6) Permissions: deny > ask > allow (and scope matters)

In `.claude/settings.json` / `~/.claude/settings.json`, rules match in order:
**deny first**, then ask, then allow.
Use deny rules to block secrets (e.g. `.env`, `secrets/**`).

### 7) Bash env vars don’t persist; use CLAUDE_ENV_FILE for persistence

Each Bash tool call runs in a fresh shell; `export FOO=bar` won’t persist.
If you need persistent env setup, set (before starting Claude Code):
```bash
export CLAUDE_ENV_FILE=/path/to/env-setup.sh
```
Claude will source it before each Bash command.

### 8) Hooks beat “please remember” instructions

Use hooks to enforce deterministic actions (format-on-edit, block writes to sensitive dirs, etc.)
when you need guarantees.

### 9) Use subagents for heavy investigation / independent review

Subagents can read many files without polluting the main context.
Use them for broad codebase research or post-implementation review.

### 10) Treat Claude as a Unix utility (headless, pipes, structured output)

Examples:
```bash
cat build-error.txt | claude -p "Explain root cause" 
claude -p "List endpoints" --output-format json
```
This is ideal for CI and automation.

## Interactive mode (tmux)

If your prompt contains lines starting with `/` (slash commands), the wrapper defaults to **auto → interactive**.

Example:

```bash
./scripts/claude_code_run.py \
  --mode auto \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/speckit.constitution ...\n/speckit.specify ...\n/speckit.plan ...\n/speckit.tasks\n/speckit.implement'
```

It will print tmux attach/capture commands so you can monitor progress.

## Spec Kit end-to-end workflow (tips that prevent hangs)

When you want Claude Code to drive **Spec Kit** end-to-end via `/speckit.*`, do **not** use headless `-p` for the whole flow.
Use **interactive tmux mode** because:
- Spec Kit runs multiple steps (Bash + file writes + git) and may pause for confirmations.
- Headless runs can appear idle and be killed (SIGKILL) by supervisors.

### Prerequisites (important)

1) **Initialize Spec Kit** (once per repo)
```bash
specify init . --ai claude
```

2) Ensure the folder is a real git repo (Spec Kit uses git branches/scripts):
```bash
git init
git add -A
git commit -m "chore: init"
```

3) Recommended: set an `origin` remote (can be a local bare repo) so `git fetch --all --prune` won’t behave oddly:
```bash
git init --bare ../origin.git
git remote add origin ../origin.git
git push -u origin main || git push -u origin master
```

4) Give Claude Code enough tool permissions for the workflow:
- Spec creation/tasks/implement need file writes, so include **Write**.
- Implementation often needs Bash.

Recommended:
```bash
--permission-mode acceptEdits --allowedTools "Bash,Read,Edit,Write"
```

### Run the full Spec Kit pipeline

```bash
./scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session cc-speckit \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/speckit.constitution Create project principles for quality, accessibility, and security.\n/speckit.specify <your feature description>\n/speckit.plan I am building with <your stack/constraints>\n/speckit.tasks\n/speckit.implement'
```

### Monitoring / interacting

The wrapper prints commands like:
- `tmux ... attach -t <session>` to watch in real time
- `tmux ... capture-pane ...` to snapshot output

If Claude Code asks a question mid-run (e.g., “Proceed?”), attach and answer.

## 🔄 Skill 自我進化規則

**每次操作 CC 遇到問題並找到解決方案時，必須立即更新此 SKILL.md。**

這包括但不限於：
- 新的卡住模式 → 更新監控腳本
- 新的確認提示格式 → 加入偵測條件
- 新的 gotcha/踩坑 → 加入 Operational gotchas
- 更好的工作流程 → 更新操作守則
- CC 版本更新導致的行為變化 → 記錄版本差異

## ⚠️ 般若 vs CC 的界線

**這份 skill 是般若的操作手冊，不是給 CC 看的。**

- **般若 → CC**：只給技術指令（任務描述、程式碼要求）
- **Paul哥 的話**：般若先消化理解，轉化成行動，不原封不動丟給 CC
- **Commit message**：只寫技術內容（feat/fix/chore），不寫般若的內部規則
- **內部規則**：只存在 clawd/ 的文件（不讓 CC 在 git log 看到）

---

## 般若操作守則（Paul哥校準）

### 主動監控 CC session
- CC 在 tmux 跑起來後，**般若要主動定期檢查**（不等 Paul哥 提醒）
- 用 `cc_monitor.py --once` 或直接 `tmux capture-pane` 掃輸出
- 看到確認提示 → 立即回答（安全的自動、不確定的問 Paul哥）
- 看到 CC 提問（如架構決策）→ 以「專案負責人」角色代答

### 決策代答原則
當 CC 詢問專案決策時，般若應根據以下優先順序回答：
1. **已有明確指示**：照 Paul哥 說的做
2. **技術最佳實務**：選推薦選項（通常是選項 1）
3. **符合專案方向**：考量現有架構、Paul哥 的設計偏好
4. **不確定**：問 Paul哥

### 不要讓 CC 空轉
- CC 卡住 = 浪費時間 = Paul哥 不滿
- 每次送 prompt 給 CC 後，至少追蹤到它開始執行或完成
- 如果 CC 停超過 2 分鐘沒動靜，主動檢查

### ⚠️ 啟動背景監控迴圈（必做）
CC 開始跑長任務時，**必須同時啟動背景監控**，不能只手動檢查幾次就停。

**完整監控腳本（處理確認提示 + 開放式問題）：**

```bash
SOCKET_PATH="<tmux socket path>"
SESSION="<session name>"  # 例如 mc-cc

for i in {1..60}; do
  output=$(tmux -S "$SOCKET_PATH" capture-pane -t ${SESSION}:0.0 -p -S -35 2>/dev/null || echo "")
  
  # 1) 標準確認提示：自動回答 2（Yes, and don't ask again）
  if echo "$output" | grep -qE "Do you want to proceed\?|Do you want to create"; then
    echo "[$(date +%H:%M:%S)] 偵測到確認提示，自動回答 2..."
    tmux -S "$SOCKET_PATH" send-keys -t ${SESSION}:0.0 "2"
    tmux -S "$SOCKET_PATH" send-keys -t ${SESSION}:0.0 Enter
  
  # 2) 開放式決策問題：CC 問「要繼續嗎」等問題且等待輸入
  elif echo "$output" | grep -qE "要繼續嗎|建議暫停|Would you like|continue\?" && echo "$output" | tail -5 | grep -q "^❯ *$"; then
    echo "[$(date +%H:%M:%S)] 偵測到決策問題，回答繼續..."
    tmux -S "$SOCKET_PATH" send-keys -t ${SESSION}:0.0 -l "yes, continue"
    tmux -S "$SOCKET_PATH" send-keys -t ${SESSION}:0.0 Enter
  
  # 3) CC 完全停住（輸入框空白超過 30 秒且沒有 thinking/running 指示）
  elif echo "$output" | tail -3 | grep -q "^❯ *$" && ! echo "$output" | grep -qE "thinking|Running|Waiting|Forming|Churning"; then
    echo "[$(date +%H:%M:%S)] CC 可能卡住，送 Enter 嘗試推進..."
    tmux -S "$SOCKET_PATH" send-keys -t ${SESSION}:0.0 Enter
  fi
  
  sleep 10
done
echo "監控結束"
```

**監控要點：**
1. **確認提示** → 自動回答 `2`（允許且不再詢問）
2. **開放式問題** → 回答 `yes, continue`
3. **空白卡住** → 送 Enter 推進
4. **每 10 秒檢查一次**，持續 10 分鐘（可調整）

這樣才不會讓 Paul哥 一直提醒「CC 又在等你了」。

### Context 管理最佳實務（官方文件摘要）

根據 [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)：

**核心原則：Context window 是最重要的資源**
- Context 滿了會導致 CC 「忘記」指令或犯更多錯
- 長 session 混雜無關內容會降低效能

**主動管理策略：**
1. **`/clear` 清除無關內容**：在不同任務之間使用，完全重置 context
2. **`/compact <focus>` 壓縮並保留重點**：例如 `/compact Focus on the API changes`
3. **用 subagent 做調查**：讓 subagent 讀大量檔案，回報摘要，不污染主 context
4. **Auto-compaction**：CC 接近限制時會自動壓縮，保留重要的 code patterns、file states、key decisions

**避免的失敗模式：**
- ❌ **Kitchen sink session**：一個 session 混雜多個不相關任務 → 用 `/clear` 分隔
- ❌ **反覆修正**：CC 做錯、修正、還是錯、再修正 → 兩次失敗後 `/clear` 重新開始，寫更好的 prompt
- ❌ **無限探索**：讓 CC「調查」但沒設範圍，讀了幾百個檔案 → 縮小範圍或用 subagent

**般若應用：**
- 當 OpenClaw session context 剩 < 20%：**自己決定** — 把重要內容寫入記憶檔，然後讓 session compact（不用問 Paul哥）
- 當派工給 CC 的任務很長：分階段、用 `/clear` 切開
- 當 CC 在同一問題上失敗 2 次：停下來，重新設計 prompt

## Operational gotchas (learned in practice)

### 1) Vite + ngrok: "Blocked request. This host (...) is not allowed"

If you expose a Vite dev server through ngrok, Vite will block unknown Host headers unless configured.

- **Vite 7** expects `server.allowedHosts` to be `true` or `string[]`.
  - ✅ Allow all hosts (quick):
    ```ts
    server: { host: true, allowedHosts: true }
    ```
  - ✅ Allow just your ngrok host (safer):
    ```ts
    server: { host: true, allowedHosts: ['xxxx.ngrok-free.app'] }
    ```
  - ❌ Do **not** set `allowedHosts: 'all'` (won't work in Vite 7).

After changing `vite.config.*`, restart the dev server.

### 2) Don’t accidentally let your *shell* eat your prompt

When you drive tmux via a shell command (e.g. `tmux send-keys ...`), avoid unescaped **backticks** and shell substitutions in the text you pass.
They can be interpreted by your shell before the text even reaches Claude Code.

Practical rule:
- Prefer sending prompts from a file, or ensure the wrapper/script quotes prompt text safely.

### 3) Long-running dev servers should run in a persistent session

In automation environments, backgrounded `vite` / `ngrok` processes can get SIGKILL.
Prefer running them in a managed background session (Clawdbot exec background) or tmux, and explicitly stop them when done.

## OpenSpec workflow (opsx)

OpenSpec is another spec-driven workflow (like Spec Kit) powered by slash commands (e.g. `/opsx:*`).
In practice it has the same reliability constraints:
- Prefer **interactive tmux mode** for `/opsx:*` commands (avoid headless `-p` for the whole flow).

### Setup (per machine)

Install CLI:
```bash
npm install -g @fission-ai/openspec@latest
```

### Setup (per project)

Initialize OpenSpec **with tool selection** (required):
```bash
openspec init --tools claude
```

Tip: disable telemetry if desired:
```bash
export OPENSPEC_TELEMETRY=0
```

### Recommended end-to-end command sequence

Inside Claude Code (interactive):
1) `/opsx:onboard`
2) `/opsx:new <change-name>`
3) `/opsx:ff` (fast-forward: generates proposal/design/specs/tasks)
4) `/opsx:apply` (implements tasks)
5) `/opsx:archive` (optional: archive finished change)

If the UI prompts you for project type/stack, answer explicitly (e.g. “Web app (HTML/JS) with localStorage”).

## Bundled scripts

- `scripts/claude_code_run.py`: wrapper that runs the local `claude` binary with a pseudo-terminal and forwards flags.
- `scripts/cc_monitor.py`: **監控腳本** — 檢查 Claude Code tmux session 是否卡在等待確認（如 "Do you want to proceed?"）。

### cc_monitor.py 使用方式

**單次檢查（適合 heartbeat / cron）：**
```bash
python scripts/cc_monitor.py --once --auto-answer
```

**持續監控（背景執行，每 5 分鐘檢查）：**
```bash
python scripts/cc_monitor.py --interval 300 --auto-answer &
```

**輸出 JSON（供 OpenClaw 解析）：**
```bash
python scripts/cc_monitor.py --once --json
```

### 自動回答的確認類型

cc_monitor 可以自動回答以下「安全」的確認：
- `Do you want to proceed?` → 回答 `1` (Yes)
- `Yes, and don't ask again for...` → 回答 `2` (永久允許該 workspace)
- `Yes, I trust this folder` → 回答 `1`
- `[Y/n]` → 回答 `Y`
- `Press Enter to continue` → 送出 Enter

如果偵測到無法自動處理的確認，會輸出通知讓般若轉達 Paul哥。

### 整合到 OpenClaw heartbeat

在 `HEARTBEAT.md` 加入：
```markdown
## Claude Code 監控
- 每次 heartbeat 執行：`python /Users/pauuul/clawd/skills/claude-code-openclaw/scripts/cc_monitor.py --once --auto-answer`
- 如果有無法自動處理的確認，通知 Paul哥
```
