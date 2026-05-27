#!/usr/bin/env python3
"""Medical Laboratory Management System — Stage 5 GUI entry point."""

from __future__ import annotations

import sys

import customtkinter as ctk

from config import load_app_config, load_database_config
from db_manager import get_db
from views.analytics.analytics_screen import AnalyticsView
from views.connection_error import ConnectionErrorView
from views.crud.generic_crud import GenericCrudView
from views.crud.table_configs import build_table_configs
from views.dashboard import DashboardView


class LabApplication(ctk.CTk):
    """Root window orchestrating navigation between modules."""

    def __init__(self) -> None:
        super().__init__()
        self.app_config = load_app_config()
        self.db_config = load_database_config()
        self.db = get_db()

        ctk.set_appearance_mode(self.app_config.appearance_mode)
        ctk.set_default_color_theme(self.app_config.color_theme)

        self.title(self.app_config.title)
        self.geometry("1200x760")
        self.minsize(1000, 640)

        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)

        self._current_view: ctk.CTkFrame | None = None
        self._table_configs = None
        self._connected = False
        self._db_version = ""

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._try_connect()

    def _clear_container(self) -> None:
        if self._current_view is not None:
            self._current_view.destroy()
            self._current_view = None

    def _try_connect(self) -> None:
        self._clear_container()
        ok, message = self.db.test_connection()
        if not ok:
            self._connected = False
            self._current_view = ConnectionErrorView(
                self._container,
                self.db_config,
                message,
                on_retry=self._try_connect,
            )
            return

        self._connected = True
        self._db_version = message
        self._table_configs = build_table_configs(self.db.schema)
        self.show_dashboard()

    def show_dashboard(self) -> None:
        if not self._connected:
            self._try_connect()
            return
        self._clear_container()
        self._current_view = DashboardView(
            self._container,
            on_crud=self.show_crud,
            on_analytics=self.show_analytics,
            on_toggle_theme=self._toggle_theme,
            db_status=self._db_version,
        )

    def show_crud(self, module_key: str) -> None:
        if not self._table_configs or module_key not in self._table_configs:
            return
        self._clear_container()
        self._current_view = GenericCrudView(
            self._container,
            self.db,
            self._table_configs[module_key],
            on_back=self.show_dashboard,
        )
        self._current_view.pack(fill="both", expand=True)

    def show_analytics(self) -> None:
        self._clear_container()
        self._current_view = AnalyticsView(
            self._container,
            self.db,
            on_back=self.show_dashboard,
        )
        self._current_view.pack(fill="both", expand=True)

    def _toggle_theme(self) -> None:
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    def _on_close(self) -> None:
        self.db.close_pool()
        self.destroy()


def main() -> int:
    app = LabApplication()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
