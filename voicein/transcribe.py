"""OpenAI 音声認識(gpt-4o-transcribe / whisper-1)で日本語に変換する。"""
from __future__ import annotations

from pathlib import Path

from openai import OpenAI


class Transcriber:
    def __init__(self, api_key: str, model: str = "gpt-4o-transcribe",
                 language: str = "ja", prompt: str = ""):
        if not api_key:
            raise ValueError(
                "OpenAI APIキーが未設定です。config.ini の api_key か "
                "環境変数 OPENAI_API_KEY を設定してください。"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.language = language
        self.prompt = prompt

    def transcribe(self, wav_path: Path) -> str:
        """同期API呼び出し。日本語テキストを返す。"""
        kwargs: dict = {"model": self.model, "language": self.language}
        if self.prompt:
            kwargs["prompt"] = self.prompt
        with open(wav_path, "rb") as f:
            resp = self.client.audio.transcriptions.create(file=f, **kwargs)
        return (resp.text or "").strip()
