"""Main navigation dashboard in English."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from utils.theme import FONT_BODY, FONT_HEADING, FONT_SUBHEADING, PAD_X, PAD_Y


class DashboardView(ctk.CTkFrame):
    """Landing page with sidebar navigation to all modules in English."""

    CRUD_MODULES = [
        ("diagnostic_equipment", "Diagnostic Equipment", "🧪"),
        ("lab_test", "Lab Tests", "🔬"),
        ("lab_order", "Lab Orders", "📋"),
        ("lab_technician", "Lab Technicians", "👨‍🔬"),
        ("lab_order_test", "Order Tests", "🧫"),
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

        # Sidebar navigation
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="Lab Management", font=FONT_HEADING
        ).pack(padx=16, pady=(24, 20), anchor="w")

        ctk.CTkLabel(sidebar, text="Tables & Records", font=FONT_SUBHEADING).pack(
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

        ctk.CTkLabel(sidebar, text="Reports & Admin", font=FONT_SUBHEADING).pack(
            padx=16, pady=(20, 4), anchor="w"
        )
        ctk.CTkButton(
            sidebar,
            text="  📈  Reports & Actions",
            anchor="w",
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.on_analytics,
        ).pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(
            sidebar,
            text="Toggle Light / Dark 🌓",
            fg_color="gray30",
            hover_color="gray40",
            command=self.on_toggle_theme,
        ).pack(side="bottom", fill="x", padx=12, pady=16)

        # Main Workspace
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=PAD_X, pady=PAD_Y)
        main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            main,
            text="Laboratory Management System",
            font=("Segoe UI", 30, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Connection status bar
        status_frame = ctk.CTkFrame(main)
        status_frame.grid(row=2, column=0, sticky="ew", pady=8)
        
        status_prefix = "Connected to Database: "
        display_status = db_status[:70] + "..." if len(db_status) > 70 else db_status
        ctk.CTkLabel(
            status_frame,
            text=f"{status_prefix}{display_status}",
            font=FONT_BODY,
            text_color="#2ECC71",
        ).pack(padx=16, pady=12, anchor="w")

        # Dynamic dashboard cards
        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.grid(row=3, column=0, sticky="nsew", pady=16)
        for i in range(3):
            cards.grid_columnconfigure(i, weight=1)

        self._card(
            cards, 0, "Manage Records",
            "View, add, update, and delete laboratory records, including equipment, tests, orders, technicians, and results.",
            "Open Records 📋",
            lambda: self.on_crud("lab_order"),
        )
        self._card(
            cards, 1, "Reports & Actions",
            "Run administrative database procedures, analyze doctor workloads, and view clinical test demand statistics.",
            "Open Reports 📈",
            self.on_analytics,
        )
        self._card(
            cards, 2, "Data Integrity",
            "The application enforces hospital database policy rules (Triggers) to prevent modification of locked or completed orders.",
            "View Orders 🔍",
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
        
        # Use high-contrast adaptive colors for body text to ensure readability on all appearance modes
        ctk.CTkLabel(
            card, 
            text=body, 
            font=FONT_BODY, 
            text_color=("gray10", "gray90"),
            wraplength=260, 
            justify="left"
        ).pack(padx=16, pady=8, anchor="w")
        
        ctk.CTkButton(card, text=btn_text, command=command).pack(
            padx=16, pady=16, anchor="w"
        )
