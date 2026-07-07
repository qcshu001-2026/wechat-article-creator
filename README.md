# wechat-article-creator

公众号文章**全流程创作**技能（CodeBuddy Skill）。覆盖从**选题 → 写稿 → 配图 → 排版 → 去 AI 痕 → 发布**的 6 个环节，每个环节可独立执行，也可全流程串联。

> ⚠️ 本技能为 **CodeBuddy（WorkBuddy）专属格式**，依赖 `allowed-tools`、`connect_cloud_service`、`ToolSearch`/`DeferExecuteTool`、`Skill`、`AskUserQuestion` 等平台原语，以及 `ImageGen` / `humanizer` / `wechat-article-search` 等协作技能。直接移植到其它 Agent 平台（如 Trae、Claude Code）需要适配编排层，未做跨平台兼容。

## 功能环节

| 环节 | 说明 | 是否依赖外部 |
|------|------|------------|
| 1. 智能选题 | 根据热点与账号定位生成 3-5 个带差异化角度的选题建议 | WebSearch（可选 `wechat-article-search`） |
| 2. AI 写稿 | 生成标题、大纲、初稿，支持多轮迭代修改 | 纯 LLM |
| 3. 自动配图 | 生成封面图（2.35:1、1:1）与内页插图 | ImageGen（或 OPENAI/GEMINI Key） |
| 4. 一键排版 | Markdown → 符合微信规范的 HTML（全内联样式） | `scripts/format_to_wechat_html.py` |
| 5. 去 AI 痕 | 优化语言，去除 AI 写作痕迹，更自然 | 纯 LLM（参考 `humanizer`） |
| 6. 自动发布 | 推送到公众号草稿箱 | `scripts/wechat_api.py` + AppID/AppSecret |

## 目录结构

```
wechat-article-creator/
├── SKILL.md                          # 技能主文件（编排逻辑）
├── references/                       # 按需加载的方法论文档
│   ├── topic_templates.md            # 选题模板与技巧
│   ├── wechat_format_guide.md        # 微信排版规范
│   └── writing_style_guide.md        # 写作风格指南
└── scripts/
    ├── wechat_api.py                 # 微信公众号 API 封装（纯标准库）
    └── format_to_wechat_html.py      # Markdown → 微信 HTML 转换器（纯标准库）
```

两个 Python 脚本均为**纯标准库实现**，不依赖任何第三方包，可在任意装有 Python 3 的环境直接运行。

## 安装

将本仓库整体拷贝到 CodeBuddy 的技能目录（即包含 `SKILL.md` 的目录）即可被识别：

```bash
# 示例：拷贝到用户技能目录
cp -r wechat-article-creator ~/.codebuddy/skills/
```

## 前置依赖

### 发布功能（环节 6）
- 微信公众号 **AppID** 和 **AppSecret**（公众平台 → 开发 → 基本配置）
- 调用服务器的公网 IP 已加入公众号后台 **IP 白名单**
- 凭证仅在运行时由用户通过命令行参数传入，**不写入文件或日志**

### 配图功能（环节 3，推荐方案，无需外部 Key）
- 使用内置 `ImageGen` 工具，前置调用 `connect_cloud_service` 获取云端凭证

### 配图功能（备选方案，需自行配置）
- `OPENAI_API_KEY` 环境变量（`openai-image-gen`）
- 或 `GEMINI_API_KEY` 环境变量（`nano-banana-pro`）

### 协作技能
- `wechat-article-search`：搜狗微信搜索（选题竞品参考），与本技能同级放置时通过 `{skill_dir}/../wechat-article-search/scripts/sogou_search.py` 调用
- `humanizer`：去 AI 痕参考指南
- `ImageGen`：内置 AI 生图

## 安全说明

- **不存储任何凭证**：AppID/AppSecret/API Key 均为占位符，由用户运行时传入。
- **草稿 ≠ 群发**：发布环节仅推送到草稿箱，群发需用户在公众号后台手动确认。
- `wechat_api.py` 的 `publish` 子命令（freepublish/submit）会真正发布且**不可撤回**，请谨慎手动调用。

## License

[MIT](./LICENSE)
