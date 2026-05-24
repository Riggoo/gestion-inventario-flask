import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# ==========================================
# GESTIÓN DE USUARIOS (AUTENTICACIÓN)
# ==========================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['username'].strip()
        contrasena = request.form['password']
        rol = request.form['rol']
        
        if not usuario or not contrasena:
            flash("Por favor, rellena todos los campos.")
            return redirect('/registro')
            
        contrasena_segura = generate_password_hash(contrasena)
        conexion = obtener_conexion()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    sql = "INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (usuario, contrasena_segura, rol))
                conexion.commit()
                return "¡Usuario registrado con éxito! <a href='/login'>Inicia sesión aquí</a>"
            except Exception as e:
                return f"Error al registrar: El usuario ya existe."
            finally:
                conexion.close()
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username'].strip()
        contrasena = request.form['password']
        
        conexion = obtener_conexion()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    sql = "SELECT id, nombre_usuario, contrasena_hash, rol FROM usuarios WHERE nombre_usuario = %s"
                    cursor.execute(sql, (usuario,))
                    resultado = cursor.fetchone()
                
                if resultado and check_password_hash(resultado['contrasena_hash'], contrasena):
                    session['usuario_id'] = resultado['id']
                    session['usuario'] = resultado['nombre_usuario']
                    session['rol'] = resultado['rol']
                    return redirect('/')
                else:
                    return "Usuario o contraseña incorrectos. <a href='/login'>Intentar de nuevo</a>"
            finally:
                conexion.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ==========================================
# CONTROL DE INVENTARIO (CRUD DE PRODUCTOS)
# ==========================================

@app.route('/')
def inicio():
    if 'usuario_id' not in session:
        return redirect('/login')
        
    conexion = obtener_conexion()
    productos = []
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # Usamos stock_actual para listar en la tabla principal
                cursor.execute("SELECT id, nombre, descripcion, precio, stock_actual FROM productos")
                productos = cursor.fetchall()
        finally:
            conexion.close()
            
    return render_template('index.html', productos=productos)


@app.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if 'usuario_id' not in session:
        return redirect('/login')
    if session.get('rol') != 'administrador':
        return "Acceso denegado.", 403

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        descripcion = request.form['descripcion'].strip()
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])

        conexion = obtener_conexion()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    # Insertamos usando el nombre de columna real 'stock_actual'
                    sql = "INSERT INTO productos (nombre, descripcion, precio, stock_actual) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (nombre, descripcion, precio, stock))
                conexion.commit()
                flash(f"Producto '{nombre}' agregado exitosamente.")
                return redirect('/')
            finally:
                conexion.close()

    return render_template('formulario_producto.html', producto=None)


@app.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'usuario_id' not in session:
        return redirect('/login')
    if session.get('rol') != 'administrador':
        return "Acceso denegado.", 403

    conexion = obtener_conexion()
    if not conexion:
        return "Error de base de datos."

    try:
        with conexion.cursor() as cursor:
            if request.method == 'POST':
                nombre = request.form['nombre'].strip()
                descripcion = request.form['descripcion'].strip()
                precio = float(request.form['precio'])
                stock = int(request.form['stock'])

                # Actualizamos usando 'stock_actual'
                sql = "UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock_actual=%s WHERE id=%s"
                cursor.execute(sql, (nombre, descripcion, precio, stock, id))
                conexion.commit()
                flash("Producto actualizado correctamente.")
                return redirect('/')
            else:
                cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
                producto = cursor.fetchone()
    finally:
        conexion.close()

    return render_template('formulario_producto.html', producto=producto)


@app.route('/producto/eliminar/<int:id>')
def eliminar_producto(id):
    if 'usuario_id' not in session:
        return redirect('/login')
    if session.get('rol') != 'administrador':
        return "Acceso denegado.", 403

    conexion = obtener_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
            conexion.commit()
            flash("Producto eliminado del inventario.")
        finally:
            conexion.close()
            
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=8080)