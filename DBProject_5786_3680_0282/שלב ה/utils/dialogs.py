"""User feedback dialogs."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from utils.theme import FONT_BODY, FONT_SUBHEADING


def show_info(parent: ctk.CTk, title: str, message: str) -> None:
    messagebox.showinfo(title, message, parent=parent)


def show_success(parent: ctk.CTk, message: str) -> None:
    messagebox.showinfo("Success", message, parent=parent)


def show_warning(parent: ctk.CTk, message: str) -> None:
    messagebox.showwarning("Warning", message, parent=parent)


def show_error(parent: ctk.CTk, message: str, *, detail: str | None = None) -> None:
    text = message
    if detail and detail not in message:
        text = f"{message}\n\nDetails:\n{detail}"
    messagebox.showerror("Error", text, parent=parent)


def confirm(parent: ctk.CTk, message: str, *, title: str = "Confirm") -> bool:
    return messagebox.askyesno(title, message, parent=parent)


class DetailDialog(ctk.CTkToplevel):
    """Scrollable dialog for long server messages (e.g. promotion logs)."""

    def __init__(self, parent: ctk.CTk, title: str, lines: list[str]) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("560x420")
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(self, text=title, font=FONT_SUBHEADING).pack(
            padx=16, pady=(16, 8), anchor="w"
        )
        box = ctk.CTkTextbox(self, font=FONT_BODY, wrap="word")
        box.pack(fill="both", expand=True, padx=16, pady=8)
        box.insert("1.0", "\n".join(lines) if lines else "(No log messages returned.)")
        box.configure(state="disabled")
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=12)
