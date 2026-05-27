"""Advanced queries and Stage 4 PL/pgSQL invocation."""

from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk
from tkinter import ttk

from db_manager import DatabaseError, DatabaseManager
from utils import dialogs
from utils.theme import FONT_BODY, FONT_HEADING, FONT_SMALL, PAD_X, PAD_Y


class AnalyticsView(ctk.CTkFrame):
    """Stage 2 analytical queries and Stage 4 procedures/functions."""

    def __init__(
        self,
        master: ctk.CTk,
        db: DatabaseManager,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.db = db
        self.on_back = on_back
        self._doctor_map: dict[str, int] = {}

        self._build_ui()
        self._load_doctors()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD_X, pady=(PAD_Y, 8))
        ctk.CTkButton(header, text="← Back", width=90, command=self.on_back).pack(
            side="left"
        )
        ctk.CTkLabel(
            header, text="Analytics & Administration", font=FONT_HEADING
        ).pack(side="left", padx=16)

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=PAD_X, pady=8)

        tab_queries = tabs.add("Stage 2 Queries")
        tab_proc = tabs.add("Procedures")
        tab_fn = tabs.add("Doctor Workload")

        self._build_queries_tab(tab_queries)
        self._build_procedures_tab(tab_proc)
        self._build_workload_tab(tab_fn)

        result_frame = ctk.CTkFrame(self)
        result_frame.pack(fill="both", expand=True, padx=PAD_X, pady=(0, PAD_Y))

        ctk.CTkLabel(result_frame, text="Results", font=FONT_BODY).pack(
            anchor="w", padx=8, pady=8
        )
        inner = ctk.CTkFrame(result_frame)
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        self.result_tree = ttk.Treeview(inner, show="headings")
        vsb = ttk.Scrollbar(inner, orient="vertical", command=self.result_tree.yview)
        hsb = ttk.Scrollbar(inner, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.result_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

    def _build_queries_tab(self, parent: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            parent,
            text="Stage 2 — Advanced analytical queries",
            font=FONT_BODY,
        ).pack(anchor="w", padx=12, pady=12)

        ctk.CTkButton(
            parent,
            text="Popular Tests (Top 5 by usage)",
            command=self.run_popular_tests,
        ).pack(anchor="w", padx=12, pady=4)

        ctk.CTkLabel(
            parent,
            text="From select_2.sql — test statistics via JOIN + GROUP BY",
            font=FONT_SMALL,
            text_color="gray60",
        ).pack(anchor="w", padx=24, pady=(0, 12))

        ctk.CTkButton(
            parent,
            text="Urgent Orders Pending (>2 days)",
            command=self.run_urgent_monitoring,
        ).pack(anchor="w", padx=12, pady=4)

        ctk.CTkLabel(
            parent,
            text="From select_6.sql — high-priority order monitoring",
            font=FONT_SMALL,
            text_color="gray60",
        ).pack(anchor="w", padx=24, pady=(0, 12))

    def _build_procedures_tab(self, parent: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            parent, text="pr_update_all_order_prices", font=FONT_BODY
        ).pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkLabel(
            parent,
            text="Batch-sync LAB_ORDER.total_price for every order, then refresh the grid.",
            font=FONT_SMALL,
            text_color="gray60",
            wraplength=500,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 8))
        ctk.CTkButton(
            parent,
            text="Run Global Price Sync",
            command=self.run_price_sync,
        ).pack(anchor="w", padx=12, pady=4)

        ctk.CTkLabel(
            parent, text="pr_promote_technicians", font=FONT_BODY
        ).pack(anchor="w", padx=12, pady=(20, 4))

        form = ctk.CTkFrame(parent, fg_color="transparent")
        form.pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(form, text="Minimum Tests:").grid(row=0, column=0, padx=4)
        self.min_tests_entry = ctk.CTkEntry(form, width=80)
        self.min_tests_entry.insert(0, "5")
        self.min_tests_entry.grid(row=0, column=1, padx=4)
        ctk.CTkLabel(form, text="Bonus Points:").grid(row=0, column=2, padx=4)
        self.bonus_entry = ctk.CTkEntry(form, width=80)
        self.bonus_entry.insert(0, "10")
        self.bonus_entry.grid(row=0, column=3, padx=4)
        ctk.CTkButton(
            form, text="Promote Technicians", command=self.run_promote_technicians
        ).grid(row=0, column=4, padx=12)

    def _build_workload_tab(self, parent: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            parent,
            text="fn_get_doctor_workload — urgent active orders by doctor",
            font=FONT_BODY,
        ).pack(anchor="w", padx=12, pady=12)

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(row, text="Doctor:").pack(side="left", padx=4)
        self.doctor_combo = ctk.CTkComboBox(
            row, values=["Loading doctors…"], width=320, state="readonly"
        )
        self.doctor_combo.pack(side="left", padx=8)
        ctk.CTkButton(
            row, text="Fetch Workload", command=self.run_doctor_workload
        ).pack(side="left", padx=8)

    def _load_doctors(self) -> None:
        sql = """
            SELECT staffid, firstname || ' ' || lastname AS full_name
            FROM staff_remote
            ORDER BY full_name
        """
        try:
            rows = self.db.execute(sql, fetch="all") or []
            labels: list[str] = []
            self._doctor_map.clear()
            for row in rows:
                name = row["full_name"]
                labels.append(name)
                self._doctor_map[name] = row["staffid"]
            if not labels:
                labels = ["(No doctors in staff_remote)"]
            self.doctor_combo.configure(values=labels)
            self.doctor_combo.set(labels[0])
        except DatabaseError:
            self.doctor_combo.configure(values=["(staff_remote unavailable)"])
            self.doctor_combo.set("(staff_remote unavailable)")

    def run_popular_tests(self) -> None:
        schema = self.db.schema
        sql = f"""
            SELECT t.test_name, COUNT(*) AS usage_count
            FROM "{schema}"."LAB_ORDER_TEST" ot
            JOIN "{schema}"."LAB_TEST" t ON ot.test_id = t.test_id
            GROUP BY t.test_name
            ORDER BY usage_count DESC
            LIMIT 5
        """
        self._run_and_display(sql, title="Popular Tests")

    def run_urgent_monitoring(self) -> None:
        schema = self.db.schema
        sql = f"""
            SELECT o.lab_order_id,
                   COALESCE(d.firstname || ' ' || d.lastname,
                            'Doctor #' || o.doctor_id::text) AS doctor,
                   o.order_date, o.status, o.priority,
                   CURRENT_DATE - o.order_date AS days_open
            FROM "{schema}"."LAB_ORDER" o
            LEFT JOIN staff_remote d ON o.doctor_id = d.staffid
            WHERE o.priority = 'URGENT'
              AND o.status != 'COMPLETED'
              AND o.order_date < CURRENT_DATE - INTERVAL '2 days'
            ORDER BY o.order_date
        """
        self._run_and_display(sql, title="Urgent Pending Orders")

    def run_price_sync(self) -> None:
        try:
            self.db.call_procedure(f"{self.db.schema}.pr_update_all_order_prices")
            dialogs.show_success(
                self.winfo_toplevel(),
                "pr_update_all_order_prices completed. Refreshing order pricing view…",
            )
            schema = self.db.schema
            sql = f"""
                SELECT lab_order_id,
                       COALESCE(total_price, 0) AS total_price,
                       status, priority
                FROM "{schema}"."LAB_ORDER"
                ORDER BY lab_order_id
                LIMIT 100
            """
            self._run_and_display(sql, title="Orders After Price Sync")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def run_promote_technicians(self) -> None:
        try:
            min_tests = int(self.min_tests_entry.get().strip())
            bonus = int(self.bonus_entry.get().strip())
        except ValueError:
            dialogs.show_warning(
                self.winfo_toplevel(), "Minimum Tests and Bonus Points must be integers."
            )
            return
        try:
            notices = self.db.execute_many_notices(
                f"CALL {self.db.schema}.pr_promote_technicians(%s, %s)",
                (min_tests, bonus),
            )
            lines = notices or ["Procedure completed (no NOTICE messages captured)."]
            dialogs.DetailDialog(
                self.winfo_toplevel(),
                "Promotion Log (RAISE NOTICE)",
                lines,
            )
            schema = self.db.schema
            sql = f"""
                SELECT t.technician_id,
                       COALESCE(s.firstname || ' ' || s.lastname,
                                'Staff #' || t.staff_id::text) AS technician,
                       t.certification,
                       COALESCE(t.bonus_points, 0) AS bonus_points
                FROM "{schema}"."LAB_TECHNICIAN" t
                LEFT JOIN staff_remote s ON t.staff_id = s.staffid
                ORDER BY t.bonus_points DESC
                LIMIT 50
            """
            self._run_and_display(sql, title="Technicians After Promotion")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def run_doctor_workload(self) -> None:
        name = self.doctor_combo.get()
        doctor_id = self._doctor_map.get(name)
        if doctor_id is None:
            dialogs.show_warning(
                self.winfo_toplevel(),
                "Select a valid doctor from the staff_remote directory.",
            )
            return
        try:
            rows = self.db.fetch_doctor_workload(doctor_id)
            if not rows:
                dialogs.show_info(
                    self.winfo_toplevel(),
                    "Workload",
                    f"No urgent active orders for {name}.",
                )
            self._display_rows(rows, title=f"Workload — {name}")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def _run_and_display(self, sql: str, *, title: str) -> None:
        try:
            rows = self.db.execute(sql, fetch="all") or []
            self._display_rows(rows, title=title)
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def _display_rows(self, rows: list[dict[str, Any]], *, title: str) -> None:
        self.result_tree.delete(*self.result_tree.get_children())
        if not rows:
            self.result_tree["columns"] = ("message",)
            self.result_tree.heading("message", text=title)
            self.result_tree.insert("", "end", values=("No rows returned.",))
            return

        columns = list(rows[0].keys())
        self.result_tree["columns"] = columns
        for col in columns:
            self.result_tree.heading(col, text=col.replace("_", " ").title())
            self.result_tree.column(col, width=120, anchor="w")
        for row in rows:
            self.result_tree.insert(
                "",
                "end",
                values=[str(row[c]) if row[c] is not None else "" for c in columns],
            )
