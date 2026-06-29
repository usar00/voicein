"""マイク録音。parecord(PipeWire/PulseAudio)で16kHzモノラルWAVに録音する。

プッシュトゥトーク用に start()/stop() で囲む。stop() は録音時間(秒)を返す。
"""
from __future__ import annotations

import asyncio
import signal
import tempfile
import time
import wave
from pathlib import Path


class Recorder:
    def __init__(self, mic_source: str = "", max_seconds: int = 60):
        self.mic_source = mic_source
        self.max_seconds = max_seconds
        self._proc: asyncio.subprocess.Process | None = None
        self._path: Path | None = None
        self._started: float = 0.0

    async def start(self) -> None:
        if self._proc is not None:
            return
        fd = tempfile.NamedTemporaryFile(prefix="voicein-", suffix=".wav", delete=False)
        fd.close()
        self._path = Path(fd.name)
        cmd = [
            "parecord",
            "--rate=16000",
            "--channels=1",
            "--format=s16le",
            "--file-format=wav",
        ]
        if self.mic_source:
            cmd.append(f"--device={self.mic_source}")
        cmd.append(str(self._path))
        self._proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        self._started = time.monotonic()

    async def stop(self) -> tuple[Path | None, float]:
        """録音を止め、(WAVパス, 秒数) を返す。失敗時は (None, 0)。"""
        if self._proc is None or self._path is None:
            return None, 0.0
        duration = time.monotonic() - self._started
        # SIGINT で parecord にWAVヘッダを確定させてから終了させる
        try:
            self._proc.send_signal(signal.SIGINT)
            await asyncio.wait_for(self._proc.wait(), timeout=3.0)
        except (ProcessLookupError, asyncio.TimeoutError):
            try:
                self._proc.kill()
            except ProcessLookupError:
                pass
        path = self._path
        self._proc = None
        self._path = None
        # WAVが空・壊れていないか軽くチェック
        try:
            with wave.open(str(path), "rb") as w:
                if w.getnframes() <= 0:
                    return None, duration
        except Exception:
            return None, duration
        return path, duration

    @property
    def recording(self) -> bool:
        return self._proc is not None
