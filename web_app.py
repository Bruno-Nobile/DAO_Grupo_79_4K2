#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Alquiler de Vehículos - Aplicación Web Flask
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from database import init_db, seed_sample_data, get_connection
from models import registrar_alquiler, calcular_costo, vehiculo_disponible
from validations import (
    validar_dni, validar_telefono, validar_email, validar_patente,
    validar_fecha_mantenimiento, validar_fecha_inicio_alquiler
)
from services.reportes_service import ReportesService
import sqlite3
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = 'alquiler_vehiculos_secret_key_2024'


# ---------------------------
# Rutas principales
# ---------------------------

@app.route('/')
def index():
    """Página principal con resumen del sistema"""
    conn = get_connection()
    c = conn.cursor()
    
    # Obtener estadísticas
    c.execute("SELECT COUNT(*) FROM cliente")
    num_clientes = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM vehiculo")
    num_vehiculos = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM empleado")
    num_empleados = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM alquiler")
    num_alquileres = c.fetchone()[0]
    
    c.execute("SELECT SUM(costo_total) FROM alquiler")
    total_facturado = c.fetchone()[0] or 0
    
    conn.close()
    
    return render_template('index.html',
                         num_clientes=num_clientes,
                         num_vehiculos=num_vehiculos,
                         num_empleados=num_empleados,
                         num_alquileres=num_alquileres,
                         total_facturado=total_facturado)


# ---------------------------
# Rutas para Clientes
# ---------------------------

@app.route('/clientes')
def clientes():
    """Lista todos los clientes"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM cliente ORDER BY apellido, nombre")
    clientes = c.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        # Validaciones
        dni = request.form.get('dni', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        if dni and not validar_dni(dni):
            flash('El DNI debe tener exactamente 8 dígitos numéricos', 'error')
            return render_template('cliente_form.html', cliente=None, titulo="Nuevo Cliente")
        
        if telefono and not validar_telefono(telefono):
            flash('El teléfono debe contener solo dígitos numéricos', 'error')
            return render_template('cliente_form.html', cliente=None, titulo="Nuevo Cliente")
        
        if email and not validar_email(email):
            flash('El email debe tener el formato x@x.com', 'error')
            return render_template('cliente_form.html', cliente=None, titulo="Nuevo Cliente")
        
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) 
                        VALUES (?,?,?,?,?,?)""",
                     (request.form['nombre'], request.form['apellido'], dni,
                      telefono, request.form['direccion'], email))
            conn.commit()
            flash('Cliente creado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al crear cliente: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', cliente=None, titulo="Nuevo Cliente")


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    """Editar cliente existente"""
    conn = get_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        # Validaciones
        dni = request.form.get('dni', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        if dni and not validar_dni(dni):
            flash('El DNI debe tener exactamente 8 dígitos numéricos', 'error')
            c.execute("SELECT * FROM cliente WHERE id_cliente = ?", (id,))
            cliente = c.fetchone()
            conn.close()
            return render_template('cliente_form.html', cliente=cliente, titulo="Editar Cliente")
        
        if telefono and not validar_telefono(telefono):
            flash('El teléfono debe contener solo dígitos numéricos', 'error')
            c.execute("SELECT * FROM cliente WHERE id_cliente = ?", (id,))
            cliente = c.fetchone()
            conn.close()
            return render_template('cliente_form.html', cliente=cliente, titulo="Editar Cliente")
        
        if email and not validar_email(email):
            flash('El email debe tener el formato x@x.com', 'error')
            c.execute("SELECT * FROM cliente WHERE id_cliente = ?", (id,))
            cliente = c.fetchone()
            conn.close()
            return render_template('cliente_form.html', cliente=cliente, titulo="Editar Cliente")
        
        try:
            c.execute("""UPDATE cliente SET nombre=?, apellido=?, dni=?, telefono=?, direccion=?, email=? 
                        WHERE id_cliente=?""",
                     (request.form['nombre'], request.form['apellido'], dni,
                      telefono, request.form['direccion'], email, id))
            conn.commit()
            flash('Cliente actualizado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al actualizar cliente: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('clientes'))
    
    c.execute("SELECT * FROM cliente WHERE id_cliente = ?", (id,))
    cliente = c.fetchone()
    conn.close()
    
    if not cliente:
        flash('Cliente no encontrado', 'error')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=cliente, titulo="Editar Cliente")


@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    """Eliminar cliente"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM cliente WHERE id_cliente = ?", (id,))
        conn.commit()
        flash('Cliente eliminado exitosamente', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'No se puede eliminar el cliente: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('clientes'))


# ---------------------------
# Rutas para Vehículos
# ---------------------------

@app.route('/vehiculos')
def vehiculos():
    """Lista todos los vehículos"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vehiculo ORDER BY marca, modelo")
    vehiculos = c.fetchall()
    conn.close()
    return render_template('vehiculos.html', vehiculos=vehiculos)


@app.route('/vehiculos/nuevo', methods=['GET', 'POST'])
def nuevo_vehiculo():
    """Crear nuevo vehículo"""
    if request.method == 'POST':
        # Validaciones
        patente = request.form.get('patente', '').strip()
        fecha_mant = request.form.get('fecha_ultimo_mantenimiento', '').strip() or None
        
        if not validar_patente(patente):
            flash('La patente debe seguir el formato ABC-123 o AB-123-CD', 'error')
            return render_template('vehiculo_form.html', vehiculo=None, titulo="Nuevo Vehículo", fecha_actual=date.today().strftime('%Y-%m-%d'))
        
        if fecha_mant and not validar_fecha_mantenimiento(fecha_mant):
            flash('La fecha de último mantenimiento no puede ser mayor a la fecha actual', 'error')
            return render_template('vehiculo_form.html', vehiculo=None, titulo="Nuevo Vehículo", fecha_actual=date.today().strftime('%Y-%m-%d'))
        
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, estado, fecha_ultimo_mantenimiento) 
                        VALUES (?,?,?,?,?,?,?)""",
                     (patente.upper(), request.form['marca'], request.form['modelo'],
                      request.form['tipo'], float(request.form['costo_diario']), request.form['estado'], fecha_mant))
            conn.commit()
            flash('Vehículo creado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al crear vehículo: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('vehiculos'))
    return render_template('vehiculo_form.html', vehiculo=None, titulo="Nuevo Vehículo", fecha_actual=date.today().strftime('%Y-%m-%d'))


@app.route('/vehiculos/editar/<int:id>', methods=['GET', 'POST'])
def editar_vehiculo(id):
    """Editar vehículo existente"""
    conn = get_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        # Validaciones
        patente = request.form.get('patente', '').strip()
        fecha_mant = request.form.get('fecha_ultimo_mantenimiento', '').strip() or None
        
        if not validar_patente(patente):
            flash('La patente debe seguir el formato ABC-123 o AB-123-CD', 'error')
            c.execute("SELECT * FROM vehiculo WHERE id_vehiculo = ?", (id,))
            vehiculo = c.fetchone()
            conn.close()
            return render_template('vehiculo_form.html', vehiculo=vehiculo, titulo="Editar Vehículo", fecha_actual=date.today().strftime('%Y-%m-%d'))
        
        if fecha_mant and not validar_fecha_mantenimiento(fecha_mant):
            flash('La fecha de último mantenimiento no puede ser mayor a la fecha actual', 'error')
            c.execute("SELECT * FROM vehiculo WHERE id_vehiculo = ?", (id,))
            vehiculo = c.fetchone()
            conn.close()
            return render_template('vehiculo_form.html', vehiculo=vehiculo, titulo="Editar Vehículo", fecha_actual=date.today().strftime('%Y-%m-%d'))
        
        try:
            c.execute("""UPDATE vehiculo SET patente=?, marca=?, modelo=?, tipo=?, costo_diario=?, 
                        estado=?, fecha_ultimo_mantenimiento=? WHERE id_vehiculo=?""",
                     (patente.upper(), request.form['marca'], request.form['modelo'],
                      request.form['tipo'], float(request.form['costo_diario']), request.form['estado'],
                      fecha_mant, id))
            conn.commit()
            flash('Vehículo actualizado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al actualizar vehículo: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('vehiculos'))
    
    c.execute("SELECT * FROM vehiculo WHERE id_vehiculo = ?", (id,))
    vehiculo = c.fetchone()
    conn.close()
    
    if not vehiculo:
        flash('Vehículo no encontrado', 'error')
        return redirect(url_for('vehiculos'))
    
    return render_template('vehiculo_form.html', vehiculo=vehiculo, titulo="Editar Vehículo", fecha_actual=date.today().strftime('%Y-%m-%d'))


@app.route('/vehiculos/eliminar/<int:id>')
def eliminar_vehiculo(id):
    """Eliminar vehículo"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM vehiculo WHERE id_vehiculo = ?", (id,))
        conn.commit()
        flash('Vehículo eliminado exitosamente', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'No se puede eliminar el vehículo: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('vehiculos'))


# ---------------------------
# Rutas para Empleados
# ---------------------------

@app.route('/empleados')
def empleados():
    """Lista todos los empleados"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM empleado ORDER BY apellido, nombre")
    empleados = c.fetchall()
    conn.close()
    return render_template('empleados.html', empleados=empleados)


@app.route('/empleados/nuevo', methods=['GET', 'POST'])
def nuevo_empleado():
    """Crear nuevo empleado"""
    if request.method == 'POST':
        # Validaciones
        dni = request.form.get('dni', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        if dni and not validar_dni(dni):
            flash('El DNI debe tener exactamente 8 dígitos numéricos', 'error')
            return render_template('empleado_form.html', empleado=None, titulo="Nuevo Empleado")
        
        if telefono and not validar_telefono(telefono):
            flash('El teléfono debe contener solo dígitos numéricos', 'error')
            return render_template('empleado_form.html', empleado=None, titulo="Nuevo Empleado")
        
        if email and not validar_email(email):
            flash('El email debe tener el formato x@x.com', 'error')
            return render_template('empleado_form.html', empleado=None, titulo="Nuevo Empleado")
        
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) 
                        VALUES (?,?,?,?,?,?)""",
                     (request.form['nombre'], request.form['apellido'], dni,
                      request.form['cargo'], telefono, email))
            conn.commit()
            flash('Empleado creado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al crear empleado: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('empleados'))
    return render_template('empleado_form.html', empleado=None, titulo="Nuevo Empleado")


@app.route('/empleados/editar/<int:id>', methods=['GET', 'POST'])
def editar_empleado(id):
    """Editar empleado existente"""
    conn = get_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        # Validaciones
        dni = request.form.get('dni', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        if dni and not validar_dni(dni):
            flash('El DNI debe tener exactamente 8 dígitos numéricos', 'error')
            c.execute("SELECT * FROM empleado WHERE id_empleado = ?", (id,))
            empleado = c.fetchone()
            conn.close()
            return render_template('empleado_form.html', empleado=empleado, titulo="Editar Empleado")
        
        if telefono and not validar_telefono(telefono):
            flash('El teléfono debe contener solo dígitos numéricos', 'error')
            c.execute("SELECT * FROM empleado WHERE id_empleado = ?", (id,))
            empleado = c.fetchone()
            conn.close()
            return render_template('empleado_form.html', empleado=empleado, titulo="Editar Empleado")
        
        if email and not validar_email(email):
            flash('El email debe tener el formato x@x.com', 'error')
            c.execute("SELECT * FROM empleado WHERE id_empleado = ?", (id,))
            empleado = c.fetchone()
            conn.close()
            return render_template('empleado_form.html', empleado=empleado, titulo="Editar Empleado")
        
        try:
            c.execute("""UPDATE empleado SET nombre=?, apellido=?, dni=?, cargo=?, telefono=?, email=? 
                        WHERE id_empleado=?""",
                     (request.form['nombre'], request.form['apellido'], dni,
                      request.form['cargo'], telefono, email, id))
            conn.commit()
            flash('Empleado actualizado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al actualizar empleado: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('empleados'))
    
    c.execute("SELECT * FROM empleado WHERE id_empleado = ?", (id,))
    empleado = c.fetchone()
    conn.close()
    
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados'))
    
    return render_template('empleado_form.html', empleado=empleado, titulo="Editar Empleado")


@app.route('/empleados/eliminar/<int:id>')
def eliminar_empleado(id):
    """Eliminar empleado"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM empleado WHERE id_empleado = ?", (id,))
        conn.commit()
        flash('Empleado eliminado exitosamente', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'No se puede eliminar el empleado: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('empleados'))


# ---------------------------
# Rutas para Alquileres
# ---------------------------

@app.route('/alquileres')
def alquileres():
    """Lista todos los alquileres"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT a.id_alquiler, a.fecha_inicio, a.fecha_fin, a.costo_total,
                        c.apellido || ', ' || c.nombre AS cliente,
                        v.patente || ' - ' || v.marca || ' ' || v.modelo AS vehiculo,
                        e.apellido || ', ' || e.nombre AS empleado
                 FROM alquiler a
                 JOIN cliente c ON a.id_cliente = c.id_cliente
                 JOIN vehiculo v ON a.id_vehiculo = v.id_vehiculo
                 LEFT JOIN empleado e ON a.id_empleado = e.id_empleado
                 ORDER BY a.fecha_inicio DESC""")
    alquileres = c.fetchall()
    conn.close()
    return render_template('alquileres.html', alquileres=alquileres)


@app.route('/alquileres/nuevo', methods=['GET', 'POST'])
def nuevo_alquiler():
    """Crear nuevo alquiler"""
    if request.method == 'POST':
        # Validaciones
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        
        if not validar_fecha_inicio_alquiler(fecha_inicio):
            flash('La fecha de inicio debe ser mayor a la fecha actual', 'error')
            # Obtener listas para los selects
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id_cliente, nombre, apellido FROM cliente ORDER BY apellido, nombre")
            clientes = c.fetchall()
            
            c.execute("SELECT id_vehiculo, patente, marca, modelo FROM vehiculo ORDER BY patente")
            vehiculos = c.fetchall()
            
            c.execute("SELECT id_empleado, nombre, apellido FROM empleado ORDER BY apellido, nombre")
            empleados = c.fetchall()
            conn.close()
            return render_template('alquiler_form.html', clientes=clientes, vehiculos=vehiculos, 
                                 empleados=empleados, fecha_actual=date.today().strftime('%Y-%m-%d'))
        
        try:
            id_cliente = int(request.form['id_cliente'])
            id_vehiculo = int(request.form['id_vehiculo'])
            id_empleado = int(request.form['id_empleado']) if request.form['id_empleado'] else None
            
            registrar_alquiler(fecha_inicio, request.form['fecha_fin'],
                              id_cliente, id_vehiculo, id_empleado)
            flash('Alquiler registrado exitosamente', 'success')
        except ValueError as e:
            flash(f'Error: {e}', 'error')
        return redirect(url_for('alquileres'))
    
    # Obtener listas para los selects
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id_cliente, nombre, apellido FROM cliente ORDER BY apellido, nombre")
    clientes = c.fetchall()
    
    c.execute("SELECT id_vehiculo, patente, marca, modelo FROM vehiculo ORDER BY patente")
    vehiculos = c.fetchall()
    
    c.execute("SELECT id_empleado, nombre, apellido FROM empleado ORDER BY apellido, nombre")
    empleados = c.fetchall()
    conn.close()
    
    return render_template('alquiler_form.html', clientes=clientes, vehiculos=vehiculos, 
                         empleados=empleados, fecha_actual=date.today().strftime('%Y-%m-%d'))


@app.route('/alquileres/<int:id>')
def detalle_alquiler(id):
    """Ver detalles de un alquiler"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT a.*, c.nombre||' '||c.apellido as cliente, v.patente, v.marca, v.modelo, 
                        e.nombre||' '||e.apellido as empleado
                 FROM alquiler a
                 JOIN cliente c ON a.id_cliente=c.id_cliente
                 JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                 LEFT JOIN empleado e ON a.id_empleado=e.id_empleado
                 WHERE a.id_alquiler = ?""", (id,))
    alquiler = c.fetchone()
    
    c.execute("SELECT * FROM multa WHERE id_alquiler = ?", (id,))
    multas = c.fetchall()
    conn.close()
    
    return render_template('alquiler_detalle.html', alquiler=alquiler, multas=multas)


@app.route('/alquileres/<int:id>/multa', methods=['GET', 'POST'])
def registrar_multa(id):
    """Registrar multa a un alquiler"""
    if request.method == 'POST':
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO multa (descripcion, monto, id_alquiler) VALUES (?,?,?)",
                     (request.form['descripcion'], float(request.form['monto']), id))
            conn.commit()
            flash('Multa registrada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar multa: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('detalle_alquiler', id=id))
    return render_template('multa_form.html', id_alquiler=id)


# ---------------------------
# Rutas para Reportes
# ---------------------------

# Instancia del servicio de reportes
# Programación Orientada a Objetos - Instancia única del servicio
reportes_service = ReportesService()


@app.route('/reportes')
def reportes():
    """
    Página principal de reportes
    Programación Estructurada - Función bien organizada
    """
    return render_template('reportes.html')


@app.route('/api/reportes/alquileres-por-cliente')
def api_alquileres_por_cliente():
    """
    API: Listado de alquileres por cliente
    Programación Orientada a Objetos - Delegación al servicio
    """
    datos = reportes_service.alquileres_por_cliente()
    return jsonify(datos)


@app.route('/api/reportes/detalle-alquileres-cliente/<int:id_cliente>')
def api_detalle_alquileres_cliente(id_cliente):
    """
    API: Detalle de alquileres de un cliente específico
    Programación Orientada a Objetos - Delegación al servicio
    """
    datos = reportes_service.detalle_alquileres_por_cliente(id_cliente)
    return jsonify(datos)


@app.route('/api/reportes/vehiculos-mas-alquilados')
def api_vehiculos_mas_alquilados():
    """
    API: Vehículos más alquilados
    Programación Orientada a Objetos - Delegación al servicio
    """
    datos = reportes_service.vehiculos_mas_alquilados()
    return jsonify(datos)


@app.route('/api/reportes/alquileres-por-periodo/<periodo>')
def api_alquileres_por_periodo(periodo):
    """
    API: Alquileres por período (mes, trimestre, año)
    Programación Orientada a Objetos - Delegación al servicio
    """
    if periodo not in ['mes', 'trimestre', 'año']:
        return jsonify({'error': 'Período inválido'}), 400
    
    datos = reportes_service.alquileres_por_periodo(periodo)
    return jsonify(datos)


@app.route('/api/reportes/facturacion-mensual-grafico')
def api_facturacion_mensual_grafico():
    """
    API: Facturación mensual en gráfico de barras
    Programación Orientada a Objetos - Delegación al servicio
    """
    img_base64 = reportes_service.facturacion_mensual_grafico()
    if img_base64:
        return jsonify({'imagen': img_base64})
    else:
        return jsonify({'error': 'No se pudo generar el gráfico'}), 500


@app.route('/api/reportes/exportar-vehiculos-excel')
def api_exportar_vehiculos_excel():
    """
    API: Exportar vehículos más alquilados a Excel
    Programación Orientada a Objetos - Delegación al servicio
    Programación Estructurada - Función bien organizada
    """
    try:
        excel_buffer = reportes_service.exportar_vehiculos_mas_alquilados_excel()
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'vehiculos_mas_alquilados_{fecha}.xlsx'
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except ImportError as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('reportes'))
    except Exception as e:
        flash(f'Error al generar el archivo Excel: {str(e)}', 'error')
        return redirect(url_for('reportes'))


@app.route('/api/reportes/exportar-alquileres-csv')
def api_exportar_alquileres_csv():
    """
    API: Exportar lista de alquileres a CSV
    Programación Estructurada - Función bien organizada
    """
    import csv
    import io
    
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute("""SELECT a.id_alquiler, a.fecha_inicio, a.fecha_fin, a.costo_total,
                            c.nombre||' '||c.apellido as cliente, v.patente as vehiculo
                     FROM alquiler a
                     JOIN cliente c ON a.id_cliente=c.id_cliente
                     JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                     ORDER BY a.fecha_inicio DESC""")
        
        rows = c.fetchall()
        
        # Crear buffer en memoria para el CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Escribir encabezados
        writer.writerow(["id_alquiler", "fecha_inicio", "fecha_fin", "costo_total", "cliente", "vehiculo"])
        
        # Escribir datos
        for row in rows:
            writer.writerow([
                row["id_alquiler"],
                row["fecha_inicio"],
                row["fecha_fin"],
                row["costo_total"],
                row["cliente"],
                row["vehiculo"]
            ])
        
        # Convertir a bytes para la respuesta
        csv_bytes = io.BytesIO()
        csv_bytes.write(csv_buffer.getvalue().encode('utf-8-sig'))  # utf-8-sig para compatibilidad con Excel
        csv_bytes.seek(0)
        
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'alquileres_export_{fecha}.csv'
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error al generar el archivo CSV: {str(e)}', 'error')
        return redirect(url_for('reportes'))
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    seed_sample_data()
    app.run(host='0.0.0.0', port=8080, debug=True)

