"""
ui/materials_window.py
Función 3: Agregar Materiales.

Formulario: nombre del material -> valida si ya existe (error si existe),
si no existe permite agregarlo. Incluye pestaña "Ver / Editar" con tabla CRUD.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

import database as db
import theme
from ui.widgets import AppHeader, section_card


class MaterialsWindow(ctk.CTkToplevel):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.on_logout = on_logout

        self.title("Encore Group - Agregar Materiales")
        self.geometry("780x680")
        self.minsize(700, 600)
        self.configure(fg_color=theme.BG_LIGHT)
        self.protocol("WM_DELETE_WINDOW", self._logout)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Agregar Materiales", user, on_back=self._back,
                  on_logout=self._logout).grid(row=0, column=0, sticky="ew")

        self.tabs = ctk.CTkTabview(
            self, fg_color=theme.SURFACE, corner_radius=16,
            segmented_button_fg_color=theme.SURFACE_2,
            segmented_button_selected_color=theme.PRIMARY,
            segmented_button_selected_hover_color=theme.PRIMARY_HOVER,
            segmented_button_unselected_color=theme.SURFACE_2,
            segmented_button_unselected_hover_color=theme.HOVER,
            text_color=theme.TEXT_MUTED,
        )
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        self.tabs.add("Agregar")
        self.tabs.add("Ver / Editar")

        self._build_add_tab(self.tabs.tab("Agregar"))
        self._build_list_tab(self.tabs.tab("Ver / Editar"))

    # ================================================================== #
    # Pestaña Agregar
    # ================================================================== #
    def _build_add_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        card = section_card(parent)
        card.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Nuevo material", font=theme.TITLE_FONT,
                     text_color="#FFFFFF").grid(row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        ctk.CTkLabel(card, text="El nombre del material no puede repetirse.",
                     font=theme.LABEL_FONT, text_color=theme.GRAY).grid(
            row=1, column=0, padx=24, pady=(0, 16), sticky="w")

        ctk.CTkLabel(card, text="Nombre del material", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=2, column=0, padx=24, sticky="w")
        self.name_entry = ctk.CTkEntry(card, height=42, font=theme.ENTRY_FONT,
                                        placeholder_text="Ej. Café en grano - Chiapas")
        theme.style_entry(self.name_entry)
        self.name_entry.grid(row=3, column=0, padx=24, pady=(4, 4), sticky="ew")
        self.name_entry.bind("<KeyRelease>", lambda e: self._clear_status())

        self.status_label = ctk.CTkLabel(card, text="", font=theme.SMALL_FONT)
        self.status_label.grid(row=4, column=0, padx=24, pady=(6, 0), sticky="w")

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=5, column=0, padx=24, pady=(16, 24), sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        check_btn = ctk.CTkButton(btn_row, text="Validar existencia", height=42,
                                   command=self._check_material)
        theme.style_secondary_button(check_btn)
        check_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.add_btn = ctk.CTkButton(btn_row, text="Agregar material", height=42,
                                      command=self._add_material, state="disabled")
        theme.style_primary_button(self.add_btn)
        self.add_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _clear_status(self):
        self.status_label.configure(text="")
        self.add_btn.configure(state="disabled")

    def _check_material(self):
        nombre = self.name_entry.get().strip()
        if not nombre:
            self.status_label.configure(text="Escribe el nombre del material.",
                                         text_color=theme.ERROR)
            self.add_btn.configure(state="disabled")
            return

        if db.material_exists(nombre):
            self.status_label.configure(text="❌ Ese material ya existe.", text_color=theme.ERROR)
            self.add_btn.configure(state="disabled")
            messagebox.showerror("Material duplicado",
                                  f'El material "{nombre}" ya está registrado.')
        else:
            self.status_label.configure(text="✔ Disponible, puedes agregarlo.",
                                         text_color=theme.SUCCESS)
            self.add_btn.configure(state="normal")

    def _add_material(self):
        nombre = self.name_entry.get().strip()
        if not nombre:
            return
        if db.material_exists(nombre):
            self.status_label.configure(text="❌ Ese material ya existe.", text_color=theme.ERROR)
            self.add_btn.configure(state="disabled")
            return

        db.add_material(nombre)
        self.status_label.configure(text="✔ Material agregado correctamente.",
                                     text_color=theme.SUCCESS)
        self.name_entry.delete(0, "end")
        self.add_btn.configure(state="disabled")
        self._reload_table()

    # ================================================================== #
    # Pestaña Ver / Editar (CRUD)
    # ================================================================== #
    def _build_list_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        style = ttk.Style()
        theme.style_treeview(style)

        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 10))

        refresh_btn = ctk.CTkButton(toolbar, text="⟳ Actualizar", width=120,
                                     command=self._reload_table)
        theme.style_ghost_button(refresh_btn)
        refresh_btn.pack(side="left")

        edit_btn = ctk.CTkButton(toolbar, text="Editar seleccionado", width=170,
                                  command=self._edit_selected)
        theme.style_primary_button(edit_btn)
        edit_btn.pack(side="left", padx=10)

        delete_btn = ctk.CTkButton(toolbar, text="Eliminar seleccionado", width=170,
                                    command=self._delete_selected)
        theme.style_danger_button(delete_btn)
        delete_btn.pack(side="left")

        table_frame = ctk.CTkFrame(parent, fg_color=theme.SURFACE)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=4)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "nombre")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Material")
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("nombre", width=420)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._reload_table()

    def _reload_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for mat in db.list_materials():
            self.tree.insert("", "end", iid=str(mat["id"]), values=(mat["id"], mat["nombre"]))

    def _get_selected_material(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Selecciona un material", "Primero selecciona una fila de la tabla.")
            return None
        mat_id = int(selection[0])
        conn_row = next((m for m in db.list_materials() if m["id"] == mat_id), None)
        return conn_row

    def _edit_selected(self):
        material = self._get_selected_material()
        if material is None:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar material")
        dialog.geometry("380x240")
        dialog.configure(fg_color=theme.BG)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Editar material", font=theme.SUBTITLE_FONT,
                     text_color="#FFFFFF").pack(pady=(20, 14))

        ctk.CTkLabel(dialog, text="Nombre", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).pack(anchor="w", padx=30)
        name_entry = ctk.CTkEntry(dialog, height=38)
        theme.style_entry(name_entry)
        name_entry.insert(0, material["nombre"])
        name_entry.pack(fill="x", padx=30, pady=(4, 14))

        status_label = ctk.CTkLabel(dialog, text="", font=theme.SMALL_FONT, text_color=theme.ERROR)
        status_label.pack()

        def save_changes():
            nuevo_nombre = name_entry.get().strip()
            if not nuevo_nombre:
                status_label.configure(text="El nombre no puede estar vacío.")
                return
            existentes = [m for m in db.list_materials()
                          if m["nombre"].lower() == nuevo_nombre.lower() and m["id"] != material["id"]]
            if existentes:
                status_label.configure(text="Ya existe un material con ese nombre.")
                return
            db.update_material(material["id"], nuevo_nombre)
            dialog.destroy()
            self._reload_table()

        save_btn = ctk.CTkButton(dialog, text="Guardar cambios", command=save_changes)
        theme.style_primary_button(save_btn)
        save_btn.pack(fill="x", padx=30, pady=(6, 20))

    def _delete_selected(self):
        material = self._get_selected_material()
        if material is None:
            return
        confirm = messagebox.askyesno("Confirmar eliminación",
                                       f'¿Eliminar el material "{material["nombre"]}"?')
        if confirm:
            db.delete_material(material["id"])
            self._reload_table()

    # ------------------------------------------------------------------ #
    def _back(self):
        self.destroy()
        self.on_back()

    def _logout(self):
        self.destroy()
        self.on_logout()
