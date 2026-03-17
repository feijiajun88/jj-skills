---
name: ai-daily-digest
description: 从 Andrej Karpathy 推荐的 90 个顶级技术博客中抓取最新文章，通过 AI 多维评分筛选，生成一份结构化的每日精选日报。默认使用 Gemini，并支持自动降级到 OpenAI 兼容 API。
license: MIT
github_url: https://github.com/vigorX777/ai-daily-digest
github_hash: 1f484a3f2f101cb0f1a94a35b1a1befe0f672b82
version: 0.1.0
created_at: 2026-02-26T00:00:00
entry_point: scripts/digest.ts
dependencies: ["bun"]
---

# AI Daily Digest 技能

从 Andrej Karpathy 推荐的 90 个顶级技术博客中抓取最新文章，通过 AI 多维评分筛选，生成一份结构化的每日精选日报。

## 项目来源

- **GitHub**: https://github.com/vigorX777/ai-daily-digest
- **公众号**: 懂点儿AI

## 功能特点

1. **五步处理流水线**:
   - RSS 抓取
   - 时间过滤
   - AI 评分 + 分类
   - AI 摘要 + 翻译
   - 趋势总结

2. **六大分类**:
   - 🤖 AI / ML
   - 🔒 安全
   - ⚙️ 工程
   - 🛠 工具 / 开源
   - 💡 观点 / 杂谈
   - 📝 其他

3. **结构化输出**:
   - 今日看点
   - 今日必读
   - 数据概览（Mermaid 饼图/柱状图、ASCII 图表、标签云）
   - 分类文章列表

## 使用方法

### 作为 OpenCode Skill

在支持 OpenCode 的对话环境中输入 `/digest` 启动交互式引导流程。

### 命令行运行

```bash
npx -y bun scripts/digest.ts --hours 48 --top-n 15 --lang zh --output ./digest.md
```

### 环境变量

需提前设置:
- `GEMINI_API_KEY` - Gemini API 密钥
- 或 OpenAI 兼容的 API 密钥

## 技术亮点

- 零依赖（纯 TypeScript，基于 Bun 运行时）
- 中英双语支持（标题自动翻译）
- 配置记忆（API Key 和参数持久化）
- 可灵活切换 AI 模型提供商

## 信息源

来自 Hacker News Popularity Contest 2025，涵盖:
- simonwillison.net
- paulgraham.com
- overreacted.io (Dan Abramov)
- 等 90+ 个顶级技术博客
