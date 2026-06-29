"""メインデーモン。

evdev で各 PTT キーの押下/離しを監視し、押している間だけ録音、
離したら OpenAI で日本語に変換 -> フォーカス中アプリへ貼り付け -> 履歴に保存する。
"""
from __future__ import annotations

import asyncio
import sys

import evdev
from evdev import ecodes

from . import history
from .config import Config, load as load_config
from .feedback import Feedback
from .inject import Injector
from .recorder import Recorder
from .transcribe import Transcriber


def _keycode(name: str) -> int | None:
    code = ecodes.ecodes.get(name.upper())
    return code if isinstance(code, int) else None


def find_devices(key_codes: set[int]) -> list[evdev.InputDevice]:
    """対象キーを持つ入力デバイス(キーボード/フットペダル等)を列挙する。"""
    devices = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
        except (PermissionError, OSError):
            continue
        caps = dev.capabilities().get(ecodes.EV_KEY, [])
        if dev.name == "voicein-virtual-kbd":
            continue
        if key_codes & set(caps):
            devices.append(dev)
        else:
            dev.close()
    return devices


class App:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.fb = Feedback(cfg.sounds, cfg.notify)
        self.recorder = Recorder(cfg.mic_source, cfg.max_seconds)
        self.injector = Injector()
        self.transcriber = Transcriber(cfg.api_key, cfg.model, cfg.language, cfg.prompt)
        # keycode -> 貼り付けコンボ
        self.bindings: dict[int, str] = {}
        for name, combo in cfg.bindings.items():
            code = _keycode(name)
            if code is None:
                print(f"[警告] 未知のキー名: {name}", file=sys.stderr)
                continue
            self.bindings[code] = combo
        self._busy = False
        self._active_key: int | None = None
        self._state = "idle"  # idle / pending(溜め中) / recording
        self._pending_start: asyncio.Task | None = None

    async def _read_device(self, dev: evdev.InputDevice) -> None:
        async for event in dev.async_read_loop():
            if event.type != ecodes.EV_KEY:
                continue
            if event.code not in self.bindings:
                continue
            # value: 1=押下, 0=離す, 2=オートリピート(無視)
            if event.value == 1:
                await self._on_press(event.code)
            elif event.value == 0:
                await self._on_release(event.code)

    async def _on_press(self, code: int) -> None:
        if self._busy or self._state != "idle":
            return
        self._active_key = code
        self._state = "pending"
        # 「溜め」: キーを press_delay 秒以上押し続けたら録音開始。
        # それより短い誤タップでは録音も効果音も発生しない。
        self._pending_start = asyncio.create_task(self._delayed_start())

    async def _delayed_start(self) -> None:
        try:
            await asyncio.sleep(self.cfg.press_delay)
        except asyncio.CancelledError:
            return
        self._state = "recording"  # ここを過ぎたら確定で録音
        await self.recorder.start()
        self.fb.sound("start")

    async def _on_release(self, code: int) -> None:
        if code != self._active_key:
            return
        if self._state == "pending":
            # 溜めの途中で離した = 短すぎる誤タップ。録音も音も出さず無視。
            if self._pending_start is not None:
                self._pending_start.cancel()
            self._pending_start = None
            self._active_key = None
            self._state = "idle"
            return
        if self._state != "recording":
            self._active_key = None
            return
        self._pending_start = None
        self._active_key = None
        self._state = "idle"
        path, duration = await self.recorder.stop()
        if path is None or duration < self.cfg.min_seconds:
            self.fb.sound("error")
            return
        combo = self.bindings.get(code, "ctrl+v")
        self._busy = True
        try:
            # ブロッキングなAPI呼び出しは別スレッドで
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(
                None, self.transcriber.transcribe, path)
            if not text:
                self.fb.sound("error")
                self.fb.notify_msg("音声入力", "(認識結果が空でした)")
                return
            self.injector.paste(text, combo)
            history.append(text, duration)
            self.fb.sound("done")
        except Exception as exc:  # noqa: BLE001
            self.fb.sound("error")
            self.fb.notify_msg("音声入力エラー", str(exc), urgency="critical")
            print(f"[エラー] {exc}", file=sys.stderr)
        finally:
            self._busy = False
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass

    async def run(self) -> None:
        devices = find_devices(set(self.bindings))
        if not devices:
            print("[エラー] 監視できる入力デバイスがありません。"
                  "`input` グループに入っているか、再ログイン済みか確認してください。",
                  file=sys.stderr)
            print("  対象キー:", ", ".join(self.cfg.bindings), file=sys.stderr)
            return
        print("voicein 起動。以下のキーを押している間だけ録音します:")
        for name, combo in self.cfg.bindings.items():
            print(f"  {name}  ->  貼り付け: {combo}")
        print("監視デバイス:", ", ".join(d.name for d in devices))
        self.fb.notify_msg("voicein 起動", "押している間だけ録音します")
        await asyncio.gather(*(self._read_device(d) for d in devices))


def main() -> int:
    cfg = load_config()
    try:
        app = App(cfg)
    except ValueError as exc:
        print(f"[エラー] {exc}", file=sys.stderr)
        return 1
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\n終了します。")
    return 0
