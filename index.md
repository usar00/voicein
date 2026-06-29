# voicein

**Linux voice input that runs on just an OpenAI API key.**

Hold a key, speak, release — the text lands in whatever app you have open
(Claude, your browser, a terminal…). No local models, no fiddly setup.
Register one API key and it works. Works in Japanese and any other language.

[**View on GitHub →**](https://github.com/usar00/voicein){: .btn }

---

## What it does

- **Push-to-talk**: record only while a key is held; release to transcribe.
- **OpenAI `gpt-4o-transcribe`**: natural punctuation, great Japanese, any language.
- **Pastes at the cursor** of the focused app via a virtual keyboard — Wayland & X11.
- **History viewer (GUI)**: list, search, and copy past transcriptions in one click.

## Quick start

```bash
git clone https://github.com/usar00/voicein.git
cd voicein
bash install.sh        # deps + permissions + venv
# log out / back in once (input group), then put your API key in config.ini
./run.sh
```

Then hold **Right Ctrl**, speak, release. That's it.

## Docs

- [README (English)](https://github.com/usar00/voicein/blob/master/README.en.md)
- [README (日本語)](https://github.com/usar00/voicein/blob/master/README.md)
- License: **MIT** — use it however you like.

---

Built because good voice input on Linux is either a paid subscription or a heavy
local-model setup. This one just needs an API key (~$0.006/min).
