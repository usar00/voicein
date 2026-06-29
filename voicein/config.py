"""設定の読み込みとパス解決。

設定ファイルは <プロジェクト>/config.ini を既定とする(無ければ config.example.ini)。
履歴は <プロジェクト>/data/history.jsonl に保存する。
"""
from __future__ import annotations

import configparser
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
HISTORY_PATH = DATA_DIR / "history.jsonl"


@dataclass
class Config:
    api_key: str = ""
    model: str = "gpt-4o-transcribe"
    language: str = "ja"
    prompt: str = ""
    mic_source: str = ""
    sounds: bool = True
    notify: bool = True
    max_seconds: int = 60
    min_seconds: float = 0.3
    # PTTキー名(evdev) -> 貼り付けキー組み合わせ
    bindings: dict[str, str] = field(default_factory=lambda: {
        "KEY_RIGHTCTRL": "ctrl+v",        # 通常のアプリ(Claude / ブラウザ / 入力欄)
        "KEY_RIGHTSHIFT": "ctrl+shift+v",  # ターミナル
    })


def _config_file() -> Path:
    primary = ROOT / "config.ini"
    if primary.exists():
        return primary
    return ROOT / "config.example.ini"


def load() -> Config:
    cfg = Config()
    path = _config_file()
    if path.exists():
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path, encoding="utf-8")
        if parser.has_section("voicein"):
            s = parser["voicein"]
            cfg.api_key = s.get("api_key", cfg.api_key).strip()
            cfg.model = s.get("model", cfg.model).strip()
            cfg.language = s.get("language", cfg.language).strip()
            cfg.prompt = s.get("prompt", cfg.prompt).strip()
            cfg.mic_source = s.get("mic_source", cfg.mic_source).strip()
            cfg.sounds = s.getboolean("sounds", cfg.sounds)
            cfg.notify = s.getboolean("notify", cfg.notify)
            cfg.max_seconds = s.getint("max_seconds", cfg.max_seconds)
            cfg.min_seconds = s.getfloat("min_seconds", cfg.min_seconds)
        if parser.has_section("bindings"):
            cfg.bindings = {k.upper(): v.strip() for k, v in parser["bindings"].items()}
    # APIキーは環境変数を優先フォールバック
    if not cfg.api_key:
        cfg.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    return cfg
