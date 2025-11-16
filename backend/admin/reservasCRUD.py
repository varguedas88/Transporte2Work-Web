from flask import Blueprint, request, jsonify
import sqlite3

reservas_bp = Blueprint('reservas', __name__)

def get_db():
    return sqlite3.connect("database.db")

@reservas_bp.route('/reservas', methods=['GET'])
def listar_reservas():
    db = get_db()
    cursor = db.execute("""
        SELECT reservas.id, usuarios.nombre, buses.placa, reservas.fecha
        FROM reservas
        JOIN usuarios ON usuarios.id = reservas.usuario_id
        JOIN buses ON buses.id = reservas.bus_id
    """)
    reservas = cursor.fetchall()
    return jsonify(reservas)

@reservas_bp.route('/reservas', methods=['POST'])
def crear_reserva():
    data = request.json
    db = get_db()
    db.execute(
        "INSERT INTO reservas (usuario_id, bus_id, fecha) VALUES (?, ?, ?)",
        (data['usuario_id'], data['bus_id'], data['fecha'])
    )
    db.commit()
    return jsonify({"status": "ok"})

@reservas_bp.route('/reservas/<int:id>', methods=['DELETE'])
def eliminar_reserva(id):
    db = get_db()
    db.execute("DELETE FROM reservas WHERE id=?", (id,))
    db.commit()
    return jsonify({"status": "ok"})
