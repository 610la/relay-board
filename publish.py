#!/usr/bin/env python3
"""往传话板推送内容：通过 Nostr 中继实时推送（秒级到达），
同时把 message.json 推到 GitHub 作为备用同步通道。
用法： echo "要传的话" | python3 publish.py
"""
import hashlib
import json
import subprocess
import sys
import time

REPO_DIR = "/home/hatch/workspace/relay-board"
RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://nostr-pub.wellorder.net",
]
TAG = "relay-board-k7q3x9"


def load_key():
    from coincurve import PrivateKey
    with open(f"{REPO_DIR}/.nostr_key", encoding="utf-8") as f:
        return PrivateKey(bytes.fromhex(f.read().strip()))


def make_event(pk, text, tm):
    pub = pk.public_key.format(compressed=True)[1:].hex()
    content = json.dumps({"text": text, "time": tm}, ensure_ascii=False)
    created = int(time.time())
    evt = [0, pub, created, 1, [["t", TAG]], content]
    eid = hashlib.sha256(
        json.dumps(evt, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")).hexdigest()
    sig = pk.sign_schnorr(bytes.fromhex(eid)).hex()
    return {"id": eid, "pubkey": pub, "created_at": created,
            "kind": 1, "tags": [["t", TAG]], "content": content,
            "sig": sig}


def publish_nostr(event):
    import websocket
    ok = []
    for url in RELAYS:
        try:
            ws = websocket.create_connection(url, timeout=15)
            ws.send(json.dumps(["EVENT", event]))
            # 等待 OK 回执（最多 5 秒）
            ws.settimeout(5)
            try:
                while True:
                    msg = json.loads(ws.recv())
                    if msg[0] == "OK" and msg[1] == event["id"]:
                        ok.append(url)
                        break
            except Exception:
                ok.append(url + "(未确认)")
            ws.close()
        except Exception as e:  # noqa: BLE001
            print(f"中继 {url} 失败：{e}", file=sys.stderr)
    return ok


def push_github_backup(text, tm):
    def sh(*args):
        subprocess.run(args, cwd=REPO_DIR, check=True,
                       capture_output=True, text=True)
    msg = {"text": text, "time": tm}
    with open(f"{REPO_DIR}/message.json", "w", encoding="utf-8") as f:
        json.dump(msg, f, ensure_ascii=False)
    sh("git", "add", "message.json")
    sh("git", "-c", "user.name=hanhan", "-c", "user.email=hanhan@local",
       "commit", "-qm", "传话更新")
    sh("git", "push", "-q", "origin", "master")


def main():
    text = sys.stdin.read()
    if not text.strip():
        print("空内容，不发送", file=sys.stderr)
        sys.exit(1)
    tm = time.strftime("%Y-%m-%d %H:%M:%S")
    pk = load_key()
    event = make_event(pk, text, tm)
    ok = publish_nostr(event)
    try:
        push_github_backup(text, tm)
        backup = "GitHub 备用通道已更新"
    except Exception as e:  # noqa: BLE001
        backup = f"GitHub 备用通道失败（{e}）"
    print(f"已推送 {len(text)} 字；Nostr 中继确认：{len(ok)}/{len(RELAYS)}；{backup}")


if __name__ == "__main__":
    main()
