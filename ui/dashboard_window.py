"""
ui/dashboard_window.py
Dashboard principal: indicadores (KPI), gráficas con filtros y accesos a
las funciones del sistema. Look "modern fintech": tema oscuro, tarjetas
elevadas y gráficas limpias (donut, barras y área degradada).
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import matplotlib
matplotlib.rcParams["font.family"] = "Segoe UI"

import database as db
import theme
from ui.widgets import AppHeader, StatCard, section_card


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
        self.geometry("1240x800")
        self.minsize(1020, 660)
        self.configure(fg_color=theme.BG)
        self.protocol("WM_DELETE_WINDOW", self._logout)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        AppHeader(self, "Dashboard", user, on_logout=self._logout).grid(
            row=0, column=0, sticky="ew")

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        body.grid_columnconfigure(0, weight=1)

        self._build_stats(body)
        self._build_actions_row(body)
        self._build_filters(body)
        self._build_charts(body)

        self.refresh()

    # ------------------------------------------------------------------ #
    def _build_stats(self, parent):
        self.stats_row = ctk.CTkFrame(parent, fg_color="transparent")
        self.stats_row.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            self.stats_row.grid_columnconfigure(i, weight=1)

        self.stat_total = StatCard(self.stats_row, "Producción total", "0",
                                   icon="📦", accent=theme.VIOLET)
        self.stat_total.grid(row=0, column=0, padx=6, sticky="ew")

        self.stat_records = StatCard(self.stats_row, "Registros capturados", "0",
                                     icon="🗒️", accent=theme.CYAN)
        self.stat_records.grid(row=0, column=1, padx=6, sticky="ew")

        self.stat_employees = StatCard(self.stats_row, "Empleados activos", "0",
                                       icon="🧑‍🏭", accent=theme.EMERALD)
        self.stat_employees.grid(row=0, column=2, padx=6, sticky="ew")

        self.stat_materials = StatCard(self.stats_row, "Materiales", "0",
                                       icon="🏷️", accent=theme.AMBER)
        self.stat_materials.grid(row=0, column=3, padx=6, sticky="ew")

    # ------------------------------------------------------------------ #
    def _build_actions_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        buttons = [
            ("📋   Capturar Datos", self.on_open_capture),
            ("🧑‍🔧   Agregar Empleados", self.on_open_employees),
            ("📦   Agregar Materiales", self.on_open_materials),
            ("📑   Ver Registros", self.on_open_records),
        ]
        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(row, text=text, height=56, font=theme.BUTTON_FONT, command=cmd)
            theme.style_primary_button(btn)
            btn.configure(font=(theme.FONT_FAMILY, 13, "bold"))
            btn.grid(row=0, column=i, padx=8, sticky="ew")

        if self.user.get("is_admin"):
            admin_btn = ctk.CTkButton(parent, text="⚙   Administrar usuarios", height=36,
                                       width=210, command=self.on_open_users,
                                       font=theme.SMALL_FONT)
            theme.style_secondary_button(admin_btn)
            admin_btn.configure(font=theme.SMALL_FONT)
            admin_btn.grid(row=2, column=0, sticky="w", pady=(0, 20))

    # ------------------------------------------------------------------ #
    def _build_filters(self, parent):
        card = section_card(parent)
        card.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        for i in range(6):
            card.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(card, text="Filtros de gráficas", font=theme.SUBTITLE_FONT,
                     text_color="#FFFFFF").grid(row=0, column=0, columnspan=6,
                                                 padx=18, pady=(16, 10), sticky="w")

        ctk.CTkLabel(card, text="Desde (AAAA-MM-DD)", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=0, padx=10, sticky="w")
        self.desde_entry = ctk.CTkEntry(card, placeholder_text="2025-01-01")
        theme.style_entry(self.desde_entry)
        self.desde_entry.grid(row=2, column=0, padx=10, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(card, text="Hasta (AAAA-MM-DD)", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=1, padx=10, sticky="w")
        self.hasta_entry = ctk.CTkEntry(card, placeholder_text="2025-12-31")
        theme.style_entry(self.hasta_entry)
        self.hasta_entry.grid(row=2, column=1, padx=10, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(card, text="Turno", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=2, padx=10, sticky="w")
        self.turno_menu = ctk.CTkOptionMenu(card, values=["Todos", "A", "B", "C"])
        theme.style_option_menu(self.turno_menu)
        self.turno_menu.set("Todos")
        self.turno_menu.grid(row=2, column=2, padx=10, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(card, text="Material", font=theme.SMALL_FONT,
                     text_color=theme.TEXT_MUTED).grid(row=1, column=3, padx=10, sticky="w")
        materiales = ["Todos"] + db.list_material_names()
        self.material_menu = ctk.CTkOptionMenu(card, values=materiales or ["Todos"])
        theme.style_option_menu(self.material_menu)
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
        charts_row.grid(row=4, column=0, sticky="nsew")
        charts_row.grid_columnconfigure(0, weight=1)
        charts_row.grid_columnconfigure(1, weight=1)

        card1 = section_card(charts_row)
        card1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(card1, text="Producción por material", font=theme.SUBTITLE_FONT,
                     text_color="#FFFFFF").pack(padx=16, pady=(14, 4), anchor="w")
        self.fig1 = Figure(figsize=(5.2, 3.8), dpi=100, facecolor=theme.SURFACE)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=card1)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(4, 12))

        card2 = section_card(charts_row)
        card2.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(card2, text="Cantidad capturada por turno", font=theme.SUBTITLE_FONT,
                     text_color="#FFFFFF").pack(padx=16, pady=(14, 4), anchor="w")
        self.fig2 = Figure(figsize=(5.2, 3.8), dpi=100, facecolor=theme.SURFACE)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=card2)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(4, 12))

        card3 = section_card(parent)
        card3.grid(row=5, column=0, sticky="nsew", pady=(20, 0))
        ctk.CTkLabel(card3, text="Producción por día", font=theme.SUBTITLE_FONT,
                     text_color="#FFFFFF").pack(padx=16, pady=(14, 4), anchor="w")
        self.fig3 = Figure(figsize=(10.8, 3.2), dpi=100, facecolor=theme.SURFACE)
        self.ax3 = self.fig3.add_subplot(111)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=card3)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(4, 12))

    # ------------------------------------------------------------------ #
    def refresh(self):
        materiales = ["Todos"] + db.list_material_names()
        self.material_menu.configure(values=materiales or ["Todos"])

        desde = self.desde_entry.get().strip() or None
        hasta = self.hasta_entry.get().strip() or None
        turno = self.turno_menu.get()
        material = self.material_menu.get()

        data = db.list_report_entries(desde, hasta, turno, material)

        total = sum(r["cantidad"] for r in data)
        self.stat_total.set_value(theme.fmt_num(total))
        self.stat_records.set_value(theme.fmt_num(len(data)))
        self.stat_employees.set_value(theme.fmt_num(len(db.list_employees())))
        self.stat_materials.set_value(theme.fmt_num(len(db.list_materials())))

        self._draw_by_material(data)
        self._draw_by_turno(data)
        self._draw_by_day(data)

    # ------------------------------------------------------------------ #
    # Estilos comunes de axes
    # ------------------------------------------------------------------ #
    def _style_ax(self, ax, grid_x=False, grid_y=True):
        ax.set_facecolor(theme.SURFACE)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(colors=theme.TEXT_FAINT, labelsize=8, length=0)
        if grid_y:
            ax.grid(axis="y", color=theme.BORDER_SOFT, lw=0.6, alpha=0.7)
        if grid_x:
            ax.grid(axis="x", color=theme.BORDER_SOFT, lw=0.6, alpha=0.7)
        ax.set_axisbelow(True)

    def _empty_ax(self, ax):
        ax.clear()
        self._style_ax(ax)
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                color=theme.TEXT_FAINT, fontsize=12)

    # ------------------------------------------------------------------ #
    def _draw_by_material(self, data):
        totals = {}
        for row in data:
            totals[row["material"]] = totals.get(row["material"], 0) + row["cantidad"]

        self.ax1.clear()
        if not totals:
            self._empty_ax(self.ax1)
        else:
            items = sorted(totals.items(), key=lambda x: -x[1])
            labels = [i[0] for i in items]
            values = [i[1] for i in items]
            colors = [theme.CHART_COLORS[i % len(theme.CHART_COLORS)]
                      for i in range(len(items))]

            self._style_ax(self.ax1, grid_x=False, grid_y=False)
            patches = self.ax1.pie(
                values, labels=None, colors=colors, startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.42, edgecolor=theme.SURFACE, linewidth=2),
            )[0]
            self.ax1.text(0, 0, f"{theme.fmt_num(sum(values))}\nunidades",
                          ha="center", va="center", color=theme.TEXT,
                          fontsize=11, fontweight="bold")
            self.ax1.legend(
                patches, labels, loc="center left", bbox_to_anchor=(1.02, 0.5),
                fontsize=8, facecolor=theme.SURFACE, edgecolor=theme.BORDER_SOFT,
                labelcolor=theme.TEXT, frameon=True, handlelength=1.2, borderpad=0.8,
            )
            self.ax1.set(aspect="equal")

        self.fig1.tight_layout()
        self.canvas1.draw()

    def _draw_by_turno(self, data):
        totals = {"A": 0, "B": 0, "C": 0}
        for row in data:
            if row["turno"] in totals:
                totals[row["turno"]] += row["cantidad"]

        self.ax2.clear()
        if not any(totals.values()):
            self._empty_ax(self.ax2)
        else:
            cats = list(totals.keys())
            values = [totals[c] for c in cats]
            colors = [theme.TURNO_COLORS[c] for c in cats]
            y_pos = range(len(cats))[::-1]

            self._style_ax(self.ax2)
            self.ax2.barh(list(y_pos), values, color=colors, height=0.55, zorder=3)
            self.ax2.set_yticks(list(y_pos), cats, color=theme.TEXT, fontsize=10)
            self.ax2.set_xlim(0, max(values) * 1.15 if values else 1)
            for y, v in zip(y_pos, values):
                self.ax2.text(v + max(values) * 0.02, y, theme.fmt_num(v),
                              ha="left", va="center", color=theme.TEXT, fontsize=9)

        self.fig2.tight_layout()
        self.canvas2.draw()

    def _draw_by_day(self, data):
        totals = {}
        for row in data:
            day = row["fecha"][:10]
            totals[day] = totals.get(day, 0) + row["cantidad"]

        self.ax3.clear()
        if not totals:
            self._empty_ax(self.ax3)
        else:
            days = sorted(totals.keys())
            values = [totals[d] for d in days]

            self._style_ax(self.ax3)
            if len(days) >= 2:
                self.ax3.fill_between(days, values, color=theme.PRIMARY,
                                      alpha=0.22, zorder=1)
            self.ax3.plot(days, values, color=theme.CYAN, lw=2.6, alpha=0.35,
                          zorder=2, solid_capstyle="round")
            self.ax3.plot(days, values, color=theme.CYAN, lw=1.6, marker="o",
                          markersize=5, zorder=3, solid_capstyle="round")
            self.ax3.set_ylim(0, max(values) * 1.2)
            self.ax3.xaxis.set_major_locator(MaxNLocator(12))
            self.ax3.tick_params(axis="x", rotation=30, labelsize=8)
            self.ax3.tick_params(axis="y", labelsize=8)

        self.fig3.tight_layout()
        self.canvas3.draw()

    # ------------------------------------------------------------------ #
    def _logout(self):
        self.destroy()
        self.on_logout()