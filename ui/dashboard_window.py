"""
ui/dashboard_window.py
Dashboard principal: gráficas (con filtros) sobre la tabla `reporte`,
más accesos a las tres funciones (Capturar Datos, Agregar Empleados,
Agregar Materiales) y a un listado general de registros.
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.rcParams["font.family"] = "sans-serif"

import database as db
import theme
from ui.widgets import AppHeader, section_card


class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, master, user, on_logout, on_open_capture, on_open_employees,
                 on_open_materials, on_open_records, on_open_users):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.on_open_capture = on_open_capture
        self.on_open_employees = on_open_employees
        self.on_open_materials = on_open_materials
        self.on_open_records = on_open_records
        self.on_open_users = on_open_users

        self.title("Encore Group - Dashboard")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(fg_color=theme.BG_LIGHT)
        self.protocol("WM_DELETE_WINDOW", self._logout)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Dashboard", user, on_logout=self._logout).grid(
            row=0, column=0, sticky="ew")

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        body.grid_columnconfigure(0, weight=1)

        self._build_actions_row(body)
        self._build_filters(body)
        self._build_charts(body)

        self.refresh()

    # ------------------------------------------------------------------ #
    def _build_actions_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        buttons = [
            ("📋  Capturar Datos", self.on_open_capture),
            ("🧑‍🔧  Agregar Empleados", self.on_open_employees),
            ("📦  Agregar Materiales", self.on_open_materials),
            ("📑  Ver Registros", self.on_open_records),
        ]
        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(row, text=text, height=64, font=theme.BUTTON_FONT, command=cmd)
            theme.style_primary_button(btn)
            btn.grid(row=0, column=i, padx=8, sticky="ew")

        if self.user.get("is_admin"):
            admin_btn = ctk.CTkButton(parent, text="⚙ Administrar usuarios", height=36,
                                       width=200, command=self.on_open_users,
                                       font=theme.SMALL_FONT)
            theme.style_secondary_button(admin_btn)
            admin_btn.grid(row=1, column=0, sticky="w", pady=(0, 20))

    # ------------------------------------------------------------------ #
    def _build_filters(self, parent):
        card = section_card(parent)
        card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        for i in range(6):
            card.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(card, text="Filtros de gráficas", font=theme.SUBTITLE_FONT,
                     text_color=theme.NAVY).grid(row=0, column=0, columnspan=6,
                                                  padx=18, pady=(16, 8), sticky="w")

        ctk.CTkLabel(card, text="Desde (AAAA-MM-DD)", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=1, column=0, padx=10, sticky="w")
        self.desde_entry = ctk.CTkEntry(card, placeholder_text="2025-01-01")
        self.desde_entry.grid(row=2, column=0, padx=10, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(card, text="Hasta (AAAA-MM-DD)", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=1, column=1, padx=10, sticky="w")
        self.hasta_entry = ctk.CTkEntry(card, placeholder_text="2025-12-31")
        self.hasta_entry.grid(row=2, column=1, padx=10, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(card, text="Turno", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=1, column=2, padx=10, sticky="w")
        self.turno_menu = ctk.CTkOptionMenu(card, values=["Todos", "A", "B", "C"])
        self.turno_menu.set("Todos")
        self.turno_menu.grid(row=2, column=2, padx=10, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(card, text="Material", font=theme.SMALL_FONT,
                     text_color=theme.GRAY).grid(row=1, column=3, padx=10, sticky="w")
        materiales = ["Todos"] + db.list_material_names()
        self.material_menu = ctk.CTkOptionMenu(card, values=materiales or ["Todos"])
        self.material_menu.set("Todos")
        self.material_menu.grid(row=2, column=3, padx=10, pady=(0, 16), sticky="ew")

        apply_btn = ctk.CTkButton(card, text="Aplicar filtros", command=self.refresh)
        theme.style_primary_button(apply_btn)
        apply_btn.grid(row=2, column=4, padx=10, pady=(0, 16), sticky="ew")

        clear_btn = ctk.CTkButton(card, text="Limpiar", command=self._clear_filters)
        theme.style_secondary_button(clear_btn)
        clear_btn.grid(row=2, column=5, padx=10, pady=(0, 16), sticky="ew")

    def _clear_filters(self):
        self.desde_entry.delete(0, "end")
        self.hasta_entry.delete(0, "end")
        self.turno_menu.set("Todos")
        self.material_menu.set("Todos")
        self.refresh()

    # ------------------------------------------------------------------ #
    def _build_charts(self, parent):
        charts_row = ctk.CTkFrame(parent, fg_color="transparent")
        charts_row.grid(row=3, column=0, sticky="nsew")
        charts_row.grid_columnconfigure(0, weight=1)
        charts_row.grid_columnconfigure(1, weight=1)

        card1 = section_card(charts_row)
        card1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(card1, text="Cantidad total por material", font=theme.SUBTITLE_FONT,
                     text_color=theme.NAVY).pack(padx=16, pady=(14, 4), anchor="w")
        self.fig1 = Figure(figsize=(5, 3.6), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=card1)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)

        card2 = section_card(charts_row)
        card2.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(card2, text="Cantidad capturada por turno", font=theme.SUBTITLE_FONT,
                     text_color=theme.NAVY).pack(padx=16, pady=(14, 4), anchor="w")
        self.fig2 = Figure(figsize=(5, 3.6), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=card2)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)

        card3 = section_card(parent)
        card3.grid(row=4, column=0, sticky="nsew", pady=(20, 0))
        ctk.CTkLabel(card3, text="Cantidad capturada por día", font=theme.SUBTITLE_FONT,
                     text_color=theme.NAVY).pack(padx=16, pady=(14, 4), anchor="w")
        self.fig3 = Figure(figsize=(10.5, 3.4), dpi=100)
        self.ax3 = self.fig3.add_subplot(111)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=card3)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)

    # ------------------------------------------------------------------ #
    def refresh(self):
        materiales = ["Todos"] + db.list_material_names()
        self.material_menu.configure(values=materiales or ["Todos"])

        desde = self.desde_entry.get().strip() or None
        hasta = self.hasta_entry.get().strip() or None
        turno = self.turno_menu.get()
        material = self.material_menu.get()

        data = db.list_report_entries(desde, hasta, turno, material)
        self._draw_by_material(data)
        self._draw_by_turno(data)
        self._draw_by_day(data)

    def _style_axes(self, ax):
        ax.set_facecolor(theme.WHITE)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.tick_params(colors=theme.GRAY, labelsize=8)

    def _draw_by_material(self, data):
        totals = {}
        for row in data:
            totals[row["material"]] = totals.get(row["material"], 0) + row["cantidad"]
        self.ax1.clear()
        self._style_axes(self.ax1)
        if totals:
            items = sorted(totals.items(), key=lambda x: -x[1])
            names = [i[0] for i in items]
            values = [i[1] for i in items]
            self.ax1.bar(names, values, color=theme.NAVY)
            self.ax1.tick_params(axis="x", rotation=30)
        else:
            self.ax1.text(0.5, 0.5, "Sin datos", ha="center", va="center", color=theme.GRAY)
        self.fig1.tight_layout()
        self.canvas1.draw()

    def _draw_by_turno(self, data):
        totals = {"A": 0, "B": 0, "C": 0}
        for row in data:
            if row["turno"] in totals:
                totals[row["turno"]] += row["cantidad"]
        self.ax2.clear()
        self._style_axes(self.ax2)
        colors = [theme.NAVY, theme.STEEL_BLUE, theme.GRAY]
        self.ax2.bar(list(totals.keys()), list(totals.values()), color=colors)
        self.fig2.tight_layout()
        self.canvas2.draw()

    def _draw_by_day(self, data):
        totals = {}
        for row in data:
            day = row["fecha"][:10]
            totals[day] = totals.get(day, 0) + row["cantidad"]
        self.ax3.clear()
        self._style_axes(self.ax3)
        if totals:
            days = sorted(totals.keys())
            values = [totals[d] for d in days]
            self.ax3.plot(days, values, color=theme.NAVY, marker="o")
            self.ax3.fill_between(days, values, color=theme.STEEL_BLUE, alpha=0.15)
            self.ax3.tick_params(axis="x", rotation=30)
        else:
            self.ax3.text(0.5, 0.5, "Sin datos", ha="center", va="center", color=theme.GRAY)
        self.fig3.tight_layout()
        self.canvas3.draw()

    # ------------------------------------------------------------------ #
    def _logout(self):
        self.destroy()
        self.on_logout()
