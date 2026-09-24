"""
theme.py
Paleta de colores corporativos (basada en el logo de Encore / Boeing Company)
y constantes de estilo reutilizadas en toda la aplicación.
"""

import customtkinter as ctk

# ---- Paleta de colores corporativos ------------------------------------
NAVY = "#1F4E79"          # Azul principal (marca)
NAVY_DARK = "#153A5B"     # Azul oscuro (hover / headers)
STEEL_BLUE = "#5A82AA"    # Azul acero (acentos, swoosh del logo)
GRAY = "#58595B"          # Gris corporativo (texto secundario)
GRAY_LIGHT = "#B9BBBD"    # Gris claro (bordes, separadores)
BG_LIGHT = "#F2F3F4"      # Fondo general claro
WHITE = "#FFFFFF"
SUCCESS = "#2E7D32"
ERROR = "#B00020"
WARNING = "#B8860B"

FONT_FAMILY = "Segoe UI"

TITLE_FONT = (FONT_FAMILY, 26, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 15, "bold")
LABEL_FONT = (FONT_FAMILY, 13)
BUTTON_FONT = (FONT_FAMILY, 14, "bold")
SMALL_FONT = (FONT_FAMILY, 11)
ENTRY_FONT = (FONT_FAMILY, 13)


def apply_global_theme():
    """Configura el modo y el tema de color base de customtkinter."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


def style_primary_button(button: ctk.CTkButton):
    button.configure(
        fg_color=NAVY,
        hover_color=NAVY_DARK,
        text_color=WHITE,
        font=BUTTON_FONT,
        corner_radius=8,
    )


def style_secondary_button(button: ctk.CTkButton):
    button.configure(
        fg_color="transparent",
        hover_color=BG_LIGHT,
        text_color=NAVY,
        border_width=2,
        border_color=NAVY,
        font=BUTTON_FONT,
        corner_radius=8,
    )


def style_danger_button(button: ctk.CTkButton):
    button.configure(
        fg_color=ERROR,
        hover_color="#7A0016",
        text_color=WHITE,
        font=BUTTON_FONT,
        corner_radius=8,
    )
