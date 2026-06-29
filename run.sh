#!/usr/bin/env bash
# 音声入力デーモンを起動する。
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python -m voicein "$@"
