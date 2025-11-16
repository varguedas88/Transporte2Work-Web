from flask import Blueprint, request, jsonify
import sqlite3

choferes_bp = Blueprint('choferes_bp', __name__)

def get_db():
    return sqlite3.connect('database.db')

@choferes_bp.route('/choferes', methods=['GET'])
def get_choferes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, cedula, telefono FROM choferes")
    rows = cursor.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "nombre": r[1],
            "cedula": r[2],
            "telefono": r[3]
        })
    return jsonify(data)

@choferes_bp.route('/choferes', methods=['POST'])
def create_chofer():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO choferes(nombre, cedula, telefono) VALUES (?, ?, ?)",
        (data['nombre'], data['cedula'], data['telefono'])
    )
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "chofer agregado"}), 201

@choferes_bp.route('/choferes/<int:id>', methods=['PUT'])
def update_chofer(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE choferes SET nombre=?, cedula=?, telefono=? WHERE id=?",
        (data['nombre'], data['cedula'], data['telefono'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "chofer actualizado"})

@choferes_bp.route('/choferes/<int:id>', methods=['DELETE'])
def delete_chofer(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM choferes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "chofer eliminado"})

