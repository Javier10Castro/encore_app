"""
theme.py
Paleta de colores y estilos para la interfaz, basada en un look
"modern fintech / DeFi dashboard": fondo oscuro, tarjetas elevadas,
acentos vibrantes (indigo, cian, violeta) y jerarquía limpia de datos.

Toda la paleta vive aquí; las ventanas solo referencian constantes.
"""

import customtkinter as ctk

# ---- Fondo y superficies ----------------------------------------------
BG = "#0A0F1E"            # Fondo principal (marino profundo)
BG_SOFT = "#0D1427"       # Fondo alterno / zonas secundarias
SURFACE = "#111A30"       # Tarjeta base
SURFACE_2 = "#15203C"     # Tarjeta elevada / campos de entrada
SURFACE_3 = "#1C2A4C"     # Elementos elevados (headers de tabla)
BORDER = "#233153"        # Borde estándar
BORDER_SOFT = "#1B2747"   # Borde suave
HOVER = "#202E52"         # Hover genérico

# ---- Acentos -----------------------------------------------------------
PRIMARY = "#6366F1"       # Indigo (marca / acción principal)
PRIMARY_HOVER = "#818CF8"
PRIMARY_DARK = "#4F46E5"
VIOLET = "#8B5CF6"        # Acento violeta
CYAN = "#22D3EE"          # Acento cian (glow)
EMERALD = "#34D399"       # Éxito
AMBER = "#FBBF24"         # Advertencia
ROSE = "#FB7185"          # Error / peligro

# ---- Texto -------------------------------------------------------------
TEXT = "#E8EEFB"          # Texto principal
TEXT_MUTED = "#9AA9C7"    # Texto secundario
TEXT_FAINT = "#5F6E8B"    # Texto tenue / placeholders

# ---- Aliases de compatibilidad ----------------------------------------
# (nombres heredados de la versión clara; aquí apuntan al esquema oscuro)
NAVY = PRIMARY
NAVY_DARK = PRIMARY_DARK
STEEL_BLUE = CYAN
GRAY = TEXT_MUTED
GRAY_LIGHT = TEXT_FAINT
BG_LIGHT = BG
WHITE = TEXT
SUCCESS = EMERALD
ERROR = ROSE
WARNING = AMBER

# ---- Tipografía --------------------------------------------------------
FONT_FAMILY = "Segoe UI"

TITLE_FONT = (FONT_FAMILY, 26, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 15, "bold")
SECTION_FONT = (FONT_FAMILY, 13, "bold")
LABEL_FONT = (FONT_FAMILY, 13)
BUTTON_FONT = (FONT_FAMILY, 14, "bold")
SMALL_FONT = (FONT_FAMILY, 11)
ENTRY_FONT = (FONT_FAMILY, 13)
KPI_FONT = (FONT_FAMILY, 24, "bold")
KPI_CAPTION_FONT = (FONT_FAMILY, 12)
HEADER_TITLE_FONT = (FONT_FAMILY, 16, "bold")

# ---- Gráficas ----------------------------------------------------------
CHART_COLORS = [
    PRIMARY, CYAN, VIOLET, EMERALD, AMBER, ROSE,
    "#38BDF8", "#A78BFA", "#2DD4BF", "#FDBA74",
    "#F472B6", "#818CF8",
]
TURNO_COLORS = {"A": PRIMARY, "B": CYAN, "C": VIOLET}
CHART_FONT = "Segoe UI"


def apply_global_theme():
    """Configura el modo y el tema base de customtkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


# --------------------------------------------------------------------- #
# Helpers de color
# --------------------------------------------------------------------- #
def _hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def interpolate(c1, c2, t):
    """Interpola entre dos colores hex. t en [0, 1]."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def fmt_num(n):
    """Formatea números enteros con separador de miles."""
    return f"{int(round(n)):,}"


# --------------------------------------------------------------------- #
# Estilos de componentes customtkinter
# --------------------------------------------------------------------- #
def style_primary_button(button: ctk.CTkButton):
    button.configure(
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="#FFFFFF",
        font=BUTTON_FONT,
        corner_radius=10,
        border_width=0,
    )


def style_secondary_button(button: ctk.CTkButton):
    button.configure(
        fg_color="transparent",
        hover_color=HOVER,
        text_color=PRIMARY_HOVER,
        border_width=1,
        border_color=PRIMARY,
        font=BUTTON_FONT,
        corner_radius=10,
    )


def style_ghost_button(button: ctk.CTkButton):
    """Botón oscuro de bajo contraste (barras de herramientas / header)."""
    button.configure(
        fg_color=SURFACE_2,
        hover_color=HOVER,
        text_color=TEXT,
        border_width=1,
        border_color=BORDER_SOFT,
        font=SMALL_FONT,
        corner_radius=8,
    )


def style_danger_button(button: ctk.CTkButton):
    button.configure(
        fg_color=ROSE,
        hover_color="#F8A5B5",
        text_color="#FFFFFF",
        font=BUTTON_FONT,
        corner_radius=10,
        border_width=0,
    )


def style_entry(entry: ctk.CTkEntry):
    entry.configure(
        fg_color=SURFACE_2,
        border_color=BORDER_SOFT,
        border_width=1,
        text_color=TEXT,
        placeholder_text_color=TEXT_FAINT,
    )


def style_option_menu(menu: ctk.CTkOptionMenu):
    menu.configure(
        fg_color=SURFACE_2,
        button_color=PRIMARY,
        button_hover_color=PRIMARY_HOVER,
        text_color=TEXT,
        dropdown_fg_color=SURFACE_2,
        dropdown_hover_color=HOVER,
        dropdown_text_color=TEXT,
    )


def style_treeview(style):
    """Estilo ttk (tablas) coherente con el tema oscuro."""
    style.theme_use("clam")
    style.configure(
        "Treeview",
        rowheight=32,
        font=(FONT_FAMILY, 11),
        background=SURFACE_2,
        fieldbackground=SURFACE_2,
        foreground=TEXT,
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        font=(FONT_FAMILY, 11, "bold"),
        background=SURFACE_3,
        foreground=TEXT,
        borderwidth=0,
        relief="flat",
    )
    style.map("Treeview.Heading",
              background=[("active", HOVER)],
              foreground=[("active", TEXT)])
    style.map("Treeview",
              background=[("selected", PRIMARY)],
              foreground=[("selected", "#FFFFFF")])
    style.configure(
        "Vertical.TScrollbar",
        background=SURFACE_3,
        troughcolor=SURFACE,
        bordercolor=SURFACE,
        arrowcolor=TEXT_FAINT,
        relief="flat",
    )