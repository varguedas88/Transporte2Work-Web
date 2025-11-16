from flask import Blueprint, request, jsonify
import sqlite3

usuarios_bp = Blueprint('usuarios', __name__)

def get_db():
    return sqlite3.connect("database.db")

@usuarios_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    db = get_db()
    cursor = db.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    return jsonify(usuarios)

@usuarios_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO usuarios (nombre, correo, rol, contrasena) VALUES (?, ?, ?, ?)",
        (data['nombre'], data['correo'], data['rol'], data['contrasena'])
    )
    db.commit()
    return jsonify({"status": "ok"})

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
def editar_usuario(id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE usuarios SET nombre=?, correo=?, rol=?, contrasena=? WHERE id=?",
        (data['nombre'], data['correo'], data['rol'], data['contrasena'], id)
    )
    db.commit()
    return jsonify({"status": "ok"})

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE id=?", (id,))
    db.commit()
    return jsonify({"status": "ok"})
