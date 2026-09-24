"""
ui/login_window.py
Pantalla de inicio de sesión. Valida contra la tabla `usuarios` de SQLite.
Estilo: split panel con degradado + decoración "glass hero" y formulario
en tarjeta elevada (tema oscuro fintech).
"""

import os

import customtkinter as ctk
from PIL import Image

import database as db
import theme
from ui.widgets import GradientFrame, maximize_window


class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success

        self.title("Encore Group - Iniciar Sesión")
        self.configure(fg_color=theme.BG)
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        maximize_window(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

        self.bind("<Return>", lambda e: self._attempt_login())

    # ------------------------------------------------------------------ #
    def _build_left_panel(self):
        left = GradientFrame(
            self,
            colors=[theme.BG, theme.PRIMARY_DARK, theme.VIOLET],
            vertical=True,
            decorations=True,
            corner_radius=0,
        )
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure(0, weight=1)
        left.grid_rowconfigure(4, weight=1)
        left.grid_columnconfigure(0, weight=1)

        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "assets", "logo.png")
        container = ctk.CTkFrame(left, fg_color="transparent")
        container.grid(row=2, column=0)

        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                w, h = img.size
                new_w = 300
                new_h = int(h * (new_w / w))
                logo_card = ctk.CTkFrame(container, fg_color="#FFFFFF", corner_radius=14,
                                         border_width=1, border_color=theme.BORDER_SOFT)
                logo_card.pack(pady=(0, 22), padx=10)
                ctk_img = ctk.CTkImage(light_image=img, size=(new_w, new_h))
                ctk.CTkLabel(logo_card, image=ctk_img, text="").pack(padx=20, pady=16)
            except Exception:
                pass

        ctk.CTkLabel(
            container, text="Sistema de Captura de Producción",
            font=(theme.FONT_FAMILY, 20, "bold"), text_color="#FFFFFF",
            wraplength=360, justify="center",
        ).pack(pady=(0, 6))
        ctk.CTkLabel(
            container, text="Control de empleados, materiales y turnos",
            font=theme.LABEL_FONT, text_color=theme.TEXT_MUTED,
        ).pack()

        badge = ctk.CTkFrame(container, fg_color=theme.SURFACE_2, corner_radius=14,
                             border_width=1, border_color=theme.BORDER_SOFT)
        badge.pack(pady=(22, 0))
        ctk.CTkLabel(badge, text="📊  Dashboard en tiempo real", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).pack(padx=16, pady=8)

    # ------------------------------------------------------------------ #
    def _build_right_panel(self):
        right = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(right, fg_color=theme.SURFACE, corner_radius=20,
                            border_width=1, border_color=theme.BORDER)
        form.grid(row=1, column=0, padx=50, pady=40)

        ctk.CTkLabel(form, text="Bienvenido", font=theme.TITLE_FONT,
                     text_color="#FFFFFF").grid(row=0, column=0, padx=50, pady=(40, 4), sticky="w")
        ctk.CTkLabel(form, text="Inicia sesión para continuar", font=theme.LABEL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=0, padx=50,
                                                        pady=(0, 24), sticky="w")

        ctk.CTkLabel(form, text="Usuario", font=theme.LABEL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=2, column=0, padx=50, sticky="w")
        self.username_entry = ctk.CTkEntry(form, width=300, height=40, font=theme.ENTRY_FONT,
                                            placeholder_text="usuario")
        theme.style_entry(self.username_entry)
        self.username_entry.grid(row=3, column=0, padx=50, pady=(4, 16))

        ctk.CTkLabel(form, text="Contraseña", font=theme.LABEL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=4, column=0, padx=50, sticky="w")
        self.password_entry = ctk.CTkEntry(form, width=300, height=40, font=theme.ENTRY_FONT,
                                            placeholder_text="contraseña", show="•")
        theme.style_entry(self.password_entry)
        self.password_entry.grid(row=5, column=0, padx=50, pady=(4, 8))

        self.error_label = ctk.CTkLabel(form, text="", font=theme.SMALL_FONT,
                                        text_color=theme.ERROR)
        self.error_label.grid(row=6, column=0, padx=50, sticky="w")

        login_btn = ctk.CTkButton(form, text="Iniciar sesión", width=300, height=42,
                                   command=self._attempt_login)
        theme.style_primary_button(login_btn)
        login_btn.grid(row=7, column=0, padx=50, pady=(12, 16))

        ctk.CTkLabel(form, text="Acceso inicial · admin / admin123",
                     font=theme.SMALL_FONT, text_color=theme.TEXT_FAINT).grid(
            row=8, column=0, padx=50, pady=(0, 40))

        self.username_entry.focus()

    # ------------------------------------------------------------------ #
    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Ingresa usuario y contraseña.")
            return

        user = db.verify_login(username, password)
        if user is None:
            self.error_label.configure(text="Usuario o contraseña incorrectos.")
            self.password_entry.delete(0, "end")
            return

        self.error_label.configure(text="")
        self.destroy()
        self.on_login_success(user)