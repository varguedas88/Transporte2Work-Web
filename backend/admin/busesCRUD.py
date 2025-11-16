from flask import Blueprint, request, jsonify
import sqlite3

buses_bp = Blueprint('buses', __name__)

def get_db():
    return sqlite3.connect("database.db")

@buses_bp.route('/buses', methods=['GET'])
def listar_buses():
    db = get_db()
    cursor = db.execute("SELECT * FROM buses")
    buses = cursor.fetchall()
    return jsonify(buses)

@buses_bp.route('/buses', methods=['POST'])
def crear_bus():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO buses (placa, modelo, capacidad) VALUES (?, ?, ?)",
        (data['placa'], data['modelo'], data['capacidad'])
    )
    db.commit()
    return jsonify({"status": "ok"})

@buses_bp.route('/buses/<int:id>', methods=['PUT'])
def editar_bus(id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE buses SET placa=?, modelo=?, capacidad=? WHERE id=?",
        (data['placa'], data['modelo'], data['capacidad'], id)
    )
    db.commit()
    return jsonify({"status": "ok"})

@buses_bp.route('/buses/<int:id>', methods=['DELETE'])
def eliminar_bus(id):
    db = get_db()
    db.execute("DELETE FROM buses WHERE id=?", (id,))
    db.commit()
    return jsonify({"status": "ok"})
