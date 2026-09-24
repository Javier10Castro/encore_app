"""
ui/widgets.py
Componentes reutilizables del tema "modern fintech":
  - GradientFrame: fondo degradado (Canvas) para headers y paneles.
  - AppHeader: encabezado de marca con degradado, logo y acciones.
  - StatCard: tarjeta de indicador (KPI) con icono y acento de color.
  - Helpers de entrada (numérica) y OptionMenu que inicia en blanco.
"""

import os
import tkinter as tk

import customtkinter as ctk
from PIL import Image

import theme

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
BLANK_OPTION = "-- Selecciona --"


# --------------------------------------------------------------------- #
# Fondo degradado
# --------------------------------------------------------------------- #
class GradientFrame(ctk.CTkFrame):
    """Fondo con degradado horizontal o vertical. Se redibuja al redimensionar.

    Opcionalmente dibuja círculos decorativos (estilo "glass hero").
    """

    def __init__(self, master, colors, vertical=False, decorations=False, **kwargs):
        kwargs.setdefault("fg_color", colors[0])
        super().__init__(master, **kwargs)
        self._colors = colors
        self._vertical = vertical
        self._decorations = decorations
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=colors[0])
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        c = self.canvas
        c.delete("grad")
        c.delete("deco")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            return

        n = len(self._colors)
        segs = max(1, n - 1)

        if self._vertical:
            for y in range(h):
                pos = (y / max(1, h - 1)) * segs
                i = min(int(pos), segs - 1)
                col = theme.interpolate(self._colors[i], self._colors[i + 1], pos - i)
                c.create_line(0, y, w, y, fill=col, tags="grad")
        else:
            for x in range(w):
                pos = (x / max(1, w - 1)) * segs
                i = min(int(pos), segs - 1)
                col = theme.interpolate(self._colors[i], self._colors[i + 1], pos - i)
                c.create_line(x, 0, x, h, fill=col, tags="grad")

        if self._decorations:
            self._draw_decorations(w, h)

    def _draw_decorations(self, w, h):
        c = self.canvas
        # Aro superior-izquierdo
        c.create_oval(int(0.03 * w), int(0.05 * h), int(0.28 * w), int(0.42 * h),
                      outline="#3B4E92", width=2, tags="deco")
        # Aro inferior-derecho
        c.create_oval(int(0.70 * w), int(0.62 * h), int(1.02 * w), int(1.05 * h),
                      outline="#164E63", width=2, tags="deco")
        # Aro medio-derecho
        c.create_oval(int(0.78 * w), int(0.10 * h), int(0.98 * w), int(0.36 * h),
                      outline="#4F46E5", width=1, tags="deco")
        # Pequeño disco de acento
        c.create_oval(int(0.86 * w), int(0.72 * h), int(0.94 * w), int(0.80 * h),
                      fill="#22D3EE", outline="", tags="deco")


# --------------------------------------------------------------------- #
# Encabezado de marca
# --------------------------------------------------------------------- #
class AppHeader(ctk.CTkFrame):
    """Encabezado reutilizado en Dashboard y funciones (degradado + logo)."""

    def __init__(self, master, title_text, user, on_back=None, on_logout=None, on_home=None):
        super().__init__(master, fg_color=theme.BG, corner_radius=0, height=76)
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        GradientFrame(
            self,
            colors=[theme.BG, theme.PRIMARY_DARK, theme.VIOLET],
            vertical=False,
        ).grid(row=0, column=0, columnspan=3, sticky="nsew")

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, padx=18, pady=10, sticky="w")

        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                w, h = img.size
                new_h = 34
                new_w = int(w * (new_h / h))
                logo_card = ctk.CTkFrame(left, fg_color="#FFFFFF", corner_radius=8)
                logo_card.pack(side="left", padx=(0, 12))
                ctk_img = ctk.CTkImage(light_image=img, size=(new_w, new_h))
                ctk.CTkLabel(logo_card, image=ctk_img, text="").pack(padx=6, pady=3)
            except Exception:
                pass

        if on_home:
            home_btn = ctk.CTkButton(left, text="⌂", width=36, height=34, command=on_home)
            theme.style_ghost_button(home_btn)
            home_btn.pack(side="left", padx=(0, 8))

        if on_back:
            back_btn = ctk.CTkButton(left, text="←  Regresar", width=110, height=34,
                                     command=on_back)
            theme.style_ghost_button(back_btn)
            back_btn.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(self, text=title_text, font=theme.HEADER_TITLE_FONT,
                     text_color="#FFFFFF").grid(row=0, column=1, sticky="w")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, padx=18, pady=10, sticky="e")

        uname = user["username"] if user else ""
        chip = ctk.CTkFrame(right, fg_color=theme.SURFACE_2, corner_radius=16,
                            border_width=1, border_color=theme.BORDER_SOFT)
        chip.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(chip, text=f"👤  {uname}", font=theme.SMALL_FONT,
                     text_color=theme.TEXT).pack(padx=14, pady=6)

        if on_logout:
            logout_btn = ctk.CTkButton(right, text="Cerrar sesión", width=110, height=34,
                                       command=on_logout)
            theme.style_danger_button(logout_btn)
            logout_btn.configure(font=theme.SMALL_FONT, corner_radius=8, height=32)
            logout_btn.pack(side="left")


# --------------------------------------------------------------------- #
# Tarjeta de indicador (KPI)
# --------------------------------------------------------------------- #
class StatCard(ctk.CTkFrame):
    """Tarjeta de métrica: icono con acento, etiqueta, valor y subtítulo."""

    def __init__(self, master, label, value, icon="📊", accent=theme.PRIMARY, sub=None):
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=16,
                         border_width=1, border_color=theme.BORDER_SOFT)
        self.grid_columnconfigure(1, weight=1)

        chip = ctk.CTkFrame(self, fg_color=accent, corner_radius=12, width=44, height=44)
        chip.grid_propagate(False)
        chip.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=(16, 14), sticky="w")
        ctk.CTkLabel(chip, text=icon, font=(theme.FONT_FAMILY, 20)).pack(expand=True)

        ctk.CTkLabel(self, text=label, font=theme.KPI_CAPTION_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=0, column=1, padx=(0, 16), pady=(16, 2),
                                                        sticky="w")
        self.value_label = ctk.CTkLabel(self, text=str(value), font=theme.KPI_FONT,
                                        text_color=theme.TEXT)
        self.value_label.grid(row=1, column=1, padx=(0, 16), pady=(0, 2), sticky="w")

        if sub:
            ctk.CTkLabel(self, text=sub, font=theme.SMALL_FONT,
                         text_color=theme.TEXT_FAINT).grid(row=2, column=1, padx=(0, 16),
                                                            pady=(0, 16), sticky="w")

        bar = ctk.CTkFrame(self, height=3, fg_color=accent, corner_radius=2)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew")

    def set_value(self, value):
        self.value_label.configure(text=str(value))


# --------------------------------------------------------------------- #
# Ayudantes de formularios
# --------------------------------------------------------------------- #
def make_numeric_entry(master, **kwargs) -> ctk.CTkEntry:
    """CTkEntry que solo acepta dígitos (bloquea cualquier otro carácter)."""
    entry = ctk.CTkEntry(master, **kwargs)
    theme.style_entry(entry)

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
        theme.style_option_menu(self)
        self.set(BLANK_OPTION)

    def has_valid_selection(self) -> bool:
        return self.get() in self._real_values

    def refresh_values(self, values):
        self._real_values = list(values)
        self.configure(values=[BLANK_OPTION] + self._real_values)
        self.set(BLANK_OPTION)


def section_card(master, **kwargs):
    """Tarjeta estándar (superficie oscura redondeada con borde sutil)."""
    kwargs.setdefault("fg_color", theme.SURFACE)
    kwargs.setdefault("corner_radius", 16)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", theme.BORDER_SOFT)
    return ctk.CTkFrame(master, **kwargs)


def show_toast_label(label: ctk.CTkLabel, text, ok=True):
    label.configure(text=text, text_color=(theme.SUCCESS if ok else theme.ERROR))