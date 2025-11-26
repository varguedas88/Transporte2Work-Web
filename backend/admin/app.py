from flask import Flask, request, jsonify, send_from_directory, session
import sqlite3
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..', '..') 
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'public')
USER_PAGES_DIR = os.path.join(FRONTEND_DIR, 'usuario')

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

print(f"Carpeta frontend: {FRONTEND_DIR}")
print(f"Carpeta usuario: {USER_PAGES_DIR}")

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__, static_folder='.')
app.secret_key = "una_clave_super_secreta_y_larga_que_nadie_mas_sepa_123"

# APIs Usuarios
@app.route("/admin/usuarios", methods=["GET"])
def listar_usuarios():
    db = get_db()
    cur = db.execute("SELECT id, nombre, correo, rol FROM usuarios")
    rows = [dict(r) for r in cur.fetchall()]
    db.close()
    return jsonify(rows)

@app.route("/admin/usuarios", methods=["POST"])
def crear_usuario():
    data = request.json
    db = get_db()
    cur = db.execute(
        "INSERT INTO usuarios (nombre, correo, rol, contrasena) VALUES (?, ?, ?, ?)",
        (data.get("nombre"), data.get("correo"), data.get("rol", "usuario"), data.get("contrasena"))
    )
    db.commit()
    id = cur.lastrowid
    db.close()
    return jsonify({"status":"ok","id": id}), 201

@app.route("/admin/usuarios/<int:id>", methods=["PUT"])
def editar_usuario(id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE usuarios SET nombre=?, correo=?, rol=?, contrasena=? WHERE id=?",
        (data.get("nombre"), data.get("correo"), data.get("rol"), data.get("contrasena"), id)
    )
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

@app.route("/admin/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

# APIs Buses
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
def crear_bus():
    try:
        data = request.get_json(force=True)
        print("[POST /admin/buses] payload:", data)
        db = get_db()
        cur = db.execute(
    "INSERT INTO buses (placa, modelo, capacidad, costo_km) VALUES (?, ?, ?, ?)",
    (data['placa'], data['modelo'], data['capacidad'], data.get('costo_km', 0))
)
        db.commit()
        new_id = cur.lastrowid
        db.close()
        print(f"[CREAR BUS] insertado id={new_id}")
        return jsonify({"status":"ok","id": new_id}), 201
    except Exception as e:
        print("[ERROR crear_bus]", e)
        return jsonify({"error": "no se pudo crear el bus", "detail": str(e)}), 500


@app.route("/admin/buses/<int:id>", methods=["PUT"])
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
def eliminar_bus(id):
    db = get_db()
    db.execute("DELETE FROM buses WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

# APIs Choferes
@app.route("/admin/choferes", methods=["GET"])
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
        print("[ERROR crear_chofer]", e)
        return jsonify({"error": "no se pudo crear chofer", "detail": str(e)}), 500

@app.route("/admin/choferes/<int:id>", methods=["PUT"])
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
def eliminar_chofer(id):
    db = get_db()
    db.execute("DELETE FROM choferes WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})


# APIs Reservas
@app.route("/admin/reservas", methods=["GET"])
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
        print(f"[LISTAR RESERVAS] {len(rows)} filas encontradas")
        return jsonify(rows)
    except Exception as e:
        print("[ERROR listar_reservas]", e)
        return jsonify({"error": "error listando reservas"}), 500

@app.route("/admin/reservas", methods=["POST"])
def crear_reserva():
    try:
        data = request.get_json(force=True)
        print("[POST /admin/reservas] payload:", data)
        db = get_db()
        cur = db.execute(
            "INSERT INTO reservas (usuario_id, bus_id, fecha_inicio, fecha_fin, estado) VALUES (?, ?, ?, ?, ?)",
            (data.get("usuario_id"), data.get("bus_id"), data.get("fecha_inicio"), data.get("fecha_fin"), data.get("estado", "en curso"))
        )
        db.commit()
        new_id = cur.lastrowid
        db.close()
        print(f"[CREAR RESERVA] insertado id={new_id}")
        return jsonify({"status":"ok","id": new_id}), 201
    except Exception as e:
        print("[ERROR crear_reserva]", e)
        return jsonify({"error": "no se pudo crear la reserva", "detail": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    
    correo = data.get("correo")
    contrasena = data.get("contrasena")

    db = get_db()
    cur = db.execute(
        "SELECT id, rol FROM usuarios WHERE correo=? AND contrasena=?",
        (correo, contrasena)
    )
    user = cur.fetchone()
    db.close()

    if not user:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if user["rol"] != "admin":
        return jsonify({"error": "No eres admin"}), 403

    session["admin_logged"] = True
    return jsonify({"status": "ok"})

@app.route("/admin/check")
def admin_check():
    return jsonify({"ok": session.get("admin_logged", False)})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("admin_logged", None)
    return jsonify({"status": "ok"})


@app.route("/admin/reservas/<int:id>", methods=["PUT"])
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
def eliminar_reserva_api(id):
    db = get_db()
    db.execute("DELETE FROM reservas WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"status":"ok"})

# Registro público de usuarios
@app.route("/registro", methods=["POST"])
def registro_publico():
    data = request.json
    nombre = data.get("nombre")
    correo = data.get("correo")
    contrasena = data.get("contrasena")

    if not nombre or not correo or not contrasena:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    # Verificar si el correo ya existe
    db = get_db()
    cur = db.execute("SELECT id FROM usuarios WHERE correo = ?", (correo,))
    if cur.fetchone():
        db.close()
        return jsonify({"error": "El correo ya está registrado"}), 400

    # Crear usuario con rol "usuario" (no admin)
    cur = db.execute(
        "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (?, ?, ?, ?)",
        (nombre, correo, contrasena, "usuario")  
    )
    db.commit()
    db.close()

    return jsonify({"status": "ok", "mensaje": "Usuario registrado exitosamente"}), 201

# Login público para usuarios normales
@app.route("/login-publico", methods=["POST"])
def login_publico():
    data = request.json
    correo = data.get("correo")
    contrasena = data.get("contrasena")

    if not correo or not contrasena:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    db = get_db()
    cur = db.execute(
        "SELECT id, nombre, correo, rol FROM usuarios WHERE correo=? AND contrasena=?",
        (correo, contrasena)
    )
    user = cur.fetchone()
    db.close()

    if not user:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # Guardar sesión para usuario normal (diferente de admin)
    session['user_id'] = user['id']
    session['user_name'] = user['nombre']
    session['user_email'] = user['correo']
    session['user_role'] = user['rol']
    session['logged_in'] = True

    return jsonify({
        "status": "ok",
        "message": "Login exitoso",
        "user": {
            "id": user['id'],
            "nombre": user['nombre'],
            "correo": user['correo'],
            "rol": user['rol']
        }
    })

# Verificar sesión de usuario normal
@app.route("/check-user")
def check_user_session():
    if session.get('logged_in'):
        return jsonify({
            "logged_in": True,
            "user": {
                "id": session.get('user_id'),
                "nombre": session.get('user_name'),
                "correo": session.get('user_email'),
                "rol": session.get('user_role')
            }
        })
    return jsonify({"logged_in": False})

# Logout de usuario normal
@app.route("/logout-publico", methods=["POST"])
def logout_publico():
    # Limpiar solo la sesión de usuario (no la de admin)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    session.pop('logged_in', None)
    return jsonify({"status": "ok"})

# Servir archivos del frontend
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/usuario/<path:filename>')
def serve_user_pages(filename):
    return send_from_directory(USER_PAGES_DIR, filename)

# Servir HTML estático
@app.route("/admin/dashboard.html")
def serve_dashboard():
    if not session.get("admin_logged"):
        return send_from_directory('.', 'login.html')
    return send_from_directory('.', 'dashboard.html')


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

if __name__ == "__main__":
    print("Iniciando servidor Flask en http://localhost:5000/")
    app.run(debug=True)

