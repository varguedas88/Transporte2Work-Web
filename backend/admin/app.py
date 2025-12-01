from flask import Flask, request, jsonify, send_from_directory, session
import sqlite3
import os
from functools import wraps

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..', '..')
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'public')
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend', 'admin')
USER_PAGES_DIR = os.path.join(FRONTEND_DIR, 'usuario')

# base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

print(f"Carpeta frontend: {FRONTEND_DIR}")
print(f"Carpeta usuario: {USER_PAGES_DIR}")

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__, static_folder='.')
app.secret_key = "una_clave_super_secreta_y_larga_que_nadie_mas_sepa_123"

# proteger rutas de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged"):
            return jsonify({"error": "Acceso denegado. Debes iniciar sesión como admin."}), 403
        return f(*args, **kwargs)
    return decorated_function

# ========================
# APIs de USUARIOS (públicas)
# ========================

@app.route('/registro', methods=['POST'])
def registro():
    data = request.json
    required = ['identificacion', 'nombre', 'primer_apellido', 'correo', 'telefono', 'contrasena']
    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos obligatorios."}), 400

    db = get_db()
    try:
        db.execute(
            """INSERT INTO usuarios 
               (identificacion, nombre, primer_apellido, segundo_apellido, correo, telefono, contrasena) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data['identificacion'],
                data['nombre'],
                data['primer_apellido'],
                data.get('segundo_apellido', ''),
                data['correo'],
                data['telefono'],
                data['contrasena']
            )
        )
        db.commit()
        return jsonify({"status": "ok"})
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "identificacion" in msg:
            return jsonify({"error": "La identificación ya está registrada."}), 400
        if "correo" in msg:
            return jsonify({"error": "El correo ya está en uso."}), 400
        return jsonify({"error": "Error al registrar."}), 400
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def user_login():
    data = request.json
    identificacion = data.get('identificacion')
    contrasena = data.get('contrasena')

    if not identificacion or not contrasena:
        return jsonify({"error": "Faltan credenciales"}), 400

    db = get_db()
    cur = db.execute(
        "SELECT id, nombre, correo, rol FROM usuarios WHERE identificacion = ? AND contrasena = ?",
        (identificacion, contrasena)
    )
    user = cur.fetchone()
    db.close()

    if user:
        session['logged_in'] = True
        session['user_id'] = user['id']
        session['user_name'] = user['nombre']
        session['user_email'] = user['correo']
        session['user_role'] = user['rol']

        return jsonify({
            "id": user['id'],
            "nombre": user['nombre'],
            "identificacion": identificacion
        })
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

@app.route("/logout-publico", methods=["POST"])
def logout_publico():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    return jsonify({"status": "ok"})

@app.route('/api/mis-reservas', methods=['GET'])
def mis_reservas():
    # Obtener identificación desde el parámetro de URL
    identificacion = request.args.get('identificacion')
    
    if not identificacion:
        return jsonify({"error": "Falta la identificación"}), 400

    db = get_db()
    try:
        # Obtener el ID del usuario desde su identificación
        cur = db.execute("SELECT id FROM usuarios WHERE identificacion = ?", (identificacion,))
        user = cur.fetchone()
        if not user:
            return jsonify([]), 200  

        user_id = user['id']

        cur = db.execute("""
            SELECT r.id, r.fecha_inicio, r.fecha_fin, r.estado,
                   b.modelo, b.placa
            FROM reservas r
            JOIN buses b ON b.id = r.bus_id
            WHERE r.usuario_id = ?
            ORDER BY r.fecha_inicio DESC
        """, (user_id,))
        reservas = [dict(row) for row in cur.fetchall()]
        return jsonify(reservas)
    except Exception as e:
        print("Error al cargar reservas:", e)
        return jsonify([]), 200  
    finally:
        db.close()

@app.route('/api/reservas', methods=['POST'])
def crear_reserva_usuario():
    data = request.json
    identificacion = data.get('identificacion')
    bus_id = data.get('bus_id')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')

    if not all([identificacion, bus_id, fecha_inicio, fecha_fin]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    db = get_db()
    try:
        # Obtener el ID del usuario desde su identificación
        cur = db.execute("SELECT id FROM usuarios WHERE identificacion = ?", (identificacion,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario_id = user['id']

        # Crear la reserva
        cur = db.execute(
            "INSERT INTO reservas (usuario_id, bus_id, fecha_inicio, fecha_fin, estado) VALUES (?, ?, ?, ?, ?)",
            (usuario_id, bus_id, fecha_inicio, fecha_fin, "activa")
        )
        db.commit()
        return jsonify({"status": "ok", "id": cur.lastrowid}), 201
    except Exception as e:
        db.rollback()
        print("Error al crear reserva:", e)
        return jsonify({"error": "No se pudo crear la reserva"}), 500
    finally:
        db.close()


# ========================
# APIs de ADMIN
# ========================

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    correo = data.get("correo")
    contrasena = data.get("contrasena")

    if not correo or not contrasena:
        return jsonify({"error": "Faltan credenciales"}), 400

    db = get_db()
    cur = db.execute(
        "SELECT id, rol FROM usuarios WHERE correo = ? AND contrasena = ?",
        (correo, contrasena)
    )
    user = cur.fetchone()
    db.close()

    if not user:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if user["rol"] != "admin":
        return jsonify({"error": "No tienes permisos de administrador"}), 403

    session["admin_logged"] = True
    return jsonify({"status": "ok"})

@app.route("/admin/check")
def admin_check():
    return jsonify({"logged_in": bool(session.get("admin_logged"))})

@app.route("/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_logged", None)
    return jsonify({"status": "ok"})

# APIs CRUD protegidas
@app.route("/admin/usuarios", methods=["GET"])
@admin_required
def listar_usuarios():
    db = get_db()
    cur = db.execute("SELECT id, identificacion, nombre, primer_apellido, segundo_apellido, correo, telefono, rol FROM usuarios")
    rows = [dict(r) for r in cur.fetchall()]
    db.close()
    return jsonify(rows)

@app.route("/admin/usuarios", methods=["POST"])
@admin_required
def crear_usuario():
    data = request.json
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO usuarios (identificacion, nombre, primer_apellido, segundo_apellido, correo, telefono, rol, contrasena) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data['identificacion'],
                data['nombre'],
                data['primer_apellido'],
                data.get('segundo_apellido', ''),
                data['correo'],
                data['telefono'],
                data.get('rol', 'usuario'),
                data['contrasena']
            )
        )
        db.commit()
        return jsonify({"status": "ok", "id": cur.lastrowid}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/admin/usuarios/<int:id>", methods=["PUT"])
@admin_required
def editar_usuario(id):
    data = request.json
    db = get_db()
    try:
        db.execute(
            "UPDATE usuarios SET identificacion=?, nombre=?, primer_apellido=?, segundo_apellido=?, correo=?, telefono=?, rol=?, contrasena=? WHERE id=?",
            (
                data['identificacion'],
                data['nombre'],
                data['primer_apellido'],
                data.get('segundo_apellido', ''),
                data['correo'],
                data['telefono'],
                data['rol'],
                data['contrasena'],
                id
            )
        )
        db.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/admin/usuarios/<int:id>", methods=["DELETE"])
@admin_required
def eliminar_usuario(id):
    db = get_db()
    try:
        db.execute("DELETE FROM usuarios WHERE id=?", (id,))
        db.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# ========================
# Otras APIs (buses, choferes, reservas)
# ========================


@app.route("/admin/buses", methods=["GET"])
def listar_buses():
    try:
        db = get_db()
        cur = db.execute("SELECT id, placa, modelo, capacidad, costo_km FROM buses")
        rows = [dict(r) for r in cur.fetchall()]
        db.close()
        return jsonify(rows)
    except Exception as e:
        print("[ERROR listar_buses]", e)
        return jsonify({"error": "error listando buses"}), 500


@app.route("/admin/buses", methods=["POST"])
@admin_required
def crear_bus():
    try:
        data = request.get_json(force=True)
        db = get_db()
        cur = db.execute(
            "INSERT INTO buses (placa, modelo, capacidad, costo_km) VALUES (?, ?, ?, ?)",
            (data['placa'], data['modelo'], data['capacidad'], data.get('costo_km', 0))
        )
        db.commit()
        new_id = cur.lastrowid
        db.close()
        return jsonify({"status":"ok","id": new_id}), 201
    except Exception as e:
        db.rollback()
        print("[ERROR crear_bus]", e)
        return jsonify({"error": "no se pudo crear el bus", "detail": str(e)}), 500

@app.route("/admin/buses/<int:id>", methods=["PUT"])
@admin_required
def editar_bus(id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE buses SET placa=?, modelo=?, capacidad=?, costo_km=? WHERE id=?",
        (data['placa'], data['modelo'], data['capacidad'], data.get('costo_km', 0), id)
    )
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

@app.route("/admin/buses/<int:id>", methods=["DELETE"])
@admin_required
def eliminar_bus(id):
    db = get_db()
    db.execute("DELETE FROM buses WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

# APIs Choferes
@app.route("/admin/choferes", methods=["GET"])
@admin_required
def listar_choferes():
    try:
        db = get_db()
        cur = db.execute("SELECT id, nombre, telefono, cedula, licencia_tipo, fecha_contratacion FROM choferes")
        rows = [dict(r) for r in cur.fetchall()]
        db.close()
        return jsonify(rows)
    except Exception as e:
        print("[ERROR listar_choferes]", e)
        return jsonify({"error": "error listando choferes"}), 500

@app.route("/admin/choferes", methods=["POST"])
@admin_required
def crear_chofer():
    try:
        data = request.json
        db = get_db()
        cur = db.execute("""
            INSERT INTO choferes (nombre, telefono, cedula, licencia_tipo, fecha_contratacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get("nombre"),
            data.get("telefono"),
            data.get("cedula"),
            data.get("licencia_tipo"),
            data.get("fecha_contratacion")
        ))
        db.commit()
        new_id = cur.lastrowid
        db.close()
        return jsonify({"status":"ok","id": new_id}), 201
    except Exception as e:
        db.rollback()
        print("[ERROR crear_chofer]", e)
        return jsonify({"error": "no se pudo crear chofer", "detail": str(e)}), 500

@app.route("/admin/choferes/<int:id>", methods=["PUT"])
@admin_required
def editar_chofer(id):
    data = request.json
    db = get_db()
    db.execute("""
        UPDATE choferes SET nombre=?, telefono=?, cedula=?, licencia_tipo=?, fecha_contratacion=? WHERE id=?
    """, (
        data.get("nombre"),
        data.get("telefono"),
        data.get("cedula"),
        data.get("licencia_tipo"),
        data.get("fecha_contratacion"),
        id
    ))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

@app.route("/admin/choferes/<int:id>", methods=["DELETE"])
@admin_required
def eliminar_chofer(id):
    db = get_db()
    db.execute("DELETE FROM choferes WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

# APIs Reservas
@app.route("/admin/reservas", methods=["GET"])
@admin_required
def listar_reservas():
    try:
        db = get_db()
        cur = db.execute("""
            SELECT r.id, r.usuario_id, r.bus_id, r.fecha_inicio, r.fecha_fin, r.estado,
                   u.nombre as usuario, b.placa as bus
            FROM reservas r
            LEFT JOIN usuarios u ON u.id = r.usuario_id
            LEFT JOIN buses b ON b.id = r.bus_id
        """)
        rows = [dict(r) for r in cur.fetchall()]
        db.close()
        return jsonify(rows)
    except Exception as e:
        print("[ERROR listar_reservas]", e)
        return jsonify({"error": "error listando reservas"}), 500

@app.route("/admin/reservas", methods=["POST"])
@admin_required
def crear_reserva():
    try:
        data = request.get_json(force=True)
        db = get_db()
        cur = db.execute(
            "INSERT INTO reservas (usuario_id, bus_id, fecha_inicio, fecha_fin, estado) VALUES (?, ?, ?, ?, ?)",
            (data.get("usuario_id"), data.get("bus_id"), data.get("fecha_inicio"), data.get("fecha_fin"), data.get("estado", "en curso"))
        )
        db.commit()
        new_id = cur.lastrowid
        db.close()
        return jsonify({"status":"ok","id": new_id}), 201
    except Exception as e:
        db.rollback()
        print("[ERROR crear_reserva]", e)
        return jsonify({"error": "no se pudo crear la reserva", "detail": str(e)}), 500

@app.route("/admin/reservas/<int:id>", methods=["PUT"])
@admin_required
def actualizar_reserva(id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE reservas SET fecha_inicio=?, fecha_fin=?, estado=? WHERE id=?",
        (data.get("fecha_inicio"), data.get("fecha_fin"), data.get("estado"), id)
    )
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

@app.route("/admin/reservas/<int:id>", methods=["DELETE"])
@admin_required
def eliminar_reserva_api(id):
    db = get_db()
    db.execute("DELETE FROM reservas WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})


# Email 

try:
    from backend.admin.send_email_service import send_contact_email
    @app.route('/api/send-email', methods=['POST'])
    def handle_contact_form():
        data = request.get_json()
        if not data:
            return jsonify({"message": "Faltan datos del formulario."}), 400
        required_fields = ['name', 'email', 'subject', 'message', 'rating']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Faltan campos requeridos."}), 400
        if send_contact_email(data):
            return jsonify({"message": "Mensaje enviado con éxito."}), 200
        else:
            return jsonify({"message": "Error al enviar correo."}), 500
except ImportError:
    print("⚠️ Módulo de email no disponible. Ruta /api/send-email desactivada.")
    
# SERVIR ARCHIVOS ESTÁTICOS

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/usuario/<path:filename>')
def serve_user_pages(filename):
    return send_from_directory(USER_PAGES_DIR, filename)

# Rutas de admin (HTML)
@app.route("/admin/dashboard.html")
def serve_dashboard():
    if not session.get("admin_logged"):
        return send_from_directory('.', 'admin-login.html')
    return send_from_directory('.', 'dashboard.html')

@app.route("/admin-login.html")
def serve_admin_login():
    return send_from_directory('.', 'admin-login.html')

@app.route('/admin/<path:filename>')
def serve_static_backend(filename):
    return send_from_directory(BACKEND_DIR, filename)

@app.route("/admin/usuarios.html")
def serve_usuarios_html():
    return send_from_directory('.', 'usuarios.html')

@app.route("/admin/buses.html")
def serve_buses_html():
    return send_from_directory('.', 'buses.html')

@app.route("/admin/choferes.html")
def serve_choferes_html():
    return send_from_directory('.', 'choferes.html')

@app.route("/admin/reservas.html")
def serve_reservas_html():
    return send_from_directory('.', 'reservas.html')

# ========================
# API para que el usuario edite SU propio perfil
# ========================

@app.route('/api/perfil', methods=['GET'])
def obtener_perfil():
    if not session.get('logged_in') or not session.get('user_id'):
        return jsonify({"error": "No autenticado"}), 401

    db = get_db()
    cur = db.execute("SELECT * FROM usuarios WHERE id = ?", (session['user_id'],))
    user = cur.fetchone()
    db.close()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user["id"],
        "identificacion": user["identificacion"],
        "nombre": user["nombre"],
        "primer_apellido": user["primer_apellido"],
        "segundo_apellido": user["segundo_apellido"],
        "correo": user["correo"],
        "telefono": user["telefono"]
    })

@app.route('/api/perfil', methods=['PUT'])
def actualizar_perfil():
    if not session.get('logged_in') or not session.get('user_id'):
        return jsonify({"error": "No autenticado"}), 401

    data = request.json
    required = ['identificacion', 'nombre', 'primer_apellido', 'correo', 'telefono']
    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    user_id = session['user_id']

    db = get_db()
    try:
        # Verificar que la identificación o correo no se dupliquen (excepto en el propio usuario)
        cur = db.execute(
            "SELECT id FROM usuarios WHERE (identificacion = ? OR correo = ?) AND id != ?",
            (data['identificacion'], data['correo'], user_id)
        )
        if cur.fetchone():
            return jsonify({"error": "La identificación o el correo ya están en uso."}), 400

        db.execute("""
            UPDATE usuarios
            SET identificacion = ?, nombre = ?, primer_apellido = ?, segundo_apellido = ?, 
                correo = ?, telefono = ?
            WHERE id = ?
        """, (
            data['identificacion'],
            data['nombre'],
            data['primer_apellido'],
            data.get('segundo_apellido', ''),
            data['correo'],
            data['telefono'],
            user_id
        ))
        db.commit()

        # Actualizar sesión
        session['user_name'] = data['nombre']

        return jsonify({"status": "ok"})
    except Exception as e:
        db.rollback()
        print("Error al actualizar perfil:", e)
        return jsonify({"error": "No se pudo actualizar el perfil"}), 500
    finally:
        db.close()

# INICIAR SERVIDOR
if __name__ == "__main__":
    print("Iniciando servidor Flask en http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)