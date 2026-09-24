"""
ui/employees_window.py
Función 2: Agregar Empleados.

Flujo secuencial:
  1) Número de empleado -> Validar (debe NO existir para continuar).
  2) Nombre + Turno (dropdown A/B/C, inicia en blanco).
  3) Guardar.

Incluye una pestaña "Ver / Editar" con tabla CRUD completa.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

import database as db
import theme
from ui.widgets import AppHeader, section_card, make_numeric_entry, BlankLockedOptionMenu


class EmployeesWindow(ctk.CTkToplevel):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.on_logout = on_logout
        self.validated_new_number = None  # número validado como disponible (no existe aún)
        self.selected_row_number = None   # empleado seleccionado en la tabla (editar)

        self.title("Encore Group - Agregar Empleados")
        self.geometry("900x720")
        self.minsize(820, 640)
        self.configure(fg_color=theme.BG_LIGHT)
        self.protocol("WM_DELETE_WINDOW", self._logout)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Agregar Empleados", user, on_back=self._back,
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

        ctk.CTkLabel(card, text="Paso 1: número de empleado (debe ser nuevo)",
                     font=theme.LABEL_FONT, text_color=theme.GRAY).grid(
            row=0, column=0, padx=24, pady=(20, 4), sticky="w")

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.grid(row=1, column=0, padx=24, sticky="ew")
        row1.grid_columnconfigure(0, weight=1)

        self.new_emp_entry = make_numeric_entry(row1, height=40, font=theme.ENTRY_FONT,
                                                  placeholder_text="Ej. 2048")
        self.new_emp_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.new_emp_entry.bind("<KeyRelease>", lambda e: self._reset_validation())

        validate_btn = ctk.CTkButton(row1, text="Validar", width=110, height=40,
                                      command=self._validate_new_employee)
        theme.style_primary_button(validate_btn)
        validate_btn.grid(row=0, column=1)

        self.new_emp_status = ctk.CTkLabel(card, text="", font=theme.SMALL_FONT)
        self.new_emp_status.grid(row=2, column=0, padx=24, pady=(6, 0), sticky="w")

        sep = ctk.CTkFrame(card, height=1, fg_color=theme.GRAY_LIGHT)
        sep.grid(row=3, column=0, sticky="ew", padx=24, pady=18)

        ctk.CTkLabel(card, text="Paso 2: datos del empleado", font=theme.LABEL_FONT,
                     text_color=theme.GRAY).grid(row=4, column=0, padx=24, sticky="w")

        ctk.CTkLabel(card, text="Nombre", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=5, column=0, padx=24, pady=(12, 0), sticky="w")
        self.name_entry = ctk.CTkEntry(card, height=40, font=theme.ENTRY_FONT,
                                        placeholder_text="Nombre completo", state="disabled")
        theme.style_entry(self.name_entry)
        self.name_entry.grid(row=6, column=0, padx=24, pady=(4, 0), sticky="ew")
        self.name_entry.bind("<KeyRelease>", lambda e: self._update_save_state())

        ctk.CTkLabel(card, text="Turno", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=7, column=0, padx=24, pady=(12, 0), sticky="w")
        self.turno_menu = BlankLockedOptionMenu(card, values=["A", "B", "C"], height=40,
                                                  state="disabled",
                                                  command=lambda _v: self._update_save_state())
        self.turno_menu.grid(row=8, column=0, padx=24, pady=(4, 0), sticky="ew")

        self.save_status = ctk.CTkLabel(card, text="", font=theme.SMALL_FONT)
        self.save_status.grid(row=9, column=0, padx=24, pady=(16, 0), sticky="w")

        self.save_btn = ctk.CTkButton(card, text="Guardar empleado", height=44,
                                       command=self._save_employee, state="disabled")
        theme.style_primary_button(self.save_btn)
        self.save_btn.grid(row=10, column=0, padx=24, pady=(10, 24), sticky="ew")

    def _reset_validation(self):
        if self.validated_new_number is not None:
            self.validated_new_number = None
            self.new_emp_status.configure(text="")
            self.name_entry.configure(state="disabled")
            self.name_entry.delete(0, "end")
            self.turno_menu.configure(state="disabled")
            self.turno_menu.refresh_values(["A", "B", "C"])
            self._update_save_state()

    def _validate_new_employee(self):
        raw = self.new_emp_entry.get().strip()
        if not raw:
            self.new_emp_status.configure(text="Ingresa un número de empleado.",
                                           text_color=theme.ERROR)
            return
        numero = int(raw)
        if db.employee_exists(numero):
            self.validated_new_number = None
            self.new_emp_status.configure(
                text="❌ Ese número de empleado ya existe. Usa otro.", text_color=theme.ERROR)
            self.name_entry.configure(state="disabled")
            self.turno_menu.configure(state="disabled")
            messagebox.showerror("Empleado duplicado",
                                  f"El empleado #{numero} ya está registrado.")
        else:
            self.validated_new_number = numero
            self.new_emp_status.configure(text="✔ Número disponible, puedes continuar.",
                                           text_color=theme.SUCCESS)
            self.name_entry.configure(state="normal")
            self.turno_menu.configure(state="normal")
        self._update_save_state()

    def _update_save_state(self):
        name_ok = bool(self.name_entry.get().strip())
        turno_ok = self.turno_menu.has_valid_selection()
        if self.validated_new_number is not None and name_ok and turno_ok:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")

    def _save_employee(self):
        if self.validated_new_number is None:
            return
        nombre = self.name_entry.get().strip()
        turno = self.turno_menu.get()
        if not nombre or not self.turno_menu.has_valid_selection():
            self.save_status.configure(text="Completa nombre y turno.", text_color=theme.ERROR)
            return

        db.add_employee(self.validated_new_number, nombre, turno)
        self.save_status.configure(text="✔ Empleado guardado correctamente.",
                                    text_color=theme.SUCCESS)
        self._clear_add_form()
        self._reload_table()

    def _clear_add_form(self):
        self.validated_new_number = None
        self.new_emp_entry.delete(0, "end")
        self.new_emp_status.configure(text="")
        self.name_entry.delete(0, "end")
        self.name_entry.configure(state="disabled")
        self.turno_menu.refresh_values(["A", "B", "C"])
        self.turno_menu.configure(state="disabled")
        self.save_btn.configure(state="disabled")

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

        columns = ("numero", "nombre", "turno")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        self.tree.heading("numero", text="# Empleado")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("turno", text="Turno")
        self.tree.column("numero", width=120, anchor="center")
        self.tree.column("nombre", width=320)
        self.tree.column("turno", width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._reload_table()

    def _reload_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for emp in db.list_employees():
            self.tree.insert("", "end", iid=str(emp["numero_empleado"]),
                              values=(emp["numero_empleado"], emp["nombre"], emp["turno"]))
        # también refresca los dropdowns de materiales/turno relacionados si aplica
        self._update_save_state()

    def _get_selected_employee(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Selecciona un empleado", "Primero selecciona una fila de la tabla.")
            return None
        numero = int(selection[0])
        return db.get_employee(numero)

    def _edit_selected(self):
        empleado = self._get_selected_employee()
        if empleado is None:
            return
        self._open_edit_dialog(empleado)

    def _open_edit_dialog(self, empleado):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar empleado")
        dialog.geometry("380x320")
        dialog.configure(fg_color=theme.BG)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Editar empleado #{empleado['numero_empleado']}",
                     font=theme.SUBTITLE_FONT, text_color="#FFFFFF").pack(pady=(20, 14))

        ctk.CTkLabel(dialog, text="Nombre", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).pack(anchor="w", padx=30)
        name_entry = ctk.CTkEntry(dialog, height=38)
        theme.style_entry(name_entry)
        name_entry.insert(0, empleado["nombre"])
        name_entry.pack(fill="x", padx=30, pady=(4, 14))

        ctk.CTkLabel(dialog, text="Turno", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).pack(anchor="w", padx=30)
        turno_menu = ctk.CTkOptionMenu(dialog, values=["A", "B", "C"])
        theme.style_option_menu(turno_menu)
        turno_menu.set(empleado["turno"])
        turno_menu.pack(fill="x", padx=30, pady=(4, 20))

        status_label = ctk.CTkLabel(dialog, text="", font=theme.SMALL_FONT)
        status_label.pack()

        def save_changes():
            nombre = name_entry.get().strip()
            if not nombre:
                status_label.configure(text="El nombre no puede estar vacío.",
                                        text_color=theme.ERROR)
                return
            db.update_employee(empleado["numero_empleado"], nombre, turno_menu.get())
            dialog.destroy()
            self._reload_table()

        save_btn = ctk.CTkButton(dialog, text="Guardar cambios", command=save_changes)
        theme.style_primary_button(save_btn)
        save_btn.pack(fill="x", padx=30, pady=(0, 20))

    def _delete_selected(self):
        empleado = self._get_selected_employee()
        if empleado is None:
            return
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar al empleado #{empleado['numero_empleado']} ({empleado['nombre']})?\n"
            "Nota: los registros históricos en el reporte no se eliminan.")
        if confirm:
            db.delete_employee(empleado["numero_empleado"])
            self._reload_table()

    # ------------------------------------------------------------------ #
    def _back(self):
        self.destroy()
        self.on_back()

    def _logout(self):
        self.destroy()
        self.on_logout()
