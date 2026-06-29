"""テキスト注入。クリップボードへコピー -> 仮想キーボードで貼り付けキーを送出。

日本語をキーコードで直接タイプするのは不可能なため、クリップボード経由で貼り付ける。
仮想キーボードは evdev.UInput(/dev/uinput が必要)で1度だけ生成して使い回す。
"""
from __future__ import annotations

import subprocess
import time

from evdev import UInput, ecodes as e

# 貼り付け文字列 -> evdev キーコード
_MODIFIERS = {
    "ctrl": e.KEY_LEFTCTRL,
    "control": e.KEY_LEFTCTRL,
    "shift": e.KEY_LEFTSHIFT,
    "alt": e.KEY_LEFTALT,
    "super": e.KEY_LEFTMETA,
    "meta": e.KEY_LEFTMETA,
}


def _keycode(token: str) -> int:
    token = token.strip().lower()
    if token in _MODIFIERS:
        return _MODIFIERS[token]
    if token == "insert":
        return e.KEY_INSERT
    if len(token) == 1 and token.isalnum():
        name = f"KEY_{token.upper()}"
        if hasattr(e, name):
            return getattr(e, name)
    name = token.upper() if token.upper().startswith("KEY_") else f"KEY_{token.upper()}"
    if hasattr(e, name):
        return getattr(e, name)
    raise ValueError(f"未知のキー: {token}")


def parse_combo(combo: str) -> list[int]:
    """'ctrl+shift+v' -> [KEY_LEFTCTRL, KEY_LEFTSHIFT, KEY_V]"""
    return [_keycode(t) for t in combo.split("+") if t.strip()]


class Injector:
    def __init__(self):
        # 送出しうるキーを広めに宣言しておく
        keys = list(_MODIFIERS.values()) + [e.KEY_INSERT]
        for c in "abcdefghijklmnopqrstuvwxyz0123456789":
            keys.append(getattr(e, f"KEY_{c.upper()}"))
        self.ui = UInput({e.EV_KEY: sorted(set(keys))}, name="voicein-virtual-kbd")
        # 新しい入力デバイスをコンポジタが認識するまで少し待つ
        time.sleep(0.8)

    def set_clipboard(self, text: str) -> None:
        for args in (["wl-copy"], ["wl-copy", "--primary"]):
            try:
                subprocess.run(args, input=text.encode("utf-8"), timeout=3, check=False)
            except FileNotFoundError:
                # wl-clipboard 未導入時は xclip にフォールバック
                sel = "primary" if "--primary" in args else "clipboard"
                try:
                    subprocess.run(["xclip", "-selection", sel],
                                   input=text.encode("utf-8"), timeout=3, check=False)
                except FileNotFoundError:
                    pass

    def _tap(self, keycodes: list[int]) -> None:
        for k in keycodes:
            self.ui.write(e.EV_KEY, k, 1)
            self.ui.syn()
            time.sleep(0.01)
        for k in reversed(keycodes):
            self.ui.write(e.EV_KEY, k, 0)
            self.ui.syn()
            time.sleep(0.01)

    def paste(self, text: str, combo: str = "ctrl+v") -> None:
        self.set_clipboard(text)
        time.sleep(0.06)  # クリップボード反映待ち
        self._tap(parse_combo(combo))

    def close(self) -> None:
        try:
            self.ui.close()
        except Exception:
            pass
