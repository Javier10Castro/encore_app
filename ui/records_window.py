"""
ui/records_window.py
Visualización tipo CRUD de la tabla `reporte` (los datos capturados en
la función 1), con filtros y opción de eliminar registros incorrectos.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

import database as db
import theme
from ui.widgets import AppHeader, section_card, maximize_window


class RecordsWindow(ctk.CTkToplevel):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.on_logout = on_logout

        self.title("Encore Group - Registros")
        self.configure(fg_color=theme.BG_LIGHT)
        self.protocol("WM_DELETE_WINDOW", self._logout)
        maximize_window(self)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Registros de Producción", user, on_back=self._back,
                  on_logout=self._logout).grid(row=0, column=0, sticky="ew")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self._build_filters(body)
        self._build_table(body)
        self._reload_table()

    # ------------------------------------------------------------------ #
    def _build_filters(self, parent):
        card = section_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for i in range(6):
            card.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(card, text="Desde", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=0, column=0, padx=10, pady=(12, 0), sticky="w")
        self.desde_entry = ctk.CTkEntry(card, placeholder_text="AAAA-MM-DD")
        theme.style_entry(self.desde_entry)
        self.desde_entry.grid(row=1, column=0, padx=10, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(card, text="Hasta", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=0, column=1, padx=10, pady=(12, 0), sticky="w")
        self.hasta_entry = ctk.CTkEntry(card, placeholder_text="AAAA-MM-DD")
        theme.style_entry(self.hasta_entry)
        self.hasta_entry.grid(row=1, column=1, padx=10, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(card, text="Turno", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=0, column=2, padx=10, pady=(12, 0), sticky="w")
        self.turno_menu = ctk.CTkOptionMenu(card, values=["Todos", "A", "B", "C"])
        theme.style_option_menu(self.turno_menu)
        self.turno_menu.set("Todos")
        self.turno_menu.grid(row=1, column=2, padx=10, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(card, text="Material", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=0, column=3, padx=10, pady=(12, 0), sticky="w")
        self.material_menu = ctk.CTkOptionMenu(card, values=["Todos"] + db.list_material_names())
        theme.style_option_menu(self.material_menu)
        self.material_menu.set("Todos")
        self.material_menu.grid(row=1, column=3, padx=10, pady=(0, 12), sticky="ew")

        apply_btn = ctk.CTkButton(card, text="Filtrar", command=self._reload_table)
        theme.style_primary_button(apply_btn)
        apply_btn.grid(row=1, column=4, padx=10, pady=(0, 12), sticky="ew")

        clear_btn = ctk.CTkButton(card, text="Limpiar", command=self._clear_filters)
        theme.style_secondary_button(clear_btn)
        clear_btn.grid(row=1, column=5, padx=10, pady=(0, 12), sticky="ew")

    def _clear_filters(self):
        self.desde_entry.delete(0, "end")
        self.hasta_entry.delete(0, "end")
        self.turno_menu.set("Todos")
        self.material_menu.set("Todos")
        self._reload_table()

    # ------------------------------------------------------------------ #
    def _build_table(self, parent):
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew")
        toolbar.grid_columnconfigure(0, weight=1)

        refresh_btn = ctk.CTkButton(toolbar, text="⟳ Actualizar", width=120,
                                     command=self._reload_table)
        theme.style_ghost_button(refresh_btn)
        refresh_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))

        delete_btn = ctk.CTkButton(toolbar, text="Eliminar seleccionado", width=180,
                                    command=self._delete_selected)
        theme.style_danger_button(delete_btn)
        delete_btn.grid(row=0, column=2, sticky="e")

        table_wrap = ctk.CTkFrame(parent, fg_color=theme.SURFACE)
        table_wrap.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        parent.grid_rowconfigure(2, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        theme.style_treeview(style)

        columns = ("id", "numero", "nombre", "turno", "material", "cantidad", "fecha")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=16)
        headers = {"id": "ID", "numero": "# Empleado", "nombre": "Nombre", "turno": "Turno",
                   "material": "Material", "cantidad": "Cantidad", "fecha": "Fecha"}
        widths = {"id": 50, "numero": 90, "nombre": 180, "turno": 60,
                  "material": 200, "cantidad": 80, "fecha": 150}
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col],
                              anchor="center" if col in ("id", "numero", "turno", "cantidad") else "w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _reload_table(self):
        self.material_menu.configure(values=["Todos"] + db.list_material_names())
        for row in self.tree.get_children():
            self.tree.delete(row)

        desde = self.desde_entry.get().strip() or None
        hasta = self.hasta_entry.get().strip() or None
        entries = db.list_report_entries(desde, hasta, self.turno_menu.get(), self.material_menu.get())
        for e in entries:
            self.tree.insert("", "end", iid=str(e["id"]),
                              values=(e["id"], e["numero_empleado"], e["nombre"], e["turno"],
                                      e["material"], e["cantidad"], e["fecha"]))

    def _delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Selecciona un registro", "Primero selecciona una fila de la tabla.")
            return
        entry_id = int(selection[0])
        confirm = messagebox.askyesno("Confirmar eliminación",
                                       "¿Eliminar este registro del reporte?")
        if confirm:
            db.delete_report_entry(entry_id)
            self._reload_table()

    # ------------------------------------------------------------------ #
    def _back(self):
        self.destroy()
        self.on_back()

    def _logout(self):
        self.destroy()
        self.on_logout()
