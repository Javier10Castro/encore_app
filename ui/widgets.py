"""
ui/widgets.py
Componentes reutilizables: encabezado con logo/marca, y helpers de
validación para Entry (solo números) y OptionMenu (bloquear valor en blanco).
"""

import os
import customtkinter as ctk
from PIL import Image

import theme

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
BLANK_OPTION = "-- Selecciona --"


class AppHeader(ctk.CTkFrame):
    """Encabezado de marca reutilizado en Dashboard y en las funciones."""

    def __init__(self, master, title_text, user, on_back=None, on_logout=None, on_home=None):
        super().__init__(master, fg_color=theme.NAVY, corner_radius=0, height=72)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                w, h = img.size
                new_h = 40
                new_w = int(w * (new_h / h))
                logo_card = ctk.CTkFrame(left, fg_color=theme.WHITE, corner_radius=6)
                logo_card.pack(side="left", padx=(0, 14))
                ctk_img = ctk.CTkImage(light_image=img, size=(new_w, new_h))
                ctk.CTkLabel(logo_card, image=ctk_img, text="").pack(padx=8, pady=4)
            except Exception:
                pass

        if on_home:
            home_btn = ctk.CTkButton(left, text="⌂", width=36, height=36, command=on_home,
                                      fg_color=theme.NAVY_DARK, hover_color=theme.STEEL_BLUE)
            home_btn.pack(side="left", padx=(0, 10))

        if on_back:
            back_btn = ctk.CTkButton(left, text="← Regresar", width=110, height=36, command=on_back,
                                      fg_color=theme.NAVY_DARK, hover_color=theme.STEEL_BLUE,
                                      font=theme.SMALL_FONT)
            back_btn.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(self, text=title_text, font=theme.SUBTITLE_FONT,
                     text_color=theme.WHITE).grid(row=0, column=1, sticky="w")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        uname = user["username"] if user else ""
        ctk.CTkLabel(right, text=f"👤 {uname}", font=theme.SMALL_FONT,
                     text_color=theme.GRAY_LIGHT).pack(side="left", padx=(0, 14))

        if on_logout:
            logout_btn = ctk.CTkButton(right, text="Cerrar sesión", width=110, height=32,
                                        command=on_logout, fg_color=theme.ERROR,
                                        hover_color="#7A0016", font=theme.SMALL_FONT)
            logout_btn.pack(side="left")


def make_numeric_entry(master, **kwargs) -> ctk.CTkEntry:
    """CTkEntry que solo acepta dígitos (bloquea cualquier otro carácter)."""
    vcmd_holder = {}

    entry = ctk.CTkEntry(master, **kwargs)

    def validate(new_value):
        return new_value == "" or new_value.isdigit()

    reg = entry.register(validate)
    entry.configure(validate="key", validatecommand=(reg, "%P"))
    return entry


class BlankLockedOptionMenu(ctk.CTkOptionMenu):
    """
    OptionMenu que inicia en blanco/null y considera "sin seleccionar"
    mientras el valor sea BLANK_OPTION. Útil para materiales y turnos.
    """

    def __init__(self, master, values, **kwargs):
        self._real_values = list(values)
        super().__init__(master, values=[BLANK_OPTION] + self._real_values, **kwargs)
        self.set(BLANK_OPTION)

    def has_valid_selection(self) -> bool:
        return self.get() in self._real_values

    def refresh_values(self, values):
        self._real_values = list(values)
        self.configure(values=[BLANK_OPTION] + self._real_values)
        self.set(BLANK_OPTION)


def section_card(master, **kwargs):
    card = ctk.CTkFrame(master, fg_color=theme.WHITE, corner_radius=14,
                         border_width=1, border_color=theme.GRAY_LIGHT, **kwargs)
    return card


def show_toast_label(label: ctk.CTkLabel, text, ok=True):
    label.configure(text=text, text_color=(theme.SUCCESS if ok else theme.ERROR))
