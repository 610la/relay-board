#!/usr/bin/env python3
"""往传话板推送内容：写进 message.json，commit/push 到 GitHub，
然后清 jsDelivr CDN 缓存；页面 3 秒轮询 CDN，约 10 秒内显示。
用法： echo "要传的话" | python3 publish.py
"""
import json
import subprocess
import sys
import time
import urllib.request

REPO_DIR = "/home/hatch/workspace/relay-board"
CDN_FILE = "https://cdn.jsdelivr.net/gh/610la/relay-board@master/message.json"


def sh(*args: str) -> None:
    subprocess.run(args, cwd=REPO_DIR, check=True,
                   capture_output=True, text=True)


def main() -> None:
    text = sys.stdin.read()
    if not text.strip():
        print("空内容，不发送", file=sys.stderr)
        sys.exit(1)
    msg = {"text": text,
           "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(f"{REPO_DIR}/message.json", "w",
              encoding="utf-8") as f:
        json.dump(msg, f, ensure_ascii=False)
    sh("git", "add", "message.json")
    sh("git", "-c", "user.name=hanhan", "-c", "user.email=hanhan@local",
       "commit", "-qm", "传话更新")
    sh("git", "push", "-q", "origin", "master")
    try:
        req = urllib.request.Request(
            "https://purge.jsdelivr.net/gh/610la/relay-board@master/message.json")
        urllib.request.urlopen(req, timeout=20).read()
        print(f"已推送 {len(text)} 字，约 10 秒内显示在页面上")
    except Exception as e:  # noqa: BLE001
        print(f"已推送 {len(text)} 字，但清 CDN 缓存失败（{e}），页面稍后同步")


if __name__ == "__main__":
    main()
