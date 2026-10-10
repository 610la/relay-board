#!/usr/bin/env python3
"""往传话板推送内容：把文本写进 message.json，commit 并 push 到 GitHub，
页面通过 GitHub API 轮询读取，约一分钟内显示。
用法： echo "要传的话" | python3 publish.py
"""
import json
import subprocess
import sys
import time

REPO_DIR = "/home/hatch/workspace/relay-board"


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
    print(f"已推送 {len(text)} 字，约一分钟内显示在页面上")


if __name__ == "__main__":
    main()
