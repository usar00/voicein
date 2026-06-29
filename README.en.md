<!-- [日本語](README.md) | English -->

# voicein — Linux voice input (just register an API key / push-to-talk)

**A voice input tool for Linux that works with nothing but an OpenAI API key.**
Speak, and the text goes straight into whatever app you have open — almost no keyboard needed.

- **Record while a key is held** (push-to-talk). Press, speak, release.
- Transcribes with OpenAI (`gpt-4o-transcribe`). Works great in **Japanese and any other
  language** (set `language` in `config.ini`).
- Pastes the result into the **focused app** (Claude / browser / terminal …) at the cursor.
- A **history viewer** (GUI) to list, search, and copy past transcriptions with one click.

No local models, no fiddly setup. **Register one API key and it runs.**

How it works: recording via `parecord`, transcription via the OpenAI API, injection via
"copy to clipboard → send a paste keystroke from a virtual keyboard (`evdev`/`uinput`)".
Works on both Wayland and X11.

---

## Setup

```bash
git clone https://github.com/usar00/voicein.git
cd voicein
bash install.sh
```

`install.sh` does:
- Install packages (`wl-clipboard`, `libnotify-bin`, `pulseaudio-utils`, `python3-tk`, …)
- Add a udev rule + put you in the **`input` group** so `/dev/uinput` and `/dev/input` are usable
- Create a Python venv (`.venv`) with `openai` and `evdev`
- Generate `config.ini`

> **Important**: log out and back in (or reboot) once so the `input` group takes effect.

Then set your OpenAI API key in `config.ini`:

```ini
[voicein]
api_key = sk-...
```

(or the `OPENAI_API_KEY` environment variable). **That's the only configuration needed.**

---

## Usage

```bash
./run.sh        # start the voice input daemon
./history.sh    # open the history viewer (GUI)
```

### Default key bindings

| Key | Paste method | For |
|------|--------------|------|
| Right Ctrl | `Ctrl+V` | Claude / browser / normal text fields |
| Right Shift | `Ctrl+Shift+V` | terminals |

Hold the key to record; release to transcribe and paste. Start/done are signaled by sounds.
A short **`press_delay`** (default 0.15s) keeps accidental taps from firing. Tune keys,
paste methods, and the delay in `config.ini`.

### Helper commands

```bash
./run.sh mics          # list microphone sources (for config's mic_source)
./run.sh keys          # list connected input devices / key names
./run.sh test-inject "any text"   # test injection only
```

---

## Autostart (optional)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/voicein.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now voicein.service
journalctl --user -u voicein -f   # logs
```

---

## Configuration (config.ini)

| Key | Description |
|------|------|
| `api_key` | OpenAI API key (falls back to `OPENAI_API_KEY`) |
| `model` | `gpt-4o-transcribe` (default) / `gpt-4o-mini-transcribe` (cheaper) / `whisper-1` |
| `language` | recognition language (default `ja`; set `en` etc. for others) |
| `prompt` | hint text; list proper nouns / jargon to improve accuracy |
| `mic_source` | which mic to use (see `./run.sh mics`) |
| `sounds` / `notify` | enable sound effects / notifications |
| `max_seconds` / `min_seconds` | max / min recording length |
| `press_delay` | hold the key this long before recording starts (anti-misfire) |
| `[bindings]` | PTT key → paste method mapping |

---

## Requirements

- Linux (developed/verified on **Wayland / GNOME / Ubuntu**; also works on X11 by design)
- Audio: PulseAudio or PipeWire (`parecord`)
- An OpenAI API key (pay-as-you-go; ~$0.006/min with `gpt-4o-transcribe`)

> Note: OpenAI requires prepaid credits. Also, OpenAI tends to reject **JCB** cards — use
> Visa/Mastercard (a debit card works) if a payment fails.

## Troubleshooting

- **Check group**: `groups | grep input`. If missing, log out/in.
- **Keys not detected**: run `./run.sh keys`. If empty, it's a permissions issue.
- **Can't paste into a terminal**: terminals paste with `Ctrl+Shift+V` — speak with Right Shift,
  or change the binding in `config.ini`.
- **Different key**: pick a name from the end of `./run.sh keys` (e.g. `KEY_SCROLLLOCK`,
  `KEY_F12`) and set it in `[bindings]`. USB foot pedals work too.

## License

MIT. Use it however you like.
