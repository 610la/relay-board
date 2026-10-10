#!/usr/bin/env python3
"""往传话板推送内容：从 stdin 读文本，以 retain 方式发到 MQTT，页面实时显示。
用法： echo "要传的话" | python3 publish.py
"""
import json
import sys
import time

import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "relay-board/610la/k7q3x9"


def main() -> None:
    text = sys.stdin.read()
    if not text.strip():
        print("空内容，不发送", file=sys.stderr)
        sys.exit(1)
    payload = json.dumps(
        {"text": text, "time": time.strftime("%Y-%m-%d %H:%M")},
        ensure_ascii=False,
    )
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.connect(BROKER, PORT, 60)
    c.publish(TOPIC, payload, qos=1, retain=True)
    c.disconnect()
    print(f"已推送 {len(text)} 字")


if __name__ == "__main__":
    main()
