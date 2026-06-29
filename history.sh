#!/usr/bin/env bash
# 変換履歴ビューア(GUI)を開く。
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python -m voicein history
