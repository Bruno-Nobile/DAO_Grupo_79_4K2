#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Alquiler de Vehículos - Aplicación Web Flask
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import init_db, seed_sample_data, get_connection
from models import registrar_alquiler, calcular_costo, vehiculo_disponible
import sqlite3
from datetime import datetime, date

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
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) 
                        VALUES (?,?,?,?,?,?)""",
                     (request.form['nombre'], request.form['apellido'], request.form['dni'],
                      request.form['telefono'], request.form['direccion'], request.form['email']))
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
        try:
            c.execute("""UPDATE cliente SET nombre=?, apellido=?, dni=?, telefono=?, direccion=?, email=? 
                        WHERE id_cliente=?""",
                     (request.form['nombre'], request.form['apellido'], request.form['dni'],
                      request.form['telefono'], request.form['direccion'], request.form['email'], id))
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
        conn = get_connection()
        c = conn.cursor()
        try:
            fecha_mant = request.form['fecha_ultimo_mantenimiento'] or None
            c.execute("""INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, estado, fecha_ultimo_mantenimiento) 
                        VALUES (?,?,?,?,?,?,?)""",
                     (request.form['patente'], request.form['marca'], request.form['modelo'],
                      request.form['tipo'], float(request.form['costo_diario']), request.form['estado'], fecha_mant))
            conn.commit()
            flash('Vehículo creado exitosamente', 'success')
        except sqlite3.IntegrityError as e:
            flash(f'Error al crear vehículo: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('vehiculos'))
    return render_template('vehiculo_form.html', vehiculo=None, titulo="Nuevo Vehículo")


@app.route('/vehiculos/editar/<int:id>', methods=['GET', 'POST'])
def editar_vehiculo(id):
    """Editar vehículo existente"""
    conn = get_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        try:
            fecha_mant = request.form['fecha_ultimo_mantenimiento'] or None
            c.execute("""UPDATE vehiculo SET patente=?, marca=?, modelo=?, tipo=?, costo_diario=?, 
                        estado=?, fecha_ultimo_mantenimiento=? WHERE id_vehiculo=?""",
                     (request.form['patente'], request.form['marca'], request.form['modelo'],
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
    
    return render_template('vehiculo_form.html', vehiculo=vehiculo, titulo="Editar Vehículo")


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
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) 
                        VALUES (?,?,?,?,?,?)""",
                     (request.form['nombre'], request.form['apellido'], request.form['dni'],
                      request.form['cargo'], request.form['telefono'], request.form['email']))
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
        try:
            c.execute("""UPDATE empleado SET nombre=?, apellido=?, dni=?, cargo=?, telefono=?, email=? 
                        WHERE id_empleado=?""",
                     (request.form['nombre'], request.form['apellido'], request.form['dni'],
                      request.form['cargo'], request.form['telefono'], request.form['email'], id))
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
        try:
            id_cliente = int(request.form['id_cliente'])
            id_vehiculo = int(request.form['id_vehiculo'])
            id_empleado = int(request.form['id_empleado']) if request.form['id_empleado'] else None
            
            registrar_alquiler(request.form['fecha_inicio'], request.form['fecha_fin'],
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
                         empleados=empleados)


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

@app.route('/reportes')
def reportes():
    """Página de reportes"""
    return render_template('reportes.html')


@app.route('/api/reportes/vehiculos-mas-alquilados')
def api_vehiculos_mas_alquilados():
    """API para obtener vehículos más alquilados"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT v.id_vehiculo, v.patente, v.marca||' '||v.modelo as desc, 
                        COUNT(a.id_alquiler) as veces
                 FROM vehiculo v
                 LEFT JOIN alquiler a ON v.id_vehiculo = a.id_vehiculo
                 GROUP BY v.id_vehiculo
                 ORDER BY veces DESC""")
    vehiculos = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in vehiculos])


if __name__ == '__main__':
    init_db()
    seed_sample_data()
    app.run(host='0.0.0.0', port=8080, debug=True)

