"""Main navigation dashboard."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from utils.theme import FONT_BODY, FONT_HEADING, FONT_SUBHEADING, PAD_X, PAD_Y


class DashboardView(ctk.CTkFrame):
    """Landing page with sidebar navigation to all modules."""

    CRUD_MODULES = [
        ("diagnostic_equipment", "Diagnostic Equipment", "🧪"),
        ("lab_test", "Lab Tests", "🔬"),
        ("lab_order", "Lab Orders", "📋"),
        ("lab_technician", "Technicians", "👨‍🔬"),
        ("lab_order_test", "Order Line Items", "🧫"),
        ("lab_result", "Lab Results", "📊"),
    ]

    def __init__(
        self,
        master: ctk.CTk,
        *,
        on_crud: Callable[[str], None],
        on_analytics: Callable[[], None],
        on_toggle_theme: Callable[[], None],
        db_status: str,
    ) -> None:
        super().__init__(master)
        self.on_crud = on_crud
        self.on_analytics = on_analytics
        self.on_toggle_theme = on_toggle_theme

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="Lab Management", font=FONT_HEADING
        ).pack(padx=16, pady=(24, 4), anchor="w")
        ctk.CTkLabel(
            sidebar, text="Hospital Diagnostics", font=FONT_BODY, text_color="gray70"
        ).pack(padx=16, pady=(0, 20), anchor="w")

        ctk.CTkLabel(sidebar, text="CRUD Modules", font=FONT_SUBHEADING).pack(
            padx=16, pady=(8, 4), anchor="w"
        )
        for key, label, icon in self.CRUD_MODULES:
            ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda k=key: self.on_crud(k),
            ).pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(sidebar, text="Analytics & Admin", font=FONT_SUBHEADING).pack(
            padx=16, pady=(20, 4), anchor="w"
        )
        ctk.CTkButton(
            sidebar,
            text="  📈  Queries & Procedures",
            anchor="w",
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.on_analytics,
        ).pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(
            sidebar,
            text="Toggle Light / Dark",
            fg_color="gray30",
            command=self.on_toggle_theme,
        ).pack(side="bottom", fill="x", padx=12, pady=16)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=PAD_X, pady=PAD_Y)
        main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            main,
            text="Medical Laboratory Management System",
            font=("Segoe UI", 30, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        ctk.CTkLabel(
            main,
            text="Stage 5 — Graphical User Interface",
            font=FONT_BODY,
            text_color="gray60",
        ).grid(row=1, column=0, sticky="w", pady=(0, 16))

        status_frame = ctk.CTkFrame(main)
        status_frame.grid(row=2, column=0, sticky="ew", pady=8)
        ctk.CTkLabel(
            status_frame,
            text=f"Connected: {db_status[:80]}…" if len(db_status) > 80 else f"Connected: {db_status}",
            font=FONT_BODY,
            text_color="#2ECC71",
        ).pack(padx=16, pady=12, anchor="w")

        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.grid(row=3, column=0, sticky="nsew", pady=16)
        for i in range(3):
            cards.grid_columnconfigure(i, weight=1)

        self._card(
            cards, 0, "Manage Records",
            "Full CRUD for equipment, tests, orders, technicians, and results. "
            "Foreign keys show human-readable names via SQL JOINs.",
            "Open CRUD",
            lambda: self.on_crud("lab_order"),
        )
        self._card(
            cards, 1, "Analytics & PL/pgSQL",
            "Run Stage 2 analytical queries and invoke Stage 4 procedures "
            "(price sync, technician promotion, doctor workload).",
            "Open Analytics",
            self.on_analytics,
        )
        self._card(
            cards, 2, "Server-Safe UX",
            "Database triggers (e.g. trg_status_protection) surface as clear "
            "error dialogs when a transaction is rejected.",
            "View Orders",
            lambda: self.on_crud("lab_order"),
        )

    def _card(
        self,
        parent: ctk.CTkFrame,
        col: int,
        title: str,
        body: str,
        btn_text: str,
        command: Callable[[], None],
    ) -> None:
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=FONT_SUBHEADING).pack(
            padx=16, pady=(16, 8), anchor="w"
        )
        ctk.CTkLabel(
            card, text=body, font=FONT_BODY, wraplength=260, justify="left"
        ).pack(padx=16, pady=8, anchor="w")
        ctk.CTkButton(card, text=btn_text, command=command).pack(
            padx=16, pady=16, anchor="w"
        )
