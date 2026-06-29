#!/usr/bin/env bash
# voicein セットアップ。sudo が必要な箇所は内部で sudo を呼びます。
# 実行: bash install.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/4 システムパッケージ =="
sudo apt-get update
sudo apt-get install -y \
    wl-clipboard libnotify-bin pulseaudio-utils \
    python3-venv python3-dev python3-tk gcc

echo "== 2/4 /dev/uinput と /dev/input への権限(inputグループ) =="
# uinput をブート時に読み込む
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf >/dev/null
sudo modprobe uinput || true
# uinput ノードを input グループで読み書き可能に
echo 'KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"' \
    | sudo tee /etc/udev/rules.d/99-uinput-voicein.rules >/dev/null
sudo udevadm control --reload-rules
sudo udevadm trigger
# 現在のユーザを input グループへ(/dev/input 読み取り + /dev/uinput 書き込み)
sudo usermod -aG input "$USER"

echo "== 3/4 Python 仮想環境 =="
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt

echo "== 4/4 設定ファイル =="
if [ ! -f config.ini ]; then
    cp config.example.ini config.ini
    echo "config.ini を作成しました。APIキーを設定してください。"
fi

cat <<'EOF'

==========================================================
セットアップ完了。

重要: input グループの反映には【一度ログアウト/ログイン】が必要です。
(または再起動)。これをしないと録音キー検出・注入ができません。

次の手順:
  1) ログアウト/ログイン
  2) config.ini に OpenAI APIキーを設定
  3) 起動:   ./run.sh
  4) 履歴GUI: ./history.sh
==========================================================
EOF
