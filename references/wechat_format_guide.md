# 微信公众号排版规范参考

> 本文档为 `wechat-article-creator` 技能的排版环节（环节 4）提供详细参考。

---

## 核心原则

1. **必须使用内联样式**：微信会移除 `<style>` 标签和外部 CSS，所有样式必须写在元素的 `style` 属性中
2. **无 JavaScript**：所有 `<script>` 标签会被过滤
3. **有限的 HTML 标签**：只支持微信白名单内的 HTML 标签
4. **适配手机屏幕**：正文最大宽度 677px，边距 16px

---

## CSS 样式速查表

### 正文字体

| 属性 | 推荐值 | 说明 |
|------|--------|------|
| `font-family` | `-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif` | 优先系统字体，保证中英文渲染 |
| `font-size` | `16px` | 手机阅读最佳字号（15-17px 均可） |
| `line-height` | `1.75` | 行间距（1.6-1.8 均可） |
| `color` | `#3f3f3f` | 正文颜色，非纯黑以保护视力 |
| `letter-spacing` | `0.5px` | 中文字间距微调 |
| `word-break` | `break-word` | 防止长 URL 溢出屏幕 |

### 标题

| 级别 | `font-size` | `color` | `font-weight` | 适用场景 |
|------|------------|---------|---------------|---------|
| H1（文章大标题） | `22px` | `#222` | `bold` | 文章顶部主标题 |
| H2（一级小标题） | `20px` | `#222` | `bold` | 章节标题 |
| H3（二级小标题） | `18px` | `#333` | `bold` | 小节标题 |
| H4（三级小标题） | `16px` | `#333` | `bold` | 更小的小节 |

### 其他元素

| 元素 | 样式 |
|------|------|
| 引用块 | `border-left: 4px solid #ddd; padding: 4px 0 4px 16px; color: #6a6a6a; font-size: 15px; line-height: 1.75` |
| 粗体 | `font-weight: bold; color: #333` |
| 链接 | `color: #576b95; text-decoration: none; border-bottom: 1px solid #d0d8e8` |
| 行内代码 | `background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 14px; color: #c7254e` |
| 代码块 | `background: #f5f5f5; padding: 14px 16px; border-radius: 6px; overflow-x: auto; font-size: 13px; white-space: pre-wrap` |
| 图片 | `width: 100%; max-width: 100%; border-radius: 4px; display: block; margin: 0 auto` |
| 分隔线 | `border: none; border-top: 1px solid #e8e8e8; margin: 2em 0` |
| 列表 | `padding-left: 1.5em; color: #3f3f3f; font-size: 16px` |

### 颜色体系

| 用途 | 颜色 | 色值 |
|------|------|------|
| 正文 | 深灰 | `#3f3f3f` |
| 标题 | 近黑 | `#222` / `#333` |
| 次要文字（作者、日期） | 中灰 | `#888` |
| 引用文字 | 浅灰 | `#6a6a6a` |
| 链接 | 微信蓝 | `#576b95` |
| 代码背景 | 极浅灰 | `#f0f0f0` / `#f5f5f5` |
| 分割线 | 浅灰 | `#e8e8e8` |
| 行内代码文字 | 暗红 | `#c7254e` |

---

## HTML 标签白名单

### 支持的块级元素
`<section>` `<div>` `<p>` `<h1>` `<h2>` `<h3>` `<h4>` `<blockquote>` `<ul>` `<ol>` `<li>` `<pre>` `<hr>` `<table>` `<thead>` `<tbody>` `<tr>` `<td>` `<th>`

### 支持的内联元素
`<span>` `<strong>` `<b>` `<em>` `<i>` `<a>` `<code>` `<br>` `<img>` `<sub>` `<sup>`

### 不支持或会被过滤的
- `<style>` — 完全移除
- `<script>` — 完全移除
- `<iframe>` — 移除
- `<form>` / `<input>` — 移除
- `class` 属性 — 保留但无用（无 `<style>`）
- 外部字体（`@import` / `@font-face`）— 移除
- `position: fixed` / `position: sticky` — 被过滤

---

## 图片规范

1. **格式**：仅支持 jpg、png、gif
2. **大小**：单张不超过 10MB（推荐控制在 1MB 以内）
3. **尺寸**：宽度建议 900-1080px
4. **来源**：必须通过 `uploadimg` 接口上传到微信服务器获取 CDN URL，外部 URL 大概率被过滤
5. **封面图**：
   - 首图封面：2.35:1 比例（推荐 900×383）
   - 分享卡片：1:1 比例（推荐 200×200 或 500×500）
6. **内页插图**：
   - `width: 100%` 确保适配手机宽度
   - 居中显示，上下留白 1em 左右

---

## 常见排版问题与解决方案

### 1. 段落间距不均匀
**原因**：空 `<p>` 标签被微信过滤。
**解决**：使用 `margin` 控制间距，不依赖空行。

### 2. 列表缩进不对齐
**原因**：微信对 `ul/ol` 的默认样式做了调整。
**解决**：显式设置 `padding-left: 1.5em`。

### 3. 代码块换行混乱
**原因**：微信可能会合并多余空格。
**解决**：使用 `<pre>` 标签 + `white-space: pre-wrap`。

### 4. 字体在安卓/iOS 显示不一致
**原因**：不同系统默认字体不同。
**解决**：使用完整字体栈 `-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif`。

### 5. 外部图片不显示
**原因**：微信过滤非白名单域名的外部图片。
**解决**：通过 `uploadimg` 接口先将图片上传到微信服务器，使用返回的 CDN URL。

### 6. 链接样式丢失
**原因**：微信会给链接加上默认样式。
**解决**：显式设置 `color: #576b95` 和 `text-decoration: none`。

---

## 不同手机屏幕适配

| 设备 | 屏幕宽度 | 内容宽度（16px 边距） |
|------|---------|---------------------|
| iPhone SE | 375px | 343px |
| iPhone 14 | 390px | 358px |
| iPhone 14 Pro Max | 430px | 398px |
| 安卓主流 | 360-414px | 328-382px |

建议设置：`max-width: 677px; padding: 0 16px; margin: 0 auto`，可适配所有机型。

---

## 发布限制速查

| 项目 | 限制 |
|------|------|
| 标题 | ≤ 32 字（64 字节） |
| 作者 | ≤ 16 字（32 字节） |
| 摘要 | ≤ 128 字（256 字节） |
| 正文 | ≤ 20,000 字符，< 1MB |
| 封面图 | 需通过永久素材接口上传（`upload-thumb`） |
| 正文图片 | 需通过 `uploadimg` 接口上传 |
| 订阅号群发 | 每天 1 次 |
| 服务号群发 | 每月 4 次 |
