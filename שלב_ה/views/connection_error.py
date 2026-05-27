"""Startup screen when the database is unreachable."""

from __future__ import annotations

import customtkinter as ctk

from config import DatabaseConfig
from utils.theme import FONT_BODY, FONT_HEADING, FONT_SMALL, PAD_X, PAD_Y


class ConnectionErrorView(ctk.CTkFrame):
    """Troubleshooting guide when Docker / PostgreSQL is unavailable."""

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
            text="The application could not reach your PostgreSQL server.",
            font=FONT_BODY,
        ).pack(pady=4)

        details = ctk.CTkTextbox(self, width=640, height=120, font=FONT_SMALL)
        details.pack(padx=PAD_X, pady=12)
        details.insert(
            "1.0",
            f"Host: {config.host}\nPort: {config.port}\nDatabase: {config.name}\n"
            f"User: {config.user}\nSchema: {config.schema}\n\nError:\n{error_message}",
        )
        details.configure(state="disabled")

        steps = ctk.CTkTextbox(self, width=640, height=220, font=FONT_BODY, wrap="word")
        steps.pack(padx=PAD_X, pady=8)
        steps.insert(
            "1.0",
            "Troubleshooting steps:\n\n"
            "1. Verify Docker is running:  docker ps\n"
            "2. Start the lab stack:      docker compose up -d db\n"
            "3. Confirm port 5432 is mapped to localhost (see docker-compose.yml)\n"
            "4. If the GUI runs inside Docker, set DB_HOST=db (the service name)\n"
            "5. If the GUI runs on your host, set DB_HOST=localhost\n"
            "6. Copy .env.example to .env and match DB_USER / DB_PASSWORD / DB_NAME "
            "with your compose secrets\n"
            "7. Ensure Stage 3 FDW (staff_remote) and Stage 4 objects are deployed\n"
            "8. Test manually:  psql -h localhost -U <user> -d <dbname> -c '\\dt labs.*'",
        )
        steps.configure(state="disabled")

        ctk.CTkButton(self, text="Retry Connection", width=200, command=on_retry).pack(
            pady=PAD_Y
        )
