<!-- 日本語 | [English](README.en.md) -->

# voicein — Linux 音声入力(APIキー登録だけで使える / プッシュトゥトーク)

**LinuxでOpenAIのAPIキーを登録するだけで使える、音声入力ツール。**
ほぼキーボードを使わずに喋った内容を、いま開いているアプリへそのまま入力できます。

- 指定キーを **押している間だけ録音**(プッシュトゥトーク)→ 離すと変換
- OpenAI の音声認識(`gpt-4o-transcribe`)で変換。**日本語もそのまま高精度**(`language`設定で他言語もOK)
- 変換結果を **いま開いているアプリ**(Claude / ブラウザ / ターミナルなど)のカーソル位置へ自動で貼り付け
- 変換履歴を **一覧表示・検索・ワンクリックでコピー** できるGUI付き

ローカルにモデルを置いたり面倒なセットアップは不要。**APIキーを1つ登録すれば動きます。**

仕組み: 録音は `parecord`、認識は OpenAI API、注入は「クリップボードへコピー →
仮想キーボード(`evdev`/`uinput`)で貼り付けキー送出」。Wayland / X11 どちらでも動きます。

---

## セットアップ

```bash
git clone https://github.com/usar00/voicein.git
cd voicein
bash install.sh
```

`install.sh` がやること:
- パッケージ導入(`wl-clipboard` `libnotify-bin` `pulseaudio-utils` `python3-tk` など)
- `/dev/uinput` と `/dev/input` を **`input` グループ**で使えるよう udev 設定 + グループ追加
- Python 仮想環境(`.venv`)に `openai` `evdev` を導入
- `config.ini` を生成

> **重要**: `input` グループの反映には **一度ログアウト/ログイン**(または再起動)が必要です。

つづいて `config.ini` に OpenAI APIキーを設定:

```ini
[voicein]
api_key = sk-...
```

(環境変数 `OPENAI_API_KEY` でも可)。**設定はこれだけ。**

---

## 使い方

```bash
./run.sh        # 音声入力デーモンを起動
./history.sh    # 変換履歴ビューア(GUI)を開く
```

### 既定のキー割り当て

| キー | 貼り付け方法 | 用途 |
|------|--------------|------|
| 右Ctrl | `Ctrl+V` | Claude / ブラウザ / 通常の入力欄 |
| 右Shift | `Ctrl+Shift+V` | ターミナル |

押している間だけ録音し、離すと変換→貼り付けします。録音開始/完了は効果音で分かります。
短い誤タップで反応しないよう、押し始めに **`press_delay`(既定0.15秒)の「溜め」** があります。
キーや貼り付け方法・溜めの長さは `config.ini` で変更できます。

### 補助コマンド

```bash
./run.sh mics          # マイク音源の一覧(config の mic_source 用)
./run.sh keys          # 接続中の入力デバイス・キー名の確認
./run.sh test-inject "好きな文字列"   # 注入だけテスト
```

---

## 自動起動(任意)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/voicein.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now voicein.service
journalctl --user -u voicein -f   # ログ確認
```

---

## 設定(config.ini)

| 項目 | 説明 |
|------|------|
| `api_key` | OpenAI APIキー(空なら `OPENAI_API_KEY`) |
| `model` | `gpt-4o-transcribe`(既定)/ `gpt-4o-mini-transcribe`(安価)/ `whisper-1` |
| `language` | 認識言語(既定 `ja`。`en` などにすれば他言語) |
| `prompt` | 認識ヒント。固有名詞・専門用語を書くと精度向上 |
| `mic_source` | 使うマイク(`./run.sh mics` で確認) |
| `sounds` / `notify` | 効果音 / 通知の有無 |
| `max_seconds` / `min_seconds` | 録音の最大/最小秒数 |
| `press_delay` | この秒数キーを押し続けてから録音開始(誤タップ・即ピコ防止。既定0.15) |
| `[bindings]` | PTTキー → 貼り付け方法 の対応 |

---

## 動作環境

- Linux(**Wayland / GNOME / Ubuntu** で開発・確認。X11でも動く設計)
- 音声: PulseAudio または PipeWire(`parecord`)
- OpenAI APIキー(従量課金。`gpt-4o-transcribe` で約$0.006/分)

他ディストロでもパッケージ名を読み替えればだいたい動きます。

> OpenAIは前払い式なので事前にクレジット購入が必要です。なお **JCBカードは弾かれる**ことが
> 多いので、決済に失敗したら Visa / Mastercard(デビット可)を使ってください。

## トラブルシューティング

- **`input` グループ確認**: `groups | grep input`。無ければ再ログイン。
- **キーが検出されない**: `./run.sh keys` でデバイスが見えるか確認。見えなければ権限不足。
- **ターミナルに貼れない**: ターミナルの貼り付けは `Ctrl+Shift+V`。右Shiftで話すか割り当て変更。
- **別キーにしたい**: `./run.sh keys` 末尾のキー名(例 `KEY_SCROLLLOCK`, `KEY_F12`)を
  `[bindings]` に設定。フットペダル(USB HID)も同様に対応可能。

## ライセンス

MIT。使いたい人は勝手にどうぞ。
