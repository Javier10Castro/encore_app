# Encore Group — App de Captura de Producción

Aplicación de escritorio en Python (customtkinter) para capturar producción
por empleado/turno/material, con dashboard de gráficas y administración
tipo CRUD de empleados y materiales.

## 1. Instalación (en PyCharm o terminal)

```bash
pip install -r requirements.txt
```

> `tkinter` ya viene incluido con Python en Windows/Mac. En Linux, si no lo
> tienes, instala `sudo apt install python3-tk`.

## 2. Ejecutar

```bash
python main.py
```

Al primer arranque se crea automáticamente el archivo `encore_app.db`
(SQLite, en la misma carpeta) y un usuario administrador:

```
usuario:    admin
contraseña: admin123
```

**Recomendación:** entra con ese usuario y crea tu propia cuenta de admin
desde Dashboard → "⚙ Administrar usuarios"; desde ahí también puedes crear
cuentas normales para otros usuarios (solo el admin ve ese botón).

## 3. Estructura del proyecto

```
encore_app/
├── main.py                 # Punto de entrada / controlador de navegación
├── database.py              # Toda la lógica de SQLite (usuarios, empleados,
│                             #   materiales, reporte)
├── theme.py                  # Colores/fuentes corporativos (logo Encore)
├── assets/
│   └── logo.png              # Logo mostrado en Login y encabezados
├── ui/
│   ├── widgets.py             # Header reutilizable, entry numérica, dropdown
│   │                           #   "bloqueado en blanco"
│   ├── login_window.py         # Pantalla de login
│   ├── dashboard_window.py      # Gráficas + filtros + accesos a funciones
│   ├── capture_window.py         # Función 1: Capturar Datos
│   ├── employees_window.py        # Función 2: Agregar/Ver/Editar Empleados
│   ├── materials_window.py         # Función 3: Agregar/Ver/Editar Materiales
│   ├── records_window.py            # Ver/filtrar/eliminar registros del reporte
│   └── users_window.py               # Crear usuarios (solo admin)
└── requirements.txt
```

## 4. Reglas de negocio implementadas

- **Capturar Datos**: pide # de empleado → botón "Validar". Si no existe,
  muestra alerta y permite reintentar. Si existe, se habilita el dropdown
  de material (inicia en blanco/null, no se puede guardar sin elegir un
  material real) y el campo de cantidad (solo acepta dígitos). El botón
  "Guardar" solo se habilita cuando todo es válido, y guarda con la
  fecha/hora actual.
- **Agregar Empleados**: pide # de empleado → "Validar" (debe **no** existir
  para continuar). Si ya existe, alerta y bloquea. Si no existe, habilita
  nombre + turno (dropdown A/B/C, también inicia en blanco). Incluye
  pestaña "Ver / Editar" con tabla, edición y eliminación.
- **Agregar Materiales**: formulario simple con "Validar existencia" (si ya
  existe, alerta) y "Agregar material" (solo se habilita tras validar que
  no existe). El nombre es único a nivel de base de datos (sin distinguir
  mayúsculas/minúsculas). Incluye pestaña "Ver / Editar".
- **Dashboard**: 3 gráficas (cantidad total por material, por turno, y por
  día) con filtros por rango de fechas, turno y material.

## 5. Personalización visual

Los colores están centralizados en `theme.py` (tomados del logo Encore / A
Boeing Company: azul marino, azul acero y gris corporativo). Puedes
ajustarlos ahí sin tocar el resto del código.

Las ventanas usan `grid`/`CTkScrollableFrame` para adaptarse al tamaño de
pantalla; todas tienen un tamaño mínimo (`minsize`) para mantener la
legibilidad.
