"""
main.py
Punto de entrada de la aplicación de escritorio Encore Group.

Ejecutar con:
    python main.py

La primera vez se crea automáticamente la base de datos SQLite
(encore_app.db) y un usuario administrador:
    usuario:    admin
    contraseña: admin123
(Cámbialo o crea nuevos usuarios desde el Dashboard -> Administrar usuarios).

Arquitectura: una sola ventana raíz de Tk (oculta) mantiene vivo el
mainloop durante toda la vida de la app; Login, Dashboard y cada función
son ventanas CTkToplevel que se abren/cierran sobre esa raíz.
"""

import customtkinter as ctk

import database as db
import theme
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow
from ui.capture_window import CaptureWindow
from ui.employees_window import EmployeesWindow
from ui.materials_window import MaterialsWindow
from ui.records_window import RecordsWindow
from ui.users_window import UsersWindow


class App:
    """Controlador principal: administra qué ventana está activa."""

    def __init__(self):
        theme.apply_global_theme()
        db.init_db()

        self.current_user = None
        self.dashboard = None

        self.root = ctk.CTk()
        self.root.withdraw()  # la raíz nunca se muestra directamente
        self.root.title("Encore Group")

        self.show_login()
        self.root.mainloop()

    # ------------------------------------------------------------------ #
    def show_login(self):
        self.current_user = None
        if self.dashboard is not None:
            try:
                self.dashboard.destroy()
            except Exception:
                pass
            self.dashboard = None

        LoginWindow(self.root, on_login_success=self.show_dashboard)

    def show_dashboard(self, user):
        self.current_user = user
        self.dashboard = DashboardWindow(
            self.root, user,
            on_logout=self.show_login,
            on_open_capture=self.open_capture,
            on_open_employees=self.open_employees,
            on_open_materials=self.open_materials,
            on_open_records=self.open_records,
            on_open_users=self.open_users,
        )

    # ------------------------------------------------------------------ #
    def _hide_dashboard(self):
        if self.dashboard is not None:
            self.dashboard.withdraw()

    def _return_to_dashboard(self):
        if self.dashboard is not None:
            self.dashboard.deiconify()
            self.dashboard.refresh()

    def open_capture(self):
        self._hide_dashboard()
        CaptureWindow(self.root, self.current_user,
                      on_back=self._return_to_dashboard, on_logout=self.show_login)

    def open_employees(self):
        self._hide_dashboard()
        EmployeesWindow(self.root, self.current_user,
                        on_back=self._return_to_dashboard, on_logout=self.show_login)

    def open_materials(self):
        self._hide_dashboard()
        MaterialsWindow(self.root, self.current_user,
                        on_back=self._return_to_dashboard, on_logout=self.show_login)

    def open_records(self):
        self._hide_dashboard()
        RecordsWindow(self.root, self.current_user,
                      on_back=self._return_to_dashboard, on_logout=self.show_login)

    def open_users(self):
        self._hide_dashboard()
        UsersWindow(self.root, self.current_user,
                    on_back=self._return_to_dashboard, on_logout=self.show_login)


if __name__ == "__main__":
    App()
