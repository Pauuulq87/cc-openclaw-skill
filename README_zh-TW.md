<div align="center">
  <h1><img src="https://api.iconify.design/lucide/terminal.svg?color=%23c084fc" width="32" height="32" /> CC-OpenClaw Skill</h1>
  <p><strong>從 OpenClaw 可靠地驅動 Claude Code CLI</strong></p>
  <p>一個 OpenClaw 技能，提供可靠的 Claude Code 無頭執行與互動模式，包含監控腳本與實戰驗證的工作流程。</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-purple" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

<p align="center">
  <a href="README.md">English</a> • <strong>繁體中文</strong> • <a href="README_zh-CN.md">简体中文</a>
</p>

---

### <img src="https://api.iconify.design/lucide/alert-circle.svg?color=%23f87171" width="18" height="18" /> 痛點

Claude Code CLI 有時會卡在等待確認、權限提示或使用者輸入。在自動化工作流程中，這些卡頓會導致：
- 浪費時間等待手動介入
- 自動化流程中斷
- 使用者體驗不佳

### <img src="https://api.iconify.design/lucide/lightbulb.svg?color=%23fbbf24" width="18" height="18" /> 解決方案

這個技能提供：
- **無頭執行**：自動配置偽終端（處理 TTY 問題）
- **互動式 tmux 模式**：適用於 slash 指令和長時間任務
- **監控腳本**：自動回答常見的確認提示
- **實戰驗證的工作流程**：Spec Kit 和 OpenSpec

### <img src="https://api.iconify.design/lucide/download.svg?color=%2360a5fa" width="18" height="18" /> 安裝

將技能複製到 OpenClaw 技能目錄：

```bash
git clone https://github.com/Pauuulq87/cc-openclaw-skill.git ~/.openclaw/skills/cc-openclaw
```

或在 OpenClaw 設定中加入：

```json
{
  "skills": {
    "load": {
      "extraDirs": ["~/.openclaw/skills"]
    }
  }
}
```

### <img src="https://api.iconify.design/lucide/settings.svg?color=%2360a5fa" width="18" height="18" /> 前置需求

- 已安裝並認證的 [Claude Code CLI](https://github.com/anthropics/claude-code)
- Python 3.10+
- tmux（互動模式需要）

### <img src="https://api.iconify.design/lucide/play.svg?color=%2334d399" width="18" height="18" /> 使用方式

**無頭執行：**
```bash
./scripts/claude_code_run.py -p "總結這個專案"
```

**帶工具權限：**
```bash
./scripts/claude_code_run.py \
  -p "修復失敗的測試" \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit"
```

**互動式 tmux 模式：**
```bash
./scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session my-session \
  -p "執行完整工作流程"
```

**監控卡住的提示：**
```bash
python scripts/cc_monitor.py --once --auto-answer
```

### <img src="https://api.iconify.design/lucide/rocket.svg?color=%23a78bfa" width="18" height="18" /> 進階用法

詳見 `SKILL.md`：
- Spec Kit 端到端工作流程
- OpenSpec 工作流程
- Context 管理最佳實務
- 實戰踩坑紀錄

---

<div align="center">
  <p><strong>MIT License</strong> - 專為 AI 驅動的開發者打造。</p>
  <p><em>謝謝 GitHub 開發者把智慧與經驗分享出來，才有今天的我。</em></p>
  <p>Fork 自 <a href="https://github.com/win4r/claude-code-clawdbot-skill">win4r/claude-code-clawdbot-skill</a></p>
</div>
