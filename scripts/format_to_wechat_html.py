#!/usr/bin/env python3
"""
Markdown → 微信兼容 HTML 转换器。
纯标准库实现，输出全内联样式（微信会移除 <style> 标签和外部 CSS）。

使用方式:
  python3 format_to_wechat_html.py --input article.md --output article.html --title "标题" --author "作者"

微信排版规范:
  - 正文字号: 16px, 行高: 1.75, 颜色: #3f3f3f, 字间距: 0.5px
  - 标题: 18-22px, 加粗, 颜色 #222/#333
  - 引用: 左侧灰色边框 + 灰色文字
  - 图片: width:100%, 居中
  - 链接: #576b95 微信蓝
  - 字体栈: 含 PingFang SC / Microsoft YaHei
"""

import argparse
import re
import sys


# ── inline formatters ────────────────────────────────────────────────────────

def _bold(text: str) -> str:
    return f'<strong style="font-weight:bold; color:#333;">{text}</strong>'


def _italic(text: str) -> str:
    return f'<em style="font-style:italic;">{text}</em>'


def _link(text: str, url: str) -> str:
    return (
        f'<a href="{url}" style="color:#576b95; text-decoration:none; '
        f'border-bottom:1px solid #d0d8e8;">{text}</a>'
    )


def _inline_code(text: str) -> str:
    return (
        f'<code style="background:#f0f0f0; padding:2px 6px; border-radius:3px; '
        f'font-family:Menlo,Monaco,Consolas,monospace; font-size:14px; '
        f'color:#c7254e;">{text}</code>'
    )


def _process_inline(text: str) -> str:
    """处理段落内的粗体、斜体、链接、行内代码。"""
    # 粗体 **text**
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: _bold(m.group(1)), text)
    # 斜体 *text*（避开 **）
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
                  lambda m: _italic(m.group(1)), text)
    # 链接 [text](url)
    text = re.sub(r"\[(.+?)\]\((.+?)\)",
                  lambda m: _link(m.group(1), m.group(2)), text)
    # 行内代码 `code`
    text = re.sub(r"`([^`]+)`", lambda m: _inline_code(m.group(1)), text)
    return text


# ── main converter ───────────────────────────────────────────────────────────

def md_to_wechat_html(md_text: str, title: str = "", author: str = "") -> str:
    """将 Markdown 文本转换为微信兼容的 HTML（全内联样式）。"""
    lines = md_text.strip().split("\n")
    html_parts = []

    # ── 文档头部 ──
    font_stack = (
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', "
        "'Helvetica Neue', sans-serif"
    )
    html_parts.append(
        f'<section style="padding:0 16px; max-width:677px; margin:0 auto; '
        f'font-family:{font_stack};">'
    )

    if title:
        html_parts.append(
            f'<h1 style="font-size:22px; font-weight:bold; color:#222; '
            f'margin:0.8em 0 0.3em; line-height:1.4; letter-spacing:0.5px;">'
            f'{title}</h1>'
        )
    if author:
        html_parts.append(
            f'<p style="color:#888; font-size:14px; margin:0 0 1.8em; '
            f'line-height:1.5;">{author}</p>'
        )

    # ── 逐行解析 ──
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # ── 代码块 ──
        if line.strip().startswith("```"):
            if in_code_block:
                code = "\n".join(code_lines)
                code = (code.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;"))
                html_parts.append(
                    f'<pre style="background:#f5f5f5; padding:14px 16px; '
                    f'border-radius:6px; overflow-x:auto; font-size:13px; '
                    f'line-height:1.6; margin:1em 0; '
                    f'font-family:Menlo,Monaco,Consolas,monospace; '
                    f'color:#333; white-space:pre-wrap; word-wrap:break-word;">'
                    f'<code>{code}</code></pre>'
                )
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # ── 空行 ──
        if not line.strip():
            i += 1
            continue

        # ── 标题 ──
        heading_matched = False
        for level, tag, style in [
            (1, "h2", "font-size:20px; font-weight:bold; color:#222; "
                     "margin:1.4em 0 0.5em; line-height:1.4;"),
            (2, "h3", "font-size:18px; font-weight:bold; color:#333; "
                     "margin:1.2em 0 0.4em; line-height:1.4;"),
            (3, "h4", "font-size:16px; font-weight:bold; color:#333; "
                     "margin:1em 0 0.3em; line-height:1.5;"),
        ]:
            prefix = "#" * level + " "
            if line.startswith(prefix):
                text = _process_inline(line[len(prefix):])
                html_parts.append(f'<{tag} style="{style}">{text}</{tag}>')
                i += 1
                heading_matched = True
                break

        if heading_matched:
            continue

        # ── 引用块 ──
        if line.startswith("> "):
            text = _process_inline(line[2:])
            html_parts.append(
                f'<blockquote style="border-left:4px solid #ddd; '
                f'padding:4px 0 4px 16px; color:#6a6a6a; margin:0.8em 0; '
                f'font-size:15px; line-height:1.75;">{text}</blockquote>'
            )
            i += 1
            continue

        # ── 图片 ──
        img_match = re.match(r"!\[(.*)\]\((.+)\)", line)
        if img_match:
            alt = img_match.group(1) or ""
            src = img_match.group(2)
            html_parts.append(
                f'<p style="text-align:center; margin:1.2em 0;">'
                f'<img src="{src}" alt="{alt}" '
                f'style="width:100%; max-width:100%; border-radius:4px; '
                f'display:block; margin:0 auto;">'
                f'</p>'
            )
            i += 1
            continue

        # ── 分隔线 ──
        if line.strip() in ("---", "***", "___", "* * *"):
            html_parts.append(
                '<hr style="border:none; border-top:1px solid #e8e8e8; '
                'margin:2em 0;">'
            )
            i += 1
            continue

        # ── 无序列表 ──
        ul_match = re.match(r"^[\-\*] (.+)", line)
        if ul_match:
            items = [ul_match.group(1)]
            while (i + 1 < len(lines)
                   and re.match(r"^[\-\*] (.+)", lines[i + 1])):
                i += 1
                items.append(re.match(r"^[\-\*] (.+)", lines[i]).group(1))
            items_html = "".join(
                f'<li style="margin:0.2em 0; line-height:1.75;">'
                f'{_process_inline(item)}</li>'
                for item in items
            )
            html_parts.append(
                f'<ul style="padding-left:1.5em; margin:0.6em 0; '
                f'color:#3f3f3f; font-size:16px;">{items_html}</ul>'
            )
            i += 1
            continue

        # ── 有序列表 ──
        ol_match = re.match(r"^\d+\.\s(.+)", line)
        if ol_match:
            items = [ol_match.group(1)]
            while (i + 1 < len(lines)
                   and re.match(r"^\d+\.\s(.+)", lines[i + 1])):
                i += 1
                items.append(re.match(r"^\d+\.\s(.+)", lines[i]).group(1))
            items_html = "".join(
                f'<li style="margin:0.2em 0; line-height:1.75;">'
                f'{_process_inline(item)}</li>'
                for item in items
            )
            html_parts.append(
                f'<ol style="padding-left:1.5em; margin:0.6em 0; '
                f'color:#3f3f3f; font-size:16px;">{items_html}</ol>'
            )
            i += 1
            continue

        # ── 普通段落 ──
        processed = _process_inline(line)
        html_parts.append(
            f'<p style="font-size:16px; line-height:1.75; color:#3f3f3f; '
            f'letter-spacing:0.5px; margin:0 0 0.8em; word-break:break-word;">'
            f'{processed}</p>'
        )
        i += 1

    # ── 文档尾部 ──
    html_parts.append('</section>')
    return "\n".join(html_parts)


# ── argparse ─────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="format_to_wechat_html",
        description="将 Markdown 转换为微信兼容的 HTML（全内联样式）",
    )
    parser.add_argument("--input", "-i", required=True,
                        help="输入 Markdown 文件路径")
    parser.add_argument("--output", "-o", required=True,
                        help="输出 HTML 文件路径")
    parser.add_argument("--title", default="",
                        help="文章标题（可选，会渲染为 H1）")
    parser.add_argument("--author", default="",
                        help="作者名（可选）")

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = md_to_wechat_html(md_text, args.title, args.author)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"已生成: {args.output}")


if __name__ == "__main__":
    main()
