"""Startup screen when the database is unreachable, in English."""

from __future__ import annotations

import customtkinter as ctk

from config import DatabaseConfig
from utils.theme import FONT_BODY, FONT_HEADING, FONT_SMALL, PAD_X, PAD_Y


class ConnectionErrorView(ctk.CTkFrame):
    """Troubleshooting guide when Docker / PostgreSQL is unavailable, in English."""

    def __init__(
        self,
        master: ctk.CTk,
        config: DatabaseConfig,
        error_message: str,
        on_retry: callable,
    ) -> None:
        super().__init__(master)
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self,
            text="Database Connection Failed",
            font=FONT_HEADING,
            text_color="#E74C3C",
        ).pack(pady=(PAD_Y * 2, 8))

        ctk.CTkLabel(
            self,
            text="The application could not reach the hospital database server.",
            font=FONT_BODY,
        ).pack(pady=4)

        details = ctk.CTkTextbox(self, width=640, height=120, font=FONT_SMALL)
        details.pack(padx=PAD_X, pady=12)
        details.insert(
            "1.0",
            f"Host: {config.host}\n"
            f"Port: {config.port}\n"
            f"Database: {config.name}\n"
            f"User: {config.user}\n"
            f"Schema: {config.schema}\n\n"
            f"Error details:\n{error_message}",
        )
        details.configure(state="disabled")

        steps = ctk.CTkTextbox(self, width=640, height=220, font=FONT_BODY, wrap="word")
        steps.pack(padx=PAD_X, pady=8)
        steps.insert(
            "1.0",
            "Troubleshooting steps:\n\n"
            "1. Verify Docker is running on your system.\n"
            "2. Start the database stack using:  docker compose up -d db\n"
            "3. Confirm port 5432 is mapped to localhost.\n"
            "4. If the app runs inside Docker, set the host configuration parameter to 'db'.\n"
            "5. If the app runs on your host machine, set the host parameter to 'localhost'.\n"
            "6. Copy .env.example to .env and match the connection credentials.\n"
            "7. Ensure Stage 3 FDW tables (staff_remote) and Stage 4 routines are deployed on the server."
        )
        steps.configure(state="disabled")

        ctk.CTkButton(
            self, 
            text="Retry Connection 🔄", 
            width=200, 
            fg_color="#1f538d",
            hover_color="#14375e",
            command=on_retry
        ).pack(pady=PAD_Y)
