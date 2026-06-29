"""変換履歴の保存・読み込み(JSON Lines)。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from .config import DATA_DIR, HISTORY_PATH


@dataclass
class Entry:
    ts: str          # ISO8601
    text: str
    seconds: float = 0.0


def append(text: str, seconds: float = 0.0) -> Entry:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = Entry(ts=datetime.now().isoformat(timespec="seconds"),
                  text=text, seconds=round(seconds, 1))
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")
    return entry


def load() -> list[Entry]:
    if not HISTORY_PATH.exists():
        return []
    out: list[Entry] = []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                out.append(Entry(ts=d.get("ts", ""), text=d.get("text", ""),
                                 seconds=float(d.get("seconds", 0))))
            except Exception:
                continue
    return out
