"""CLI エントリポイント。

  python -m voicein            デーモン起動(プッシュトゥトーク音声入力)
  python -m voicein history    変換履歴ビューア(GUI)を開く
  python -m voicein mics       マイク(音源)一覧
  python -m voicein keys       接続中の入力デバイスとキーを確認
  python -m voicein test-inject "文字列"   注入のテスト(現在のカーソル位置へ貼り付け)
"""
from __future__ import annotations

import subprocess
import sys


def _mics() -> int:
    print("利用可能な音源(config.ini の mic_source に名前を設定):\n", flush=True)
    subprocess.run(["pactl", "list", "short", "sources"])
    return 0


def _keys() -> int:
    import evdev
    print("接続中の入力デバイス:\n")
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
        except (PermissionError, OSError) as exc:
            print(f"  {path}: アクセス不可 ({exc})")
            continue
        print(f"  {dev.path}  {dev.name}")
    print("\nPTTキー名の例: KEY_RIGHTCTRL, KEY_RIGHTSHIFT, KEY_SCROLLLOCK, KEY_PAUSE, KEY_F12")
    return 0


def _test_inject(text: str) -> int:
    from .inject import Injector
    inj = Injector()
    print("3秒後に貼り付けます。対象の入力欄にフォーカスしてください…")
    import time
    time.sleep(3)
    inj.paste(text)
    inj.close()
    print("完了。")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        from .app import main as daemon_main
        return daemon_main()
    cmd = args[0]
    if cmd in ("history", "gui"):
        from .historygui import main as gui_main
        return gui_main()
    if cmd == "mics":
        return _mics()
    if cmd == "keys":
        return _keys()
    if cmd == "test-inject":
        return _test_inject(args[1] if len(args) > 1 else "テスト 日本語 入力 123")
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
