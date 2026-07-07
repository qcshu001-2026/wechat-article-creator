#!/usr/bin/env python3
"""
微信公众号 API 命令行工具。
纯标准库实现，无需安装第三方依赖。

子命令:
  token          获取 access_token
  upload-thumb   上传封面图（永久素材，返回 thumb_media_id）
  upload-image   上传文章内图片（返回微信 CDN URL）
  create-draft   创建草稿
  publish        发布草稿

使用示例:
  python3 wechat_api.py token --appid APPID --secret SECRET
  python3 wechat_api.py upload-thumb --token TOKEN --file cover.jpg
  python3 wechat_api.py upload-image --token TOKEN --file img.png
  python3 wechat_api.py create-draft --token TOKEN --title "标题" --content article.html --thumb-media-id ID
  python3 wechat_api.py publish --token TOKEN --media-id MEDIA_ID
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.weixin.qq.com/cgi-bin"


# ── helpers ──────────────────────────────────────────────────────────────────

def _read_file(path: str) -> str:
    """读取文本文件内容。如果 path 不是文件路径（如直接传入 HTML 字符串），原样返回。"""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return path


def _multipart_post(url: str, filepath: str, field_name: str = "media",
                    content_type: str = "image/jpeg") -> dict:
    """发送 multipart/form-data POST 请求，上传文件。"""
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
    filename = os.path.basename(filepath)

    with open(filepath, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _json_post(url: str, payload: dict) -> dict:
    """发送 application/json POST 请求。"""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _print_and_exit(result: dict) -> None:
    """打印 JSON 结果。如果 errcode 非 0，以非零退出码退出。"""
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("errcode", 0) != 0:
        sys.exit(1)


# ── subcommands ──────────────────────────────────────────────────────────────

def cmd_token(args) -> None:
    """获取 access_token。"""
    url = (f"{API_BASE}/token?appid={args.appid}"
           f"&secret={args.secret}&grant_type=client_credential")
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        result = json.loads(e.read())

    if "access_token" in result:
        # 只打印 token 值，方便 shell 脚本用 $() 捕获
        print(result["access_token"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


def cmd_upload_thumb(args) -> None:
    """上传缩略图（封面图）到永久素材库，返回 thumb_media_id。"""
    url = f"{API_BASE}/material/add_material?access_token={args.token}&type=thumb"
    result = _multipart_post(url, args.file)
    _print_and_exit(result)


def cmd_upload_image(args) -> None:
    """上传文章内图片，返回微信 CDN URL。
    注意：<1MB，仅 jpg/png，不占用素材库限额。"""
    url = f"{API_BASE}/media/uploadimg?access_token={args.token}"
    result = _multipart_post(url, args.file)
    _print_and_exit(result)


def cmd_create_draft(args) -> None:
    """创建草稿。"""
    url = f"{API_BASE}/draft/add?access_token={args.token}"
    content = _read_file(args.content)

    payload = {
        "articles": [{
            "article_type": "news",
            "title": args.title,
            "author": args.author or "",
            "digest": args.digest or "",
            "content": content,
            "thumb_media_id": args.thumb_media_id,
            "need_open_comment": 1 if args.open_comment else 0,
            "only_fans_can_comment": 1 if args.fans_only else 0,
        }]
    }
    result = _json_post(url, payload)
    _print_and_exit(result)


def cmd_publish(args) -> None:
    """发布草稿（freepublish/submit 接口）。注意：发布后不可撤回。"""
    url = f"{API_BASE}/freepublish/submit?access_token={args.token}"
    payload = {"media_id": args.media_id}
    result = _json_post(url, payload)
    _print_and_exit(result)


# ── argparse ─────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wechat_api",
        description="微信公众号 API 命令行工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # token
    p = sub.add_parser("token", help="获取 access_token")
    p.add_argument("--appid", required=True, help="公众号 AppID")
    p.add_argument("--secret", required=True, help="公众号 AppSecret")

    # upload-thumb
    p = sub.add_parser("upload-thumb", help="上传封面图（永久素材）")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--file", required=True, help="封面图文件路径（jpg/png，建议 1:1 比例）")

    # upload-image
    p = sub.add_parser("upload-image", help="上传文章内图片")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--file", required=True, help="图片文件路径（jpg/png，<1MB）")

    # create-draft
    p = sub.add_parser("create-draft", help="创建草稿")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--title", required=True, help="文章标题（≤32字）")
    p.add_argument("--content", required=True, help="文章正文 HTML 文件路径（或直接传入 HTML 字符串）")
    p.add_argument("--thumb-media-id", required=True, help="封面图 thumb_media_id")
    p.add_argument("--author", default="", help="作者名（≤16字）")
    p.add_argument("--digest", default="", help="文章摘要（≤128字）")
    p.add_argument("--open-comment", action="store_true", default=True, help="开启评论（默认）")
    p.add_argument("--fans-only", action="store_true", default=False, help="仅粉丝可评论")

    # publish
    p = sub.add_parser("publish", help="发布草稿（谨慎使用）")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--media-id", required=True, help="草稿 media_id")

    args = parser.parse_args()

    commands = {
        "token": cmd_token,
        "upload-thumb": cmd_upload_thumb,
        "upload-image": cmd_upload_image,
        "create-draft": cmd_create_draft,
        "publish": cmd_publish,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
