# Sistema de Alquiler de Vehículos - Grupo 79 4K2

Sistema de gestión de alquiler de vehículos desarrollado con Python, Tkinter y SQLite.

## Características

- **ABM Clientes**: Alta, baja y modificación de clientes
- **ABM Vehículos**: Gestión del inventario de vehículos
- **ABM Empleados**: Administración de empleados
- **Registro de Alquileres**: Gestión de alquileres con validación de disponibilidad
- **Registro de Mantenimientos**: Control de mantenimientos de vehículos
- **Registro de Multas/Daños**: Registro de incidencias por alquiler
- **Reportes**: 
  - Listado de alquileres por cliente
  - Vehículos más alquilados
  - Facturación mensual (gráfico)
  - Exportación a CSV

## Requisitos

- Python 3.7 o superior
- Flask 2.3+ (para versión web)
- tkinter (incluido en Python estándar, para versión desktop)
- matplotlib (opcional, para gráficos en versión desktop)

## Instalación

1. Clonar o descargar el repositorio
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

O solo instalar matplotlib (las demás librerías vienen con Python):

```bash
pip install matplotlib
```

## Uso

Este proyecto tiene **DOS VERSIONES** de la aplicación:

### 1. Aplicación Desktop (Tkinter)

Para ejecutar la aplicación de escritorio:

```bash
python main.py
```

O hacer doble clic en `start.bat`

### 2. Aplicación Web (Flask)

Para ejecutar la aplicación web:

```bash
python web_app.py
```

O hacer doble clic en `start_web.bat`

La aplicación web estará disponible en: **http://localhost:8080**

## Estructura del Proyecto

```
DAO_Grupo_79_4K2/
├── config.py                    # Configuración y constantes
├── database.py                  # Funciones de base de datos
├── models.py                    # Lógica de negocio
├── main.py                      # Punto de entrada - App Desktop
├── web_app.py                   # Aplicación web Flask
├── requirements.txt             # Dependencias
├── README.md                    # Este archivo
├── start.bat                    # Inicio rápido Desktop
├── start_web.bat                # Inicio rápido Web
├── alquiler_vehiculos.db        # Base de datos SQLite
├── templates/                   # Templates HTML (versión web)
│   ├── base.html
│   ├── index.html
│   ├── clientes.html
│   ├── cliente_form.html
│   ├── vehiculos.html
│   ├── vehiculo_form.html
│   ├── empleados.html
│   ├── empleado_form.html
│   ├── alquileres.html
│   ├── alquiler_form.html
│   ├── alquiler_detalle.html
│   ├── multa_form.html
│   └── reportes.html
└── ui/                          # Interfaz Desktop (Tkinter)
    ├── __init__.py
    ├── main_window.py          # Ventana principal
    ├── clients_tab.py          # Pestaña de clientes
    ├── vehicles_tab.py         # Pestaña de vehículos
    ├── employees_tab.py        # Pestaña de empleados
    ├── rentals_tab.py          # Pestaña de alquileres
    └── reports_tab.py          # Pestaña de reportes
```

## Base de Datos

La base de datos se crea automáticamente en `alquiler_vehiculos.db` al ejecutar la aplicación por primera vez. Incluye datos de ejemplo para pruebas.

## Funcionalidades Detalladas

### Clientes
- Registrar nuevos clientes con datos completos
- Editar información de clientes existentes
- Eliminar clientes (con validación de integridad)
- Ver listado completo

### Vehículos
- Registrar vehículos con patente, marca, modelo, tipo, costo diario
- Actualizar estado de vehículos
- Registrar fecha de último mantenimiento
- Eliminar vehículos

### Empleados
- Registrar empleados con cargo
- Editar información
- Eliminar empleados

### Alquileres
- Crear nuevo alquiler con validación de disponibilidad
- Ver detalles completos del alquiler
- Registrar multas/damages asociados a un alquiler
- Calcular automáticamente el costo total basado en días

### Mantenimientos
- Registrar mantenimientos preventivos o correctivos
- Asociar mantenimientos a vehículos específicos
- Registrar costos y observaciones

### Reportes
- Listar todos los alquileres o por cliente específico
- Identificar vehículos más alquilados
- Ver gráfico de facturación mensual
- Exportar listado de alquileres a CSV

## Licencia

Este proyecto es parte del trabajo práctico del curso DAO - Grupo 79 4K2.

