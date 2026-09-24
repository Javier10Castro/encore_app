"""
database.py
Capa de acceso a datos. Usa SQLite (incluido en Python, sin dependencias
externas) y guarda el archivo encore_app.db junto al ejecutable/proyecto.

Tablas:
    usuarios   -> login de la aplicación
    empleados  -> # Empleado, Nombre, Turno (A/B/C)
    materiales -> Nombre (único)
    reporte    -> # Empleado, Nombre, Turno, Material, Cantidad, Fecha
"""

import sqlite3
import hashlib
import os
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "encore_app.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def init_db():
    """Crea las tablas si no existen y siembra el usuario admin por defecto."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            numero_empleado INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            turno TEXT NOT NULL CHECK (turno IN ('A', 'B', 'C'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE COLLATE NOCASE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reporte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_empleado INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            turno TEXT NOT NULL CHECK (turno IN ('A', 'B', 'C')),
            material TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha DATETIME NOT NULL,
            FOREIGN KEY (numero_empleado) REFERENCES empleados (numero_empleado)
        )
    """)

    conn.commit()

    # Sembrar usuario admin por defecto si no existe ningún usuario todavía
    cur.execute("SELECT COUNT(*) AS c FROM usuarios")
    if cur.fetchone()["c"] == 0:
        salt = secrets.token_hex(8)
        cur.execute(
            "INSERT INTO usuarios (username, salt, password_hash, is_admin) VALUES (?, ?, ?, 1)",
            ("admin", salt, _hash_password("admin123", salt)),
        )
        conn.commit()

    conn.close()


# --------------------------------------------------------------------- #
# Usuarios / Login
# --------------------------------------------------------------------- #
def verify_login(username: str, password: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    if _hash_password(password, row["salt"]) == row["password_hash"]:
        return dict(row)
    return None


def username_exists(username: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM usuarios WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row is not None


def create_user(username: str, password: str, is_admin: bool = False):
    salt = secrets.token_hex(8)
    conn = get_connection()
    conn.execute(
        "INSERT INTO usuarios (username, salt, password_hash, is_admin) VALUES (?, ?, ?, ?)",
        (username, salt, _hash_password(password, salt), 1 if is_admin else 0),
    )
    conn.commit()
    conn.close()


def list_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, is_admin, creado_en FROM usuarios ORDER BY username"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --------------------------------------------------------------------- #
# Empleados
# --------------------------------------------------------------------- #
def employee_exists(numero_empleado: int) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM empleados WHERE numero_empleado = ?", (numero_empleado,)
    ).fetchone()
    conn.close()
    return row is not None


def get_employee(numero_empleado: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM empleados WHERE numero_empleado = ?", (numero_empleado,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_employee(numero_empleado: int, nombre: str, turno: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO empleados (numero_empleado, nombre, turno) VALUES (?, ?, ?)",
        (numero_empleado, nombre.strip(), turno),
    )
    conn.commit()
    conn.close()


def update_employee(numero_empleado: int, nombre: str, turno: str):
    conn = get_connection()
    conn.execute(
        "UPDATE empleados SET nombre = ?, turno = ? WHERE numero_empleado = ?",
        (nombre.strip(), turno, numero_empleado),
    )
    conn.commit()
    conn.close()


def delete_employee(numero_empleado: int):
    conn = get_connection()
    conn.execute("DELETE FROM empleados WHERE numero_empleado = ?", (numero_empleado,))
    conn.commit()
    conn.close()


def list_employees():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM empleados ORDER BY numero_empleado"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --------------------------------------------------------------------- #
# Materiales
# --------------------------------------------------------------------- #
def material_exists(nombre: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM materiales WHERE LOWER(nombre) = LOWER(?)", (nombre.strip(),)
    ).fetchone()
    conn.close()
    return row is not None


def add_material(nombre: str):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO materiales (nombre) VALUES (?)", (nombre.strip(),))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f'El material "{nombre}" ya existe.')
    finally:
        conn.close()


def update_material(material_id: int, nombre: str):
    conn = get_connection()
    conn.execute(
        "UPDATE materiales SET nombre = ? WHERE id = ?", (nombre.strip(), material_id)
    )
    conn.commit()
    conn.close()


def delete_material(material_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM materiales WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()


def list_materials():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM materiales ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_material_names():
    return [m["nombre"] for m in list_materials()]


# --------------------------------------------------------------------- #
# Reporte (captura de datos)
# --------------------------------------------------------------------- #
def add_report_entry(numero_empleado: int, nombre: str, turno: str, material: str, cantidad: int):
    conn = get_connection()
    conn.execute(
        """INSERT INTO reporte (numero_empleado, nombre, turno, material, cantidad, fecha)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (numero_empleado, nombre, turno, material, cantidad,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def list_report_entries(fecha_desde=None, fecha_hasta=None, turno=None, material=None):
    query = "SELECT * FROM reporte WHERE 1=1"
    params = []
    if fecha_desde:
        query += " AND date(fecha) >= date(?)"
        params.append(fecha_desde)
    if fecha_hasta:
        query += " AND date(fecha) <= date(?)"
        params.append(fecha_hasta)
    if turno and turno != "Todos":
        query += " AND turno = ?"
        params.append(turno)
    if material and material != "Todos":
        query += " AND material = ?"
        params.append(material)
    query += " ORDER BY fecha DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_report_entry(entry_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM reporte WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
