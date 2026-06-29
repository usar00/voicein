---
title: "Linuxの日本語音声入力、高い課金をやめて自分で作った（OpenAI gpt-4o-transcribe）"
emoji: "🎤"
type: "tech"
topics: ["linux", "openai", "音声入力", "wayland", "python"]
published: true
---

## なにこれ

Linux（Wayland / GNOME）で、**ほぼキーボードを使わずに日本語を音声入力できるツール**を作りました。

- 指定キーを **押している間だけ録音**（プッシュトゥトーク）→ 離すと変換
- OpenAI の **`gpt-4o-transcribe`** で日本語に変換（句読点も自然）
- 変換結果を **いま開いているアプリ**（Claude / ブラウザ / ターミナルなど）のカーソル位置へ自動で貼り付け
- 変換履歴を **一覧表示・検索・ワンクリックでコピー** できるGUI付き

リポジトリはこちら。MITライセンスなので **使いたい人は勝手に使ってください**。

https://github.com/usar00/voicein

この記事自体、ほぼこのツールの音声入力で書いています。

## なんで作ったのか（モチベーション）

音声入力って便利なんですが、いい感じのものは**だいたい有料のサブスク**なんですよね。月額で課金が続くし、そもそも **Linux 対応が弱い**（Macは充実してるのにLinuxは選択肢が少ない）。さらに **日本語に特化したもの**となると一気に減ります。

要するに「Linux × 日本語 × 安い」が成立しない。なら作るか、と。

OpenAI の音声認識APIは **従量課金で激安**で、`gpt-4o-transcribe` だと **音声1分あたり約1円**。月に何時間しゃべっても数十円〜数百円で収まります。サブスクの月額を払い続けるより、自分でAPIを叩いたほうが安い。日本語の認識精度も普通に高い。

というわけで「高いから自分で作った」ツールです。

## 仕組み

特別なことはしていません。素朴な構成です。

```
[キー押下中] parecord で録音(16kHz mono WAV)
     │  キーを離す
     ▼
OpenAI gpt-4o-transcribe で日本語に変換
     │
     ▼
wl-copy でクリップボードへ → 仮想キーボード(evdev/uinput)で
Ctrl+V を送出 → カーソル位置に貼り付け
     │
     ▼
履歴(JSONL)に保存 → GUIで一覧・コピー
```

ポイントだけ:

### 文字注入は「クリップボード貼り付け」方式

日本語をキーコードで1文字ずつタイプするのは（レイアウト依存で）現実的でないので、**テキストをクリップボードに入れて Ctrl+V を送る**方式にしました。これなら日本語でも絵文字でも確実に入ります。

### Wayland でも X11 でも動く

GNOME の Wayland は合成入力に厳しいですが、カーネルレベルの **`uinput`（仮想キーボード）** と **`evdev`（キー検出）** を使うことで、Wayland / X11 どちらでも動きます。`/dev/uinput` と `/dev/input` を `input` グループで使えるようにするのがミソ（udevルール + グループ追加）。

### キーごとに貼り付け方法を変える

ターミナルは貼り付けが `Ctrl+Shift+V` だったりするので、設定でキーごとに割り当てを変えられます。

```ini
[bindings]
KEY_RIGHTCTRL = ctrl+v          ; 通常アプリ(Claude / ブラウザ / 入力欄)
KEY_RIGHTSHIFT = ctrl+shift+v   ; ターミナル
```

## 使い方

```bash
git clone https://github.com/usar00/voicein.git
cd voicein
bash install.sh        # 依存導入 + 権限設定 + venv
# 一度ログアウト/ログイン(inputグループ反映のため)
# config.ini に OpenAI APIキーを設定
./run.sh               # 起動
```

あとは **右Ctrlを押しながら話して離す** だけ。カーソル位置に日本語が入ります。

```bash
./history.sh           # 変換履歴ビューア(一覧 + コピー)
```

ログイン時の自動起動（systemd user service）も同梱しています。

## 動作環境

- Linux（**Wayland / GNOME / Ubuntu** で開発・確認。X11でも動く設計）
- 音声: PulseAudio または PipeWire（`parecord`）
- OpenAI APIキー（従量課金。`gpt-4o-transcribe` で約1円/分）

他ディストロでもパッケージ名を読み替えればだいたい動きます。

## ハマりどころ（OpenAIの課金）

ひとつだけ注意。OpenAIは前払い式なので、APIキーを作っただけだと `insufficient_quota` で動きません。**クレジットの購入が必要**です。

そして地味な罠として、**OpenAIはJCBカードを弾きます**。自分もJCBで決済失敗して、**Mastercard（デビットでOK）に変えたら通りました**。同じところで詰まったらカードを変えてみてください。

## おわりに

「Linuxで、日本語で、安く、ハンズフリーで打ちたい」を全部満たすものが無かったので作りました。MITなので改造もフォークもご自由に。Issue / PR 歓迎です。

https://github.com/usar00/voicein
