"""Reusable CRUD screen with smart lookup and FK dropdowns."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import customtkinter as ctk
from tkinter import ttk

from db_manager import DatabaseError, DatabaseManager
from utils import dialogs
from utils.theme import FONT_BODY, FONT_HEADING, FONT_SMALL, PAD_X, PAD_Y
from views.crud.table_configs import FieldConfig, TableConfig, editable_columns


class GenericCrudView(ctk.CTkFrame):
    """Create / read / update / delete for a single laboratory table."""

    def __init__(
        self,
        master: ctk.CTk,
        db: DatabaseManager,
        config: TableConfig,
        on_back: callable,
    ) -> None:
        super().__init__(master)
        self.db = db
        self.config = config
        self.on_back = on_back
        self._widgets: dict[str, Any] = {}
        self._fk_maps: dict[str, dict[str, Any]] = {}
        self._loaded_pk: Any = None

        self._build_ui()
        self.refresh_grid()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD_X, pady=(PAD_Y, 8))
        ctk.CTkButton(header, text="← Back", width=90, command=self.on_back).pack(
            side="left"
        )
        ctk.CTkLabel(
            header, text=self.config.title, font=FONT_HEADING
        ).pack(side="left", padx=16)

        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=PAD_X, pady=8)

        left = ctk.CTkFrame(body, width=360)
        left.pack(side="left", fill="y", padx=(0, 12), pady=4)
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="Smart Update Lookup", font=FONT_BODY).pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        lookup_row = ctk.CTkFrame(left, fg_color="transparent")
        lookup_row.pack(fill="x", padx=12)
        self.lookup_entry = ctk.CTkEntry(
            lookup_row, placeholder_text=f"Enter {self.config.lookup_label}"
        )
        self.lookup_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(lookup_row, text="Load", width=70, command=self.load_record).pack(
            side="left"
        )

        ctk.CTkLabel(left, text="Record Form", font=FONT_BODY).pack(
            anchor="w", padx=12, pady=(16, 4)
        )
        self.form_scroll = ctk.CTkScrollableFrame(left, width=330)
        self.form_scroll.pack(fill="both", expand=True, padx=8, pady=4)
        self._build_form_fields()

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(btn_row, text="Create", command=self.create_record).pack(
            side="left", padx=4
        )
        ctk.CTkButton(btn_row, text="Update", command=self.update_record).pack(
            side="left", padx=4
        )
        ctk.CTkButton(
            btn_row, text="Delete", fg_color="#8B2942", hover_color="#6B1F32",
            command=self.delete_record,
        ).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Clear", fg_color="gray30", command=self.clear_form).pack(
            side="left", padx=4
        )

        right = ctk.CTkFrame(body)
        right.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(
            right, text="All Records (human-readable FKs)", font=FONT_BODY
        ).pack(anchor="w", padx=8, pady=8)
        ctk.CTkButton(
            right, text="Refresh Grid", width=120, command=self.refresh_grid
        ).pack(anchor="e", padx=8)

        tree_frame = ctk.CTkFrame(right)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Lab.Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=26,
        )
        style.configure(
            "Lab.Treeview.Heading",
            background="#1f538d",
            foreground="white",
            font=(FONT_BODY[0], 11, "bold"),
        )

        self.tree = ttk.Treeview(tree_frame, style="Lab.Treeview", show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    def _build_form_fields(self) -> None:
        for widget in self.form_scroll.winfo_children():
            widget.destroy()
        self._widgets.clear()
        self._fk_maps.clear()

        for field in self.config.fields:
            ctk.CTkLabel(
                self.form_scroll, text=field.label, font=FONT_SMALL
            ).pack(anchor="w", pady=(8, 2))
            widget = self._create_field_widget(field)
            widget.pack(fill="x", pady=(0, 4))
            self._widgets[field.column] = widget

    def _create_field_widget(self, field: FieldConfig) -> Any:
        if field.field_type == "choice":
            w = ctk.CTkComboBox(self.form_scroll, values=field.choices, state="readonly")
            if field.choices:
                w.set(field.choices[0])
            return w
        if field.field_type == "fk":
            return self._create_fk_combo(field)
        if field.field_type == "readonly":
            w = ctk.CTkEntry(self.form_scroll)
            w.configure(state="disabled")
            return w
        return ctk.CTkEntry(self.form_scroll)

    def _create_fk_combo(self, field: FieldConfig) -> ctk.CTkComboBox:
        combo = ctk.CTkComboBox(self.form_scroll, values=["Loading…"], state="readonly")
        try:
            rows = self.db.get_fk_options(field.fk_query or "")
            display_values: list[str] = []
            id_map: dict[str, Any] = {}
            for pk_val, label in rows:
                text = str(label)
                display_values.append(text)
                id_map[text] = pk_val
            if not display_values:
                display_values = ["(No options available)"]
            combo.configure(values=display_values)
            combo.set(display_values[0])
            self._fk_maps[field.column] = id_map
        except Exception as exc:
            combo.configure(values=[f"(FK load failed: {exc})"])
            combo.set(combo.cget("values")[0])
            self._fk_maps[field.column] = {}
        return combo

    def refresh_grid(self) -> None:
        try:
            rows = self.db.execute(self.config.list_sql, fetch="all") or []
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)
            return

        self.tree.delete(*self.tree.get_children())
        if not rows:
            return

        columns = list(rows[0].keys())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=max(100, len(col) * 12), anchor="w")

        for row in rows:
            values = [self._format_cell(row[c]) for c in columns]
            self.tree.insert("", "end", iid=str(row.get(self.config.pk, "")), values=values)

    def load_record(self) -> None:
        pk_raw = self.lookup_entry.get().strip()
        if not pk_raw:
            dialogs.show_warning(self.winfo_toplevel(), "Enter a record ID to load.")
            return
        try:
            pk_val = int(pk_raw)
        except ValueError:
            dialogs.show_warning(self.winfo_toplevel(), "Record ID must be a number.")
            return

        try:
            row = self.db.execute(self.config.fetch_sql, (pk_val,), fetch="one")
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)
            return

        if not row:
            dialogs.show_warning(self.winfo_toplevel(), "No record found with that ID.")
            return

        self._loaded_pk = pk_val
        self._populate_form(row)

    def _populate_form(self, row: dict[str, Any]) -> None:
        for field in self.config.fields:
            widget = self._widgets.get(field.column)
            if widget is None:
                continue
            value = row.get(field.column)
            if field.field_type == "fk":
                id_map = self._fk_maps.get(field.column, {})
                label = next((k for k, v in id_map.items() if v == value), None)
                if label:
                    widget.set(label)
            elif field.field_type == "choice":
                widget.set(str(value) if value is not None else "")
            elif field.field_type == "readonly":
                widget.configure(state="normal")
                widget.delete(0, "end")
                widget.insert(0, self._format_cell(value))
                widget.configure(state="disabled")
            else:
                widget.delete(0, "end")
                widget.insert(0, self._format_cell(value))

    def _on_row_select(self, _event: Any = None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        pk = selected[0]
        self.lookup_entry.delete(0, "end")
        self.lookup_entry.insert(0, pk)
        self.load_record()

    def create_record(self) -> None:
        values, columns = self._collect_form_values(creating=True)
        if values is None:
            return
        try:
            result = self.db.execute(self.config.insert_sql, values, fetch="one")
            new_id = result[list(result.keys())[0]] if result else "?"
            dialogs.show_success(
                self.winfo_toplevel(),
                f"Created {self.config.title} (ID: {new_id}).",
            )
            self.clear_form()
            self.refresh_grid()
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def update_record(self) -> None:
        pk = self._loaded_pk
        if pk is None:
            pk_raw = self.lookup_entry.get().strip()
            if not pk_raw:
                dialogs.show_warning(
                    self.winfo_toplevel(),
                    "Load a record first or enter its ID in the lookup field.",
                )
                return
            try:
                pk = int(pk_raw)
            except ValueError:
                dialogs.show_warning(self.winfo_toplevel(), "Invalid record ID.")
                return

        values, _ = self._collect_form_values(creating=False)
        if values is None:
            return
        values = list(values) + [pk]
        try:
            self.db.execute(self.config.update_sql, values)
            dialogs.show_success(self.winfo_toplevel(), "Record updated successfully.")
            self._loaded_pk = pk
            self.refresh_grid()
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def delete_record(self) -> None:
        pk = self._loaded_pk
        if pk is None:
            pk_raw = self.lookup_entry.get().strip()
            if not pk_raw:
                dialogs.show_warning(self.winfo_toplevel(), "Select or load a record to delete.")
                return
            try:
                pk = int(pk_raw)
            except ValueError:
                dialogs.show_warning(self.winfo_toplevel(), "Invalid record ID.")
                return

        if not dialogs.confirm(
            self.winfo_toplevel(),
            f"Permanently delete {self.config.title} #{pk}?",
        ):
            return
        try:
            self.db.execute(self.config.delete_sql, (pk,))
            dialogs.show_success(self.winfo_toplevel(), "Record deleted.")
            self.clear_form()
            self.refresh_grid()
        except DatabaseError as exc:
            dialogs.show_error(self.winfo_toplevel(), str(exc), detail=exc.detail)

    def clear_form(self) -> None:
        self._loaded_pk = None
        self.lookup_entry.delete(0, "end")
        for field in self.config.fields:
            widget = self._widgets.get(field.column)
            if widget is None:
                continue
            if field.field_type in ("choice", "fk"):
                vals = widget.cget("values")
                if vals:
                    widget.set(vals[0])
            elif field.field_type == "readonly":
                widget.configure(state="normal")
                widget.delete(0, "end")
                widget.configure(state="disabled")
            else:
                widget.delete(0, "end")

    def _collect_form_values(
        self, *, creating: bool
    ) -> tuple[tuple[Any, ...], list[str]] | tuple[None, None]:
        cols: list[str] = []
        vals: list[Any] = []
        for field in editable_columns(self.config, creating=creating):
            raw = self._read_field(field)
            if raw is None and field.required:
                dialogs.show_warning(
                    self.winfo_toplevel(), f"'{field.label}' is required."
                )
                return None, None
            cols.append(field.column)
            vals.append(raw)
        return tuple(vals), cols

    def _read_field(self, field: FieldConfig) -> Any:
        widget = self._widgets[field.column]
        if field.field_type == "fk":
            label = widget.get()
            mapped = self._fk_maps.get(field.column, {}).get(label)
            return mapped
        if field.field_type == "choice":
            return widget.get()
        if field.field_type == "readonly":
            return None
        text = widget.get().strip()
        if not text and not field.required:
            return None
        if field.field_type == "int":
            return int(text)
        if field.field_type == "float":
            return float(text)
        if field.field_type == "date":
            return date.fromisoformat(text)
        if field.field_type == "datetime":
            return datetime.fromisoformat(text.replace(" ", "T", 1))
        return text

    @staticmethod
    def _format_cell(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M")
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)
