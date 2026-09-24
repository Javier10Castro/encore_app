"""
ui/capture_window.py
Función 1: Capturar Datos.

Flujo secuencial:
  1) Número de empleado -> botón Validar.
     - No existe -> alerta, permite reintentar.
     - Existe -> muestra nombre/turno y habilita el paso 2.
  2) Dropdown de materiales (inicia en blanco, no permite guardar en blanco).
  3) Cantidad (solo números).
  4) Guardar -> solo habilitado si todo es válido; inserta en `reporte`
     con la fecha/hora actual.
"""

import customtkinter as ctk
from tkinter import messagebox

import database as db
import theme
from ui.widgets import AppHeader, section_card, make_numeric_entry, BlankLockedOptionMenu


class CaptureWindow(ctk.CTkToplevel):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.on_logout = on_logout
        self.validated_employee = None  # dict con numero/nombre/turno una vez validado

        self.title("Encore Group - Capturar Datos")
        self.geometry("760x680")
        self.minsize(680, 620)
        self.configure(fg_color=theme.BG_LIGHT)
        self.protocol("WM_DELETE_WINDOW", self._logout)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Capturar Datos", user, on_back=self._back,
                  on_logout=self._logout).grid(row=0, column=0, sticky="ew")

        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        wrapper.grid_columnconfigure(0, weight=1)

        card = section_card(wrapper)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Capturar Datos", font=theme.TITLE_FONT,
                     text_color="#FFFFFF").grid(row=0, column=0, padx=24, pady=(24, 4), sticky="w")
        ctk.CTkLabel(card, text="Paso 1: valida el número de empleado para continuar.",
                     font=theme.LABEL_FONT, text_color=theme.GRAY).grid(
            row=1, column=0, padx=24, pady=(0, 16), sticky="w")

        # ---- Paso 1: número de empleado ---------------------------------
        step1 = ctk.CTkFrame(card, fg_color="transparent")
        step1.grid(row=2, column=0, padx=24, pady=(0, 6), sticky="ew")
        step1.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(step1, text="# Empleado", font=theme.LABEL_FONT,
                     text_color=theme.GRAY).grid(row=0, column=0, sticky="w")
        row1 = ctk.CTkFrame(step1, fg_color="transparent")
        row1.grid(row=1, column=0, sticky="ew")
        row1.grid_columnconfigure(0, weight=1)

        self.emp_entry = make_numeric_entry(row1, height=40, font=theme.ENTRY_FONT,
                                             placeholder_text="Ej. 1024")
        self.emp_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.emp_entry.bind("<KeyRelease>", lambda e: self._reset_validation())

        validate_btn = ctk.CTkButton(row1, text="Validar", width=110, height=40,
                                      command=self._validate_employee)
        theme.style_primary_button(validate_btn)
        validate_btn.grid(row=0, column=1)

        self.emp_status_label = ctk.CTkLabel(step1, text="", font=theme.SMALL_FONT)
        self.emp_status_label.grid(row=2, column=0, sticky="w", pady=(6, 0))

        self.emp_info_label = ctk.CTkLabel(step1, text="", font=theme.LABEL_FONT,
                                            text_color=theme.PRIMARY_HOVER)
        self.emp_info_label.grid(row=3, column=0, sticky="w", pady=(4, 0))

        # ---- Separador ----------------------------------------------------
        sep1 = ctk.CTkFrame(card, height=1, fg_color=theme.GRAY_LIGHT)
        sep1.grid(row=3, column=0, sticky="ew", padx=24, pady=18)

        # ---- Paso 2: material ----------------------------------------------
        step2 = ctk.CTkFrame(card, fg_color="transparent")
        step2.grid(row=4, column=0, padx=24, pady=(0, 6), sticky="ew")
        step2.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(step2, text="Paso 2: selecciona el material", font=theme.LABEL_FONT,
                     text_color=theme.GRAY).grid(row=0, column=0, sticky="w")
        materiales = db.list_material_names()
        self.material_menu = BlankLockedOptionMenu(step2, values=materiales, height=40,
                                                     command=lambda _v: self._update_save_state())
        self.material_menu.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        if not materiales:
            ctk.CTkLabel(step2, text="⚠ No hay materiales registrados todavía.",
                         font=theme.SMALL_FONT, text_color=theme.WARNING).grid(
                row=2, column=0, sticky="w", pady=(4, 0))

        # ---- Paso 3: cantidad ----------------------------------------------
        step3 = ctk.CTkFrame(card, fg_color="transparent")
        step3.grid(row=5, column=0, padx=24, pady=(18, 6), sticky="ew")
        step3.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(step3, text="Paso 3: cantidad", font=theme.LABEL_FONT,
                     text_color=theme.GRAY).grid(row=0, column=0, sticky="w")
        self.cantidad_entry = make_numeric_entry(step3, height=40, font=theme.ENTRY_FONT,
                                                  placeholder_text="Solo números")
        self.cantidad_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.cantidad_entry.bind("<KeyRelease>", lambda e: self._update_save_state())

        # ---- Guardar ---------------------------------------------------
        self.save_status_label = ctk.CTkLabel(card, text="", font=theme.SMALL_FONT)
        self.save_status_label.grid(row=6, column=0, padx=24, pady=(16, 0), sticky="w")

        self.save_btn = ctk.CTkButton(card, text="Guardar registro", height=44,
                                       command=self._save_entry, state="disabled")
        theme.style_primary_button(self.save_btn)
        self.save_btn.grid(row=7, column=0, padx=24, pady=(10, 24), sticky="ew")

        self._set_step_enabled(False)

    # ------------------------------------------------------------------ #
    def _set_step_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.material_menu.configure(state=state)
        self.cantidad_entry.configure(state=state)

    def _reset_validation(self):
        if self.validated_employee is not None:
            self.validated_employee = None
            self.emp_info_label.configure(text="")
            self.emp_status_label.configure(text="")
            self._set_step_enabled(False)
            self._update_save_state()

    def _validate_employee(self):
        raw = self.emp_entry.get().strip()
        if not raw:
            self.emp_status_label.configure(text="Ingresa un número de empleado.",
                                             text_color=theme.ERROR)
            return

        numero = int(raw)
        empleado = db.get_employee(numero)
        if empleado is None:
            self.validated_employee = None
            self.emp_status_label.configure(
                text="❌ El empleado no existe. Verifica el número e intenta de nuevo.",
                text_color=theme.ERROR)
            self.emp_info_label.configure(text="")
            self._set_step_enabled(False)
            messagebox.showerror("Empleado no encontrado",
                                  f"El empleado #{numero} no existe en la base de datos.")
        else:
            self.validated_employee = empleado
            self.emp_status_label.configure(text="✔ Empleado validado correctamente.",
                                             text_color=theme.SUCCESS)
            self.emp_info_label.configure(
                text=f"{empleado['nombre']}   ·   Turno {empleado['turno']}")
            self._set_step_enabled(True)

        self._update_save_state()

    def _update_save_state(self):
        material_ok = self.material_menu.has_valid_selection() if self.validated_employee else False
        cantidad_raw = self.cantidad_entry.get().strip()
        cantidad_ok = cantidad_raw.isdigit() and int(cantidad_raw) > 0

        if self.validated_employee and material_ok and cantidad_ok:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")

    def _save_entry(self):
        if self.validated_employee is None:
            return
        if not self.material_menu.has_valid_selection():
            self.save_status_label.configure(text="Selecciona un material válido.",
                                              text_color=theme.ERROR)
            return
        cantidad_raw = self.cantidad_entry.get().strip()
        if not cantidad_raw.isdigit() or int(cantidad_raw) <= 0:
            self.save_status_label.configure(text="La cantidad debe ser un número mayor a 0.",
                                              text_color=theme.ERROR)
            return

        db.add_report_entry(
            numero_empleado=self.validated_employee["numero_empleado"],
            nombre=self.validated_employee["nombre"],
            turno=self.validated_employee["turno"],
            material=self.material_menu.get(),
            cantidad=int(cantidad_raw),
        )

        self.save_status_label.configure(text="✔ Registro guardado correctamente.",
                                          text_color=theme.SUCCESS)
        self._clear_form()

    def _clear_form(self):
        self.validated_employee = None
        self.emp_entry.delete(0, "end")
        self.emp_status_label.configure(text="")
        self.emp_info_label.configure(text="")
        self.material_menu.refresh_values(db.list_material_names())
        self.cantidad_entry.delete(0, "end")
        self._set_step_enabled(False)
        self.save_btn.configure(state="disabled")

    # ------------------------------------------------------------------ #
    def _back(self):
        self.destroy()
        self.on_back()

    def _logout(self):
        self.destroy()
        self.on_logout()
