"""効果音・デスクトップ通知によるハンズフリーなフィードバック。"""
from __future__ import annotations

import subprocess
from pathlib import Path

_SOUNDS = {
    "start": "/usr/share/sounds/freedesktop/stereo/dialog-information.oga",
    "done": "/usr/share/sounds/freedesktop/stereo/complete.oga",
    "error": "/usr/share/sounds/freedesktop/stereo/dialog-error.oga",
}


class Feedback:
    def __init__(self, sounds: bool = True, notify: bool = True):
        self.sounds = sounds
        self.notify = notify

    def sound(self, kind: str) -> None:
        if not self.sounds:
            return
        path = _SOUNDS.get(kind)
        if path and Path(path).exists():
            subprocess.Popen(["paplay", path],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def notify_msg(self, title: str, body: str = "", urgency: str = "low") -> None:
        if not self.notify:
            return
        subprocess.Popen(
            ["notify-send", "-a", "voicein", "-u", urgency, "-t", "2500", title, body],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
