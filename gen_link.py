#!/usr/bin/env python3
"""生成传话板链接：从 stdin 读文本，输出带 base64url hash 的完整 URL。
用法： echo "要传的话" | python3 gen_link.py https://relay-board.pages.dev
"""
import base64
import sys

if len(sys.argv) < 2:
    print("用法: gen_link.py <页面基地址> < 文本文件", file=sys.stderr)
    sys.exit(1)

base = sys.argv[1].rstrip("/")
text = sys.stdin.read()
b64 = base64.urlsafe_b64encode(text.encode("utf-8")).decode().rstrip("=")
print(f"{base}#{b64}")
