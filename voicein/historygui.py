"""変換履歴ビューア(Tkinter)。

一覧表示・検索・各行「コピー」ボタン・自動更新を提供する。
キーボードをほぼ使わずに過去の入力を再利用できるよう、行クリックでもコピーできる。
"""
from __future__ import annotations

import subprocess
import tkinter as tk
from tkinter import ttk

from . import history
from .config import HISTORY_PATH


def copy_to_clipboard(root: tk.Tk, text: str) -> None:
    # Wayland では wl-copy を優先。失敗時は Tk のクリップボードへ。
    try:
        subprocess.run(["wl-copy"], input=text.encode("utf-8"), timeout=3, check=True)
        return
    except Exception:
        pass
    try:
        subprocess.run(["xclip", "-selection", "clipboard"],
                       input=text.encode("utf-8"), timeout=3, check=True)
        return
    except Exception:
        pass
    root.clipboard_clear()
    root.clipboard_append(text)


class HistoryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("voicein 変換履歴")
        self.root.geometry("680x560")
        self._last_mtime = 0.0
        self._query = tk.StringVar()
        self._status = tk.StringVar(value="")
        self._build()
        self.refresh(force=True)
        self.root.after(2000, self._poll)

    def _build(self) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="検索:").pack(side="left")
        entry = ttk.Entry(top, textvariable=self._query)
        entry.pack(side="left", fill="x", expand=True, padx=6)
        entry.bind("<KeyRelease>", lambda _e: self.refresh())
        ttk.Button(top, text="再読み込み",
                   command=lambda: self.refresh(force=True)).pack(side="left")

        # スクロール領域
        mid = ttk.Frame(self.root)
        mid.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(mid, highlightthickness=0)
        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = ttk.Frame(self.canvas)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self._win, width=e.width))
        # マウスホイール
        self.canvas.bind_all("<Button-4>", lambda _e: self.canvas.yview_scroll(-2, "units"))
        self.canvas.bind_all("<Button-5>", lambda _e: self.canvas.yview_scroll(2, "units"))
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        bottom = ttk.Frame(self.root, padding=6)
        bottom.pack(fill="x")
        ttk.Label(bottom, textvariable=self._status).pack(side="left")

    def _flash(self, msg: str) -> None:
        self._status.set(msg)
        self.root.after(1500, lambda: self._status.set(""))

    def _copy(self, text: str) -> None:
        copy_to_clipboard(self.root, text)
        preview = text[:30] + ("…" if len(text) > 30 else "")
        self._flash(f"コピーしました: {preview}")

    def refresh(self, force: bool = False) -> None:
        for child in self.inner.winfo_children():
            child.destroy()
        entries = list(reversed(history.load()))  # 新しい順
        q = self._query.get().strip()
        if q:
            entries = [e for e in entries if q in e.text]
        if not entries:
            ttk.Label(self.inner, text="(履歴はまだありません)",
                      padding=20).pack(anchor="w")
        for e in entries:
            self._row(e)
        if force:
            self._flash(f"{len(entries)} 件")

    def _row(self, entry: history.Entry) -> None:
        row = ttk.Frame(self.inner, padding=(8, 6))
        row.pack(fill="x", expand=True)
        meta = entry.ts.replace("T", " ")
        if entry.seconds:
            meta += f"  ({entry.seconds:.0f}s)"
        ttk.Label(row, text=meta, foreground="#888").pack(anchor="w")
        body = ttk.Frame(row)
        body.pack(fill="x", expand=True)
        lbl = tk.Label(body, text=entry.text, justify="left", anchor="w",
                       wraplength=540, cursor="hand2")
        lbl.pack(side="left", fill="x", expand=True)
        lbl.bind("<Button-1>", lambda _e, t=entry.text: self._copy(t))
        ttk.Button(body, text="コピー", width=8,
                   command=lambda t=entry.text: self._copy(t)).pack(side="right")
        ttk.Separator(self.inner, orient="horizontal").pack(fill="x")

    def _poll(self) -> None:
        try:
            mtime = HISTORY_PATH.stat().st_mtime
        except OSError:
            mtime = 0.0
        if mtime != self._last_mtime:
            self._last_mtime = mtime
            self.refresh()
        self.root.after(2000, self._poll)

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    HistoryGUI().run()
    return 0
