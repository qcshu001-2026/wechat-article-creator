---
name: wechat-article-creator
description: |
  公众号文章全流程创作技能。从选题、写作、配图、排版、去AI痕到发布，一站式完成公众号推文创作。

  使用场景：
  - 需要写一篇公众号文章（从选题开始，全流程）
  - 已有选题，需要 AI 写稿并排版
  - 需要为公众号文章配图（封面图 + 内页插图）
  - 需要将 Markdown 文章转为微信排版格式
  - 需要去除文章的 AI 痕迹，让语言更自然
  - 需要将文章推送到公众号草稿箱

  触发词示例：
  - "帮我写一篇公众号文章"
  - "写一篇关于 XX 的公众号推文"
  - "帮我做一篇公众号文章，主题是 XX"
  - "把这篇文章排版成微信格式"
  - "把这篇文章发到公众号草稿箱"
  - "为这篇公众号文章配图"

  支持的环节（可单独执行或全流程执行）：
  1. 智能选题 — 根据热点和账号定位生成选题建议
  2. AI写稿 — 生成标题、大纲、初稿，支持多轮迭代修改
  3. 自动配图 — 生成封面图（2.35:1 和 1:1）和内页插图
  4. 一键排版 — 将文章转换为符合微信排版规范的 HTML
  5. 去AI痕 — 优化语言，让文章读起来更自然
  6. 自动发布 — 推送到公众号草稿箱

allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Skill
---

# 公众号文章全流程创作

> 覆盖从选题、写作、配图、排版、去AI痕到发布的 6 环节全链路。每个环节可独立执行，也可全流程串联。

---

## 前置条件

### 发布功能需要（环节 6）

- 微信公众号 **AppID** 和 **AppSecret**（在 [微信公众平台](https://mp.weixin.qq.com) → 开发 → 基本配置 获取）
- 调用服务器的公网 IP 已加入公众号后台的 **IP 白名单**

### 配图功能需要（环节 3）

**推荐方案**（无需外部 API Key）：
- 使用内置 `ImageGen` 工具直接生成配图
- 前置步骤：调用 `connect_cloud_service` 获取云端凭证

**备选方案**（需自行配置）：
- `OPENAI_API_KEY` 环境变量（openai-image-gen）
- 或 `GEMINI_API_KEY` 环境变量（nano-banana-pro）

### 可选配置

- 公众号名称（如"慧灯禅语"，用于 HTML 模板中的引导关注模块）
- 账号定位（如"佛学传统文化"、"科技资讯"、"生活美学"）
- 目标读者画像
- 写作风格偏好

### 输出目录规范

所有产出物统一放在 `/workspace/output/` 目录下：
```
/workspace/output/
├── wechat_article_YYYYMMDD_slug.html   # 排版完成的 HTML 文章
└── images/
    ├── cover.png                        # 封面图
    ├── img_01_desc.png                  # 内页图①
    ├── img_02_desc.png                  # 内页图②
    └── ...                              # 更多内页图
```

---

## 核心工作流

```
选题 ──→ 写稿 ──→ 配图 ──→ 排版 ──→ 去AI痕 ──→ 发布
  │        │        │        │        │          │
  ▼        ▼        ▼        ▼        ▼          ▼
选题建议  article.md  images/  HTML文件  润色后文章  草稿箱
                     cover.png           +发布清单
                     img_01~N.png
```

**重要规则**：
- 每个环节之间必须等待用户确认后才能继续
- 用户可指定只执行其中某几个环节
- 所有产出物统一输出到 `/workspace/output/`

---

## 环节 1：智能选题

### 何时触发
用户没有明确选题，或说"帮我推荐几个选题"。

### 流程
1. 询问账号定位和目标读者（如果用户未提供）
2. 使用 `WebSearch` 搜索近期相关热点话题
3. 可选：使用 `wechat-article-search`（搜狗微信搜索）检索同类公众号文章作为参考：
   ```bash
   python3 {skill_dir}/../wechat-article-search/scripts/sogou_search.py "关键词" --days 30
   ```
4. 分析竞品文章时关注：已有文章的角度是什么？哪些角度还没人写？差异化空间在哪？
5. 结合定位与热点生成 **3-5 个选题建议**
6. 每个选题包含以下 **7 个字段**：

| 字段 | 说明 |
|------|------|
| **选题标题** | 2-3 个备选标题（15-25 字） |
| **核心角度** | 与已有内容的差异化切入点 |
| **内容框架** | 3-5 个段落要点概要 |
| **话题热度** | ⭐（5 星评级） |
| **目标读者** | 主要吸引哪类读者 |
| **预估阅读量** | 低 / 中 / 高 / 爆款 |
| **差异化优势** | 为什么读者要看你这篇而不是已有的 |

7. 以表格形式展示选题，让用户选择或要求修改

> 选题方法论详见 `references/topic_templates.md`，包含 5 种高传播选题类型、不同定位的选题策略、自检清单。

### 输出
- 选定的选题（标题方向 + 核心论点 + 目标读者）

### 实现方式
- 纯 LLM 生成 + WebSearch 热点搜索，无需外部脚本

---

## 环节 2：AI写稿

### 何时触发
用户提供了选题（或从环节 1 来），需要生成文章。

### 流程
1. 根据选题生成 **3-5 个备选标题**，展示给用户选择
2. 用户选择标题后，**选择一个文章结构模式**（参照 `references/writing_style_guide.md` 的 5 种模式）：
   - 模式 1：是什么→为什么→怎么办（适合概念解读、方法论）
   - 模式 2：故事→道理→行动（适合个人成长、修行感悟）
   - 模式 3：问题→分析→方案（适合痛点解决、生活困扰）
   - 模式 4：对比→选择→建议（适合观点辨析、概念澄清）
   - 模式 5：现象→原因→趋势（适合行业分析、社会观察）
3. 生成 **文章大纲**（引言 → 正文分点 → 结论），展示给用户确认
4. 用户确认大纲（可要求调整），然后生成 **初稿**
5. 支持多轮迭代修改（如"精简这段"、"增加数据支撑"、"换个例子"）
6. 最终输出 Markdown 格式的完整文章，保存为 `/workspace/output/article.md`

### 格式约束
- 每段不超过 4 行（手机屏约 150 字）
- 每 300-500 字一个二级标题分段
- 正文 1500-3000 字（3-5 分钟阅读）
- 口语化表达，敢于表达观点和态度

### 输出
- `/workspace/output/article.md` — Markdown 格式的完整文章（标题 + 正文）

### 实现方式
- 纯 LLM 生成，标题和大纲阶段必须等待用户确认后才继续

---

## 环节 3：自动配图

### 何时触发
文章内容已完成，需要配图。

### 前置步骤
调用 `connect_cloud_service` 获取云端凭证（ImageGen 工具依赖此步骤）。

### 流程

**步骤 1：分析文章，确定配图方案**

根据文章内容提炼核心意象，确定配图数量和主题：
- **封面图**：1 张，作为文章首图
- **内页插图**：根据文章段落主题，2-5 张

**步骤 2：生成配图描述词**

为每张图生成详细的英文 prompt，展示给用户确认。Prompt 格式：
```
A WeChat public account article illustration, [核心意象描述], [风格描述], vertical composition, no text, no watermark, high quality
```

**步骤 3：调用 ImageGen 生成图片**

使用 `ToolSearch` 查找 `ImageGen` 工具，然后用 `DeferExecuteTool` 调用。每张图片依次生成，输出到 `/workspace/output/images/`。

**步骤 4：重命名图片**

生成后按规范重命名：
- 封面图 → `cover.png`
- 内页图① → `img_01_desc.png`
- 内页图② → `img_02_desc.png`
- ...

### 提示词风格参考

根据文章调性选择风格关键词：

| 文章调性 | 风格关键词 |
|---------|-----------|
| 佛学/禅意 | Zen aesthetics, ink wash painting style, minimalist, negative space, ethereal, serene |
| 科技/AI | cyberpunk-meets-zen, data streams, circuit patterns, neon-meets-nature |
| 生活美学 | warm natural light, minimalist interior, soft tones, wabi-sabi |
| 职场/商业 | clean professional, modern office, warm lighting, confident |

### 输出
- `/workspace/output/images/cover.png` — 封面图
- `/workspace/output/images/img_01_*.png ~ img_05_*.png` — 内页插图

### 降级方案

如果 ImageGen 不可用且 `OPENAI_API_KEY`/`GEMINI_API_KEY` 也未配置，不要中断流程：

1. 为每张配图生成详细的中文描述词（prompt）
2. 将描述词保存为 `/workspace/output/image_prompts.md`
3. 告知用户可复制 prompt 到以下工具手动生成：Midjourney / DALL·E / 稿定设计 / Canva
4. 后续排版环节使用占位图，提示用户手动替换

---

## 环节 4：一键排版

### 何时触发
文章 Markdown 和配图已完成，需要转为微信 HTML 格式。

### 流程

1. 确认文章 Markdown 文件路径和配图路径
2. 创建输出目录 `mkdir -p /workspace/output/images`
3. **生成完整的微信 HTML 文章**，必须包含以下模块：

**HTML 模板结构**：
```
① 顶部引导关注模块（公众号名称 + "点击上方蓝字关注"）
② 文章标题（H1，居中，粗体）
③ 文章正文（全内联样式，适配微信规范）
④ 内页插图（img 标签，引用 images/ 相对路径）
⑤ 底部公众号名片模块（名称 + 简介 + 关注提示）
⑥ 版权声明
```

4. 文件命名规范：`wechat_article_YYYYMMDD_slug.html`
   - 例：`wechat_article_20260630_ai_zen.html`

### HTML 模板代码

生成 HTML 时，必须嵌入以下固定模块：

**顶部引导关注**：
```html
<section style="text-align:center; padding:20px 16px 10px; color:#888; font-size:14px;">
  点击上方蓝字关注 <strong style="color:#333;">【公众号名称】</strong>
</section>
```

**底部公众号名片**：
```html
<section style="margin:2em 0; padding:16px; background:#f9f9f9; border-radius:8px; text-align:center;">
  <p style="font-size:15px; font-weight:bold; color:#333; margin:0 0 4px;">【公众号名称】</p>
  <p style="font-size:13px; color:#888; margin:0 0 8px;">佛学智慧 | 传统文化 | 心灵成长</p>
  <p style="font-size:13px; color:#576b95;">长按识别二维码，关注我们</p>
</section>
```

**版权声明**：
```html
<p style="font-size:12px; color:#bbb; text-align:center; margin:1.5em 0 0.5em;">
  本文由 【公众号名称】 原创发布<br>转载请注明出处
</p>
```

### 微信排版规范速查

| 元素 | 样式 |
|------|------|
| 正文 | font-size:16px; line-height:1.75; color:#3f3f3f; letter-spacing:0.5px |
| 标题 H2 | font-size:20px; font-weight:bold; color:#222; margin:1.4em 0 0.5em |
| 标题 H3 | font-size:18px; font-weight:bold; color:#333; margin:1.2em 0 0.4em |
| 引用块 | border-left:4px solid #ddd; padding-left:16px; color:#6a6a6a |
| 粗体 | font-weight:bold; color:#333 |
| 链接 | color:#576b95; text-decoration:none |
| 图片 | width:100%; border-radius:4px; display:block; margin:1em auto |
| 字体栈 | -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif |

详细规范见 `references/wechat_format_guide.md`。

### 输出
- `/workspace/output/wechat_article_YYYYMMDD_slug.html` — 完整微信 HTML 文章

---

## 环节 5：去AI痕

### 何时触发
文章内容已完成，需要让语言更自然。

### 流程
1. 从 HTML 或 Markdown 中提取纯文本
2. 加载 `humanizer` 技能作为参考指南（`Skill("humanizer")`）
3. 按以下分类系统检查中文 AI 写作痕迹：

**内容层面**：
- 开头模板化："在...的背景下"、"随着...的发展" → 改为具体场景或问题
- 结尾套路化："总的来说..."、"综上所述..."、"相信未来..." → 删除或用具体展望替代
- 空洞升华：没有实质内容的"启发"和"思考" → 要么给具体结论，要么留白

**语言层面**：
- AI 高频词汇："此外"→"另外"、"至关重要"→"很关键"、"不可否认"→删除
- 互联网黑话："赋能"、"抓手"、"闭环"、"底层逻辑" → 替换为日常表达
- 过度排比：连续 3 个以上的形容词或成语堆砌 → 保留一个最精准的
- 系动词泛滥："这是...的"、"是...的"结构过多 → 换主动句式

**结构层面**：
- 三段式固化："首先...其次...最后..." → 灵活调整，有时只需两个层次
- 每段长度均等 → 长段后跟短句，制造节奏变化
- 小标题数量过多 → 合并或精简

**风格层面**：
- 破折号滥用：一篇文章超过 3 个破折号 → 用逗号或句号替代
- 感叹号堆砌：连续使用感叹号 → 保留真正需要强调的一句
- 营销用语："干货"、"重磅"、"炸裂" → 除非账号风格如此
- 谄媚语气："让我们一起..."、"相信你一定..." → 删除，读者不需要被鼓励

4. 保持原意的同时，让语言更口语化、更有个人风格
5. 将润色后的文本重新填入 HTML 模板

> 详细写作风格指南见 `references/writing_style_guide.md`。

### 实现方式
- 纯 LLM 执行文本润色
- 加载 humanizer 技能的 24 类 AI 写作模式作为参考

---

## 环节 6：自动发布

### 何时触发
文章 HTML + 封面图已就绪，需要推送到公众号。

### 前置条件
- 已获取 AppID 和 AppSecret
- 服务器 IP 已加入公众号后台白名单

### 流程

使用 `scripts/wechat_api.py` 逐步操作：

```bash
SCRIPT="{skill_dir}/scripts/wechat_api.py"

# 1. 获取 access_token（有效期 7200 秒，会话内注意缓存）
TOKEN=$($SCRIPT token --appid APPID --secret APPSECRET)

# 2. 上传封面图（1:1 方形图作为 thumb 永久素材）
THUMB=$($SCRIPT upload-thumb --token $TOKEN --file cover_11.png)
# 从返回 JSON 中提取 thumb_media_id

# 3. 上传文章内图片（每张图片都要上传，获取微信 CDN URL）
$SCRIPT upload-image --token $TOKEN --file illustration_01.png
# 用返回的微信 URL 替换 HTML 中的图片链接

# 4. 创建草稿
$SCRIPT create-draft \
  --token $TOKEN \
  --title "文章标题" \
  --content article_formatted.html \
  --thumb-media-id "从步骤2获取的ID" \
  --author "作者名" \
  --digest "文章摘要"

# 5. 查看返回的 media_id，告知用户草稿已创建
# 注意：不自动执行 publish，用户需在公众号后台手动预览和群发
```

### 微信公众号 API 参考

| 接口 | 方法 | 说明 |
|------|------|------|
| `/cgi-bin/token` | GET | 获取 access_token（有效期 7200s） |
| `/cgi-bin/material/add_material?type=thumb` | POST | 上传封面图（永久素材，返回 thumb_media_id） |
| `/cgi-bin/media/uploadimg` | POST | 上传文章内图片（返回微信 CDN URL，<1MB） |
| `/cgi-bin/draft/add` | POST | 创建草稿（返回 media_id） |
| `/cgi-bin/freepublish/submit` | POST | 发布草稿（谨慎使用） |

### 发布限制

| 项目 | 限制 |
|------|------|
| 标题 | ≤ 32 字（64 字节） |
| 作者 | ≤ 16 字（32 字节） |
| 摘要 | ≤ 128 字（256 字节） |
| 正文 | ≤ 20,000 字符，< 1MB |
| 正文图片 | 必须通过 uploadimg 接口上传，外部 URL 会被过滤 |
| 订阅号群发 | 每天 1 次 |
| 服务号群发 | 每月 4 次 |

### 发布前检查清单

文章排版完成后，必须向用户输出以下检查清单：

```
📋 发布前检查清单
□ 标题在 15-25 字范围内（微信限制 ≤32 字）
□ 封面图已上传（比例裁剪为 2.35:1）
□ 正文有顶部引导关注模块
□ 正文有底部公众号名片模块
□ 正文有版权声明
□ 请手动检查错别字
□ 确认所有引用来源准确
□ 摘要建议：[自动生成的摘要]（约 40 字）
□ 所有配图已生成并引用正确
```

### 手动发布操作指引

由于微信 API 发布涉及 IP 白名单等限制，推荐用户手动发布：

1. 打开 `/workspace/output/wechat_article_*.html`，全选复制
2. 登录 [mp.weixin.qq.com](https://mp.weixin.qq.com) → 新建图文 → 粘贴到正文区域
3. 上传 `/workspace/output/images/` 下的图片，替换 HTML 中的本地路径
4. 上传封面图，裁剪为 2.35:1 比例
5. 手机预览确认后发布

> ⚠️ HTML 中图片引用的是本地相对路径 `images/...`，发布时必须替换为微信图片 CDN URL 或重新上传。

### 发布时间建议

根据公众号读者活跃时间选择发布时段：

| 时段 | 适合场景 | 说明 |
|------|---------|------|
| 工作日 12:00-13:00 | 职场/商业/科技类 | 午休阅读高峰 |
| 工作日 20:00-22:00 | 通用推荐 | 晚间阅读高峰，适合深度内容 |
| 周末 10:00-11:00 | 生活/文化/修行类 | 周末早晨放松阅读 |
| 周末 21:00-22:00 | 情感/故事类 | 睡前阅读高峰 |

> 佛学传统文化类建议：**周末早晨 10:00 或工作日晚间 21:00**，读者心态更沉静。

### 发布后跟进

```
📊 发布后跟进清单：
□ 发布后 1 小时检查阅读量，判断标题效果
□ 回复前 10 条评论（提升互动率，触发微信推荐算法）
□ 转发到朋友圈和相关微信群（前 2 小时是关键传播窗口）
□ 关注「分享率」和「收藏率」——比阅读量更能衡量内容质量
□ 记录数据用于复盘：什么标题效果好？什么话题读者更喜欢？
```

---

## 脚本参考

| 脚本 | 用途 | 参数 |
|------|------|------|
| `scripts/wechat_api.py` | 微信公众号 API 封装 | `token` / `upload-thumb` / `upload-image` / `create-draft` / `publish` |
| `scripts/format_to_wechat_html.py` | Markdown → 微信兼容 HTML | `--input` / `--output` / `--title` / `--author` |

---

## 与其他技能的协作

| 环节 | 协作技能/工具 | 调用方式 | 说明 |
|------|------------|---------|------|
| 选题 | WebSearch | 搜索热点话题 | 获取近期相关领域热点 |
| 选题（素材） | wechat-article-search | `python3 {path}/scripts/sogou_search.py "关键词" --days 30` | 搜索同类公众号文章参考 |
| 配图 | ImageGen | `ToolSearch("ImageGen")` → `DeferExecuteTool` | 内置 AI 生图（推荐首选，无需 API Key） |
| 配图（前置） | connect_cloud_service | 获取云端凭证 | ImageGen 依赖此步骤 |
| 配图（备选） | openai-image-gen | `python3 {path}/scripts/gen.py --prompt "..." --count N --size 1024x1024 --out-dir ./dir` | 需 OPENAI_API_KEY |
| 配图（备选） | nano-banana-pro | `uv run {path}/scripts/generate_image.py --prompt "..." --filename "..." --resolution 2K` | 需 GEMINI_API_KEY |
| 去AI痕 | humanizer | `Skill("humanizer")` 加载 24 类 AI 写作模式作为润色参考 | 需 LLM 将英文模式适配到中文语境 |

## 参考文档

本技能附带以下参考文档，按需加载：

| 文档 | 用途 | 何时加载 |
|------|------|---------|
| `references/wechat_format_guide.md` | 微信排版规范：CSS 速查、标签白名单、常见问题 | 环节 4（排版） |
| `references/writing_style_guide.md` | 公众号写作风格指南：不同定位的风格建议、标题技巧、节奏控制 | 环节 2（写稿）和环节 5（去AI痕） |
| `references/topic_templates.md` | 选题模板与技巧：5 种高传播选题类型、自检清单 | 环节 1（选题） |

---

## 注意事项

1. **AppSecret 安全**：AppSecret 仅在内存中使用，**绝不写入文件或日志**
2. **Token 缓存**：access_token 有效期 7200 秒，同一会话内可复用，避免频繁获取
3. **图片先上传**：HTML 中的图片必须使用微信 `uploadimg` 返回的 CDN URL，外部 URL 大概率被过滤
4. **每个环节确认**：全流程执行时，每个环节之间必须等待用户确认
5. **草稿 ≠ 群发**：`create-draft` 仅推送到草稿箱，用户需在公众号后台手动预览和群发
6. **API 白名单**：调用微信 API 的服务器 IP 需在公众号后台提前配置
7. **发布次数限制**：订阅号每天 1 次，服务号每月 4 次
8. **封面图要求**：需同时提供 2.35:1（首图）和 1:1（分享卡片）两种比例
9. **内页图片大小**：`uploadimg` 接口要求图片 < 1MB，超过需先压缩
10. **标题字数**：微信限制标题 ≤ 32 字（64 字节），生成标题时需注意
