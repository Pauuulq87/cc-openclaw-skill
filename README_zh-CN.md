<div align="center">
  <h1><img src="https://api.iconify.design/lucide/terminal.svg?color=%23c084fc" width="32" height="32" /> CC-OpenClaw Skill</h1>
  <p><strong>从 OpenClaw 可靠地驱动 Claude Code CLI</strong></p>
  <p>一个 OpenClaw 技能，提供可靠的 Claude Code 无头执行与交互模式，包含监控脚本与实战验证的工作流程。</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-purple" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

<p align="center">
  <a href="README.md">English</a> • <a href="README_zh-TW.md">繁體中文</a> • <strong>简体中文</strong>
</p>

---

### <img src="https://api.iconify.design/lucide/alert-circle.svg?color=%23f87171" width="18" height="18" /> 痛点

Claude Code CLI 有时会卡在等待确认、权限提示或用户输入。在自动化工作流程中，这些卡顿会导致：
- 浪费时间等待手动介入
- 自动化流程中断
- 用户体验不佳

### <img src="https://api.iconify.design/lucide/lightbulb.svg?color=%23fbbf24" width="18" height="18" /> 解决方案

这个技能提供：
- **无头执行**：自动配置伪终端（处理 TTY 问题）
- **交互式 tmux 模式**：适用于 slash 指令和长时间任务
- **监控脚本**：自动回答常见的确认提示
- **实战验证的工作流程**：Spec Kit 和 OpenSpec

### <img src="https://api.iconify.design/lucide/download.svg?color=%2360a5fa" width="18" height="18" /> 安装

将技能复制到 OpenClaw 技能目录：

```bash
git clone https://github.com/Pauuulq87/cc-openclaw-skill.git ~/.openclaw/skills/cc-openclaw
```

或在 OpenClaw 配置中加入：

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

- 已安装并认证的 [Claude Code CLI](https://github.com/anthropics/claude-code)
- Python 3.10+
- tmux（交互模式需要）

### <img src="https://api.iconify.design/lucide/play.svg?color=%2334d399" width="18" height="18" /> 使用方式

**无头执行：**
```bash
./scripts/claude_code_run.py -p "总结这个项目"
```

**带工具权限：**
```bash
./scripts/claude_code_run.py \
  -p "修复失败的测试" \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit"
```

**交互式 tmux 模式：**
```bash
./scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session my-session \
  -p "执行完整工作流程"
```

**监控卡住的提示：**
```bash
python scripts/cc_monitor.py --once --auto-answer
```

### <img src="https://api.iconify.design/lucide/rocket.svg?color=%23a78bfa" width="18" height="18" /> 进阶用法

详见 `SKILL.md`：
- Spec Kit 端到端工作流程
- OpenSpec 工作流程
- Context 管理最佳实践
- 实战踩坑记录

---

<div align="center">
  <p><strong>MIT License</strong> - 专为 AI 驱动的开发者打造。</p>
  <p><em>谢谢 GitHub 开发者把智慧与经验分享出来，才有今天的我。</em></p>
  <p>Fork 自 <a href="https://github.com/win4r/claude-code-clawdbot-skill">win4r/claude-code-clawdbot-skill</a></p>
</div>
