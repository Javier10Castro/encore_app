"""
ui/users_window.py
Administración de usuarios (solo visible/accesible para el admin).
Permite crear nuevas cuentas para usar la aplicación localmente.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

import database as db
import theme
from ui.widgets import AppHeader, section_card


class UsersWindow(ctk.CTkToplevel):
    def __init__(self, master, user, on_back, on_logout):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.on_logout = on_logout

        self.title("Encore Group - Usuarios")
        self.geometry("700x640")
        self.minsize(640, 560)
        self.configure(fg_color=theme.BG_LIGHT)
        self.protocol("WM_DELETE_WINDOW", self._logout)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Administrar Usuarios", user, on_back=self._back,
                  on_logout=self._logout).grid(row=0, column=0, sticky="ew")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        self._build_form(body)
        self._build_table(body)
        self._reload_table()

    # ------------------------------------------------------------------ #
    def _build_form(self, parent):
        card = section_card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="Crear nuevo usuario", font=theme.SUBTITLE_FONT,
                     text_color="#FFFFFF").grid(row=0, column=0, columnspan=2,
                                                  padx=18, pady=(16, 10), sticky="w")

        ctk.CTkLabel(card, text="Usuario", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=0, padx=18, sticky="w")
        self.username_entry = ctk.CTkEntry(card, height=38)
        theme.style_entry(self.username_entry)
        self.username_entry.grid(row=2, column=0, padx=18, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(card, text="Contraseña", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=1, padx=18, sticky="w")
        self.password_entry = ctk.CTkEntry(card, height=38, show="•")
        theme.style_entry(self.password_entry)
        self.password_entry.grid(row=2, column=1, padx=18, pady=(4, 12), sticky="ew")

        self.is_admin_var = ctk.BooleanVar(value=False)
        admin_check = ctk.CTkCheckBox(card, text="Es administrador", variable=self.is_admin_var,
                                       fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
                                       text_color=theme.TEXT)
        admin_check.grid(row=3, column=0, padx=18, pady=(0, 6), sticky="w")

        self.status_label = ctk.CTkLabel(card, text="", font=theme.SMALL_FONT)
        self.status_label.grid(row=4, column=0, columnspan=2, padx=18, sticky="w")

        create_btn = ctk.CTkButton(card, text="Crear usuario", height=40, command=self._create_user)
        theme.style_primary_button(create_btn)
        create_btn.grid(row=5, column=0, columnspan=2, padx=18, pady=(12, 18), sticky="ew")

    def _create_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="Usuario y contraseña son obligatorios.",
                                         text_color=theme.ERROR)
            return
        if len(password) < 4:
            self.status_label.configure(text="La contraseña debe tener al menos 4 caracteres.",
                                         text_color=theme.ERROR)
            return
        if db.username_exists(username):
            self.status_label.configure(text="Ese nombre de usuario ya existe.",
                                         text_color=theme.ERROR)
            messagebox.showerror("Usuario duplicado", f'El usuario "{username}" ya existe.')
            return

        db.create_user(username, password, self.is_admin_var.get())
        self.status_label.configure(text="✔ Usuario creado correctamente.", text_color=theme.SUCCESS)
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.is_admin_var.set(False)
        self._reload_table()

    # ------------------------------------------------------------------ #
    def _build_table(self, parent):
        style = ttk.Style()
        theme.style_treeview(style)

        table_wrap = ctk.CTkFrame(parent, fg_color=theme.SURFACE)
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        columns = ("username", "is_admin", "creado_en")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=12)
        self.tree.heading("username", text="Usuario")
        self.tree.heading("is_admin", text="Administrador")
        self.tree.heading("creado_en", text="Creado")
        self.tree.column("username", width=200)
        self.tree.column("is_admin", width=120, anchor="center")
        self.tree.column("creado_en", width=180, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _reload_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in db.list_users():
            self.tree.insert("", "end", values=(u["username"],
                                                  "Sí" if u["is_admin"] else "No",
                                                  u["creado_en"]))

    # ------------------------------------------------------------------ #
    def _back(self):
        self.destroy()
        self.on_back()

    def _logout(self):
        self.destroy()
        self.on_logout()
