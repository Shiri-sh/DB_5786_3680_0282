"""Advanced queries and PL/pgSQL routines view in English."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable

import customtkinter as ctk
from tkinter import ttk

from db_manager import DatabaseError, DatabaseManager
from utils import dialogs
from utils.theme import FONT_BODY, FONT_HEADING, FONT_SUBHEADING, FONT_SMALL, PAD_X, PAD_Y
from views.crud.generic_crud import COLUMN_TRANSLATIONS


class AnalyticsView(ctk.CTkFrame):
    """Stage 2 analytical queries and Stage 4 procedures/functions in English."""

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
        
        ctk.CTkButton(
            header, 
            text="← Back", 
            width=90, 
            font=FONT_SUBHEADING,
            fg_color="gray30",
            hover_color="gray40",
            command=self.on_back
        ).pack(side="left")
        
        ctk.CTkLabel(
            header, 
            text="Data Analytics & Administration", 
            font=FONT_HEADING
        ).pack(side="left", padx=16)

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=PAD_X, pady=8)

        tab_queries = tabs.add("Analytical Reports")
        tab_proc = tabs.add("System Actions")
        tab_fn = tabs.add("Workload")
        tab_custom = tabs.add("Free Query")

        self._build_queries_tab(tab_queries)
        self._build_procedures_tab(tab_proc)
        self._build_workload_tab(tab_fn)
        self._build_custom_query_tab(tab_custom)

        result_frame = ctk.CTkFrame(self)
        result_frame.pack(fill="both", expand=True, padx=PAD_X, pady=(0, PAD_Y))

        ctk.CTkLabel(result_frame, text="Query Results", font=FONT_SUBHEADING).pack(
            anchor="w", padx=12, pady=8
        )
        inner = ctk.CTkFrame(result_frame)
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Analytics.Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=26,
        )
        style.configure(
            "Analytics.Treeview.Heading",
            background="#1f538d",
            foreground="white",
            font=(FONT_BODY[0], 11, "bold"),
        )

        self.result_tree = ttk.Treeview(inner, style="Analytics.Treeview", show="headings")
        vsb = ttk.Scrollbar(inner, orient="vertical", command=self.result_tree.yview)
        hsb = ttk.Scrollbar(inner, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.result_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

    def _create_card(self, parent: ctk.CTkFrame, title: str, desc: str) -> ctk.CTkFrame:
        """Create a beautifully styled medical dashboard card."""
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("#e0e0e0", "#3d3d3d"),
            fg_color=("#fcfcfc", "#212121"),
        )
        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_SUBHEADING,
            text_color=("#2c3e50", "#3498db"),
        ).pack(anchor="w", padx=14, pady=(10, 4))
        
        # High contrast readable description text
        ctk.CTkLabel(
            card,
            text=desc,
            font=FONT_SMALL,
            text_color=("gray10", "gray90"),
            wraplength=480,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))
        return card

    def _build_queries_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # Card 1: Popular Tests
        card_popular = self._create_card(
            parent,
            "📊 Top 5 Popular Tests",
            "Executive report analyzing lab test demand to display the top 5 most frequently ordered tests based on total order records."
        )
        card_popular.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        
        ctk.CTkButton(
            card_popular,
            text="Generate Popularity Report",
            font=FONT_BODY,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.run_popular_tests,
        ).pack(padx=14, pady=(0, 14), anchor="w")

        # Card 2: Urgent Pending Orders
        card_urgent = self._create_card(
            parent,
            "⚠️ Urgent Pending Orders",
            "Monitoring report displaying urgent laboratory orders that have remained uncompleted for over 48 hours to prevent diagnostic delays."
        )
        card_urgent.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")

        ctk.CTkButton(
            card_urgent,
            text="Retrieve Delayed Orders",
            font=FONT_BODY,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.run_urgent_monitoring,
        ).pack(padx=14, pady=(0, 14), anchor="w")

    def _build_procedures_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # Card 1: Price Sync
        card_price = self._create_card(
            parent,
            "🔄 Global Price Synchronization",
            "System procedure to automatically recalculate and update total order prices based on active test line item costs."
        )
        card_price.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        ctk.CTkButton(
            card_price,
            text="Run Global Price Sync",
            font=FONT_BODY,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.run_price_sync,
        ).pack(padx=14, pady=(0, 14), anchor="w")

        # Card 2: Promote Technicians
        card_promote = self._create_card(
            parent,
            "🎁 Technician Bonus Promotion",
            "Administrative process to grant bonus points to certified lab technicians who successfully complete orders beyond the system target."
        )
        card_promote.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")

        form = ctk.CTkFrame(card_promote, fg_color="transparent")
        form.pack(anchor="w", padx=14, pady=(0, 10))
        
        ctk.CTkLabel(form, text="Target Orders:", font=FONT_SMALL).grid(row=0, column=0, padx=(0, 4))
        self.min_tests_entry = ctk.CTkEntry(form, width=70, font=FONT_SMALL)
        self.min_tests_entry.insert(0, "5")
        self.min_tests_entry.grid(row=0, column=1, padx=4)
        
        ctk.CTkLabel(form, text="Bonus Points:", font=FONT_SMALL).grid(row=0, column=2, padx=(10, 4))
        self.bonus_entry = ctk.CTkEntry(form, width=70, font=FONT_SMALL)
        self.bonus_entry.insert(0, "10")
        self.bonus_entry.grid(row=0, column=3, padx=4)

        ctk.CTkButton(
            card_promote,
            text="Execute Bonus Promotion",
            font=FONT_BODY,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            command=self.run_promote_technicians,
        ).pack(padx=14, pady=(0, 14), anchor="w")

    def _build_workload_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)

        card_workload = self._create_card(
            parent,
            "🔍 Doctor Active Workload Search",
            "Select a physician from the medical staff list to retrieve their active and urgent laboratory orders."
        )
        card_workload.pack(fill="x", padx=12, pady=12)

        row = ctk.CTkFrame(card_workload, fg_color="transparent")
        row.pack(anchor="w", padx=14, pady=(0, 14))
        
        ctk.CTkLabel(row, text="Select Doctor:", font=FONT_BODY).pack(side="left", padx=(0, 8))
        self.doctor_combo = ctk.CTkComboBox(
            row, values=["Loading doctors..."], width=320, font=FONT_BODY
        )
        self.doctor_combo.pack(side="left", padx=8)
        
        ctk.CTkButton(
            row,
            text="Fetch Workload",
            font=FONT_BODY,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.run_doctor_workload
        ).pack(side="left", padx=8)

    def _build_custom_query_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)

        card_custom = self._create_card(
            parent,
            "⚡ Custom Database Query Builder",
            "Administrator tool to execute custom search and retrieval statements. Only SELECT queries are permitted."
        )
        card_custom.pack(fill="both", expand=True, padx=12, pady=12)

        self.custom_query_text = ctk.CTkTextbox(card_custom, height=80, font=FONT_SMALL)
        self.custom_query_text.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        self.custom_query_text.insert("1.0", "SELECT test_name, cost, normal_range FROM labs.lab_test LIMIT 10;")

        ctk.CTkButton(
            card_custom,
            text="Execute Query",
            font=FONT_BODY,
            fg_color="#16a085",
            hover_color="#117a65",
            command=self.run_custom_query,
        ).pack(padx=14, pady=(0, 14), anchor="w")

    def _load_doctors(self) -> None:
        sql = """
            SELECT staffid, firstname || ' ' || lastname AS full_name
            FROM staff_remote
            ORDER BY full_name, staffid
        """
        try:
            rows = self.db.execute(sql, fetch="all") or []
            labels: list[str] = []
            self._doctor_map.clear()
            for row in rows:
                display_name = f"{row['full_name']} (ID: {row['staffid']})"
                labels.append(display_name)
                self._doctor_map[display_name] = row["staffid"]
            if not labels:
                labels = ["(No doctors in database)"]
            self.doctor_combo.configure(values=labels)
            self.doctor_combo.set(labels[0])
            self._setup_combobox_autocomplete(self.doctor_combo, labels)
        except DatabaseError:
            self.doctor_combo.configure(values=["(Staff registry unavailable)"])
            self.doctor_combo.set("(Staff registry unavailable)")

    def _setup_combobox_autocomplete(self, combo: ctk.CTkComboBox, original_values: list[str]) -> None:
        def on_keyrelease(event: Any) -> None:
            if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Tab"):
                return
            typed = combo.get()
            if not typed:
                filtered = original_values
            else:
                typed_lower = typed.lower()
                filtered = [v for v in original_values if typed_lower in v.lower()]
            combo.configure(values=filtered if filtered else ["(No matches)"])
            try:
                combo._open_dropdown_menu()
            except Exception:
                pass
            combo.focus()

        combo.bind("<KeyRelease>", on_keyrelease)

    def run_popular_tests(self) -> None:
        schema = self.db.schema
        sql = f"""
            SELECT t.test_name AS "Test Name", COUNT(*) AS "Order Count"
            FROM "{schema}"."lab_order_test" ot
            JOIN "{schema}"."lab_test" t ON ot.test_id = t.test_id
            GROUP BY t.test_name
            ORDER BY "Order Count" DESC
            LIMIT 5
        """
        self._run_and_display(sql, title="Most Popular Tests")

    def run_urgent_monitoring(self) -> None:
        schema = self.db.schema
        sql = f"""
            SELECT o.lab_order_id AS "Order ID",
                   COALESCE(d.firstname || ' ' || d.lastname,
                            'Doctor #' || o.doctor_id::text) AS "Doctor Name",
                   o.order_date AS "Order Date", o.status AS "Status", o.priority AS "Priority",
                   CURRENT_DATE - o.order_date AS "Days Pending"
            FROM "{schema}"."lab_order" o
            LEFT JOIN staff_remote d ON o.doctor_id = d.staffid
            WHERE o.priority = 'URGENT'
              AND o.status != 'COMPLETED'
              AND o.order_date < CURRENT_DATE - INTERVAL '2 days'
            ORDER BY o.order_date
        """
        self._run_and_display(sql, title="Urgent Pending Orders")

    def run_price_sync(self) -> None:
        try:
            self.db.call_procedure("public.pr_update_all_order_prices")
            dialogs.show_success(
                self.winfo_toplevel(),
                "Global order price synchronization completed. Refreshing prices...",
            )
            schema = self.db.schema
            sql = f"""
                SELECT lab_order_id AS "Order ID",
                       COALESCE(total_price, 0) AS "Total Price ($)",
                       status AS "Status", priority AS "Priority"
                FROM "{schema}"."lab_order"
                ORDER BY lab_order_id
                LIMIT 100
            """
            self._run_and_display(sql, title="Updated Order Prices")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def run_promote_technicians(self) -> None:
        try:
            min_tests = int(self.min_tests_entry.get().strip())
            bonus = int(self.bonus_entry.get().strip())
        except ValueError:
            dialogs.show_warning(
                self.winfo_toplevel(), "Target orders and bonus points must be integers."
            )
            return
        try:
            notices = self.db.call_procedure("public.pr_promote_technicians", (min_tests, bonus))
            # call_procedure doesn't return notices directly, let's use execute_many_notices instead
            notices = self.db.execute_many_notices(
                "CALL public.pr_promote_technicians(%s, %s)",
                (min_tests, bonus),
            )
            lines = notices or ["Bonus promotion completed successfully."]
            dialogs.DetailDialog(
                self.winfo_toplevel(),
                "Technician bonus promotion logs (RAISE NOTICE)",
                lines,
            )
            schema = self.db.schema
            sql = f"""
                SELECT t.technician_id AS "Technician ID",
                       COALESCE(s.firstname || ' ' || s.lastname,
                                'Staff #' || t.staff_id::text) AS "Technician Name",
                       t.certification AS "Certification",
                       COALESCE(t.bonus_points, 0) AS "Bonus Points"
                FROM "{schema}"."lab_technician" t
                LEFT JOIN staff_remote s ON t.staff_id = s.staffid
                ORDER BY t.bonus_points DESC
                LIMIT 50
            """
            self._run_and_display(sql, title="Technician Bonus Points")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def run_doctor_workload(self) -> None:
        name = self.doctor_combo.get()
        doctor_id = self._doctor_map.get(name)
        if doctor_id is None:
            dialogs.show_warning(
                self.winfo_toplevel(),
                "Please select a valid doctor from the list.",
            )
            return
        try:
            rows = self.db.fetch_doctor_workload(doctor_id)
            if not rows:
                dialogs.show_info(
                    self.winfo_toplevel(),
                    "Doctor Workload",
                    f"No active urgent orders found for {name}.",
                )
            renamed_rows = []
            for r in rows:
                renamed_rows.append({
                    "Order ID": r.get("lab_order_id"),
                    "Order Date": r.get("order_date"),
                    "Priority": r.get("priority")
                })
            self._display_rows(renamed_rows, title=f"Active Orders — {name}")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def run_custom_query(self) -> None:
        sql = self.custom_query_text.get("1.0", "end").strip()
        if not sql:
            dialogs.show_warning(self.winfo_toplevel(), "Please enter an SQL query.")
            return
        if not sql.lower().startswith("select"):
            dialogs.show_warning(self.winfo_toplevel(), "For security reasons, only SELECT queries are allowed.")
            return
        self._run_and_display(sql, title="Custom Query Results")

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
            self.result_tree.insert("", "end", values=("No records found.",))
            return

        columns = list(rows[0].keys())
        self.result_tree["columns"] = columns
        for col in columns:
            translated = COLUMN_TRANSLATIONS.get(col.lower(), col.replace("_", " ").title())
            self.result_tree.heading(col, text=translated)
            self.result_tree.column(col, width=max(120, len(translated) * 12), anchor="w")
        for row in rows:
            self.result_tree.insert(
                "",
                "end",
                values=[str(row[c]) if row[c] is not None else "" for c in columns],
            )
