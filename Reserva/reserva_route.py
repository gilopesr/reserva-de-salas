from flask import Blueprint, request, jsonify
from reserva_model import Reserva, ReservaNaoEncontrada
from database import db
import requests


routes = Blueprint("routes", __name__)


def validar_turma(turma_id):
    resp = requests.get(f"http://localhost:5002/api/turmas/{turma_id}")
    return resp.status_code == 200

@routes.route("/reservas", methods=["POST"])
def criar_reserva():
    dados = request.json
    turma_id = dados.get("turma_id")

    if not validar_turma(turma_id):
        return jsonify({"erro": "Turma não encontrada"}), 400

    reserva = Reserva(
        turma_id=turma_id,
        sala=dados.get("sala"),
        data=dados.get("data"),
        hora_inicio=dados.get("hora_inicio"),
        hora_fim=dados.get("hora_fim")
    )

    db.session.add(reserva)
    db.session.commit()

    return jsonify({"mensagem": "Reserva criada com sucesso"}), 201

@routes.route("/reservas", methods=["GET"])
def listar_reservas():
    reservas = Reserva.query.all()
    return jsonify([
        {
            "id": r.id,
            "turma_id": r.turma_id,
            "sala": r.sala,
            "data": r.data,
            "hora_inicio": r.hora_inicio,
            "hora_fim": r.hora_fim
        } for r in reservas
    ])

@routes.route("/reservas", methods=["DELETE"])
def delete_reservas():
    reservas = Reserva.query.get("id_reserva")
    if not reservas:
        raise ReservaNaoEncontrada
    db.session.delete(reservas)
    db.session.commit()
    return 'mensagem: Reserva deletada com sucesso', reservas