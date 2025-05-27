import datetime
from flask import Blueprint, request, jsonify
from reserva_model import Reserva, ReservaNaoEncontrada
from database import db
import requests
import re
from sqlalchemy import and_, or_, not_


routes = Blueprint("routes", __name__)


def validar_turma(turma_id):
    resp = requests.get(f"http://localhost:5002/api/turmas/{turma_id}")
    return resp.status_code == 200

def validar_professor(id_professor):
    try:
        resp = requests.get(f"http://localhost:5002/api/professores/{id_professor}")
        if resp.status_code == 200:
            dados = resp.json()
            return dados.get("nome") #verifica o professor pelo id mas retorna o nome para colocar no banco de dados
    except requests.RequestException:
        pass
    return None


def validar_hora_formato(hora_str):
    return bool(re.match(r"^\d{2}:\d{2}$", hora_str))


@routes.route("/reservas", methods=["POST"])
def criar_reserva():
    dados = request.json
    turma_id = dados.get("turma_id")
    id_professor = dados.get("id_professor")

    if not turma_id:
        return jsonify({"erro": "ID da turma é obrigatório"}), 400
    if not id_professor:
        return jsonify({"erro": "ID do professor é obrigatório"}), 400
    if not dados.get("sala"):
        return jsonify({"erro": "Sala é obrigatória"}), 400
    if not dados.get("data"):
        return jsonify({"erro": "Data é obrigatória"}), 400
    if not dados.get("hora_inicio"):
        return jsonify({"erro": "Hora de início é obrigatória"}), 400
    if not dados.get("hora_fim"):
        return jsonify({"erro": "Hora de fim é obrigatória"}), 400

    if not validar_turma(turma_id):
        return jsonify({"erro": "Turma não encontrada ou serviço de turmas indisponível"}), 400
    
    nome_professor = validar_professor(id_professor)
    if not nome_professor:
        return jsonify({"erro": "Professor não encontrado ou serviço de professores indisponível"}), 400
    
    try:
        data_reserva = datetime.datetime.strptime(dados["data"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if not validar_hora_formato(dados["hora_inicio"]):
        return jsonify({"erro": "Formato de hora de início inválido. Use HH:MM"}), 400
    hora_inicio_reserva = datetime.datetime.strptime(dados["hora_inicio"], "%H:%M").time()
    
    if not validar_hora_formato(dados["hora_fim"]):
        return jsonify({"erro": "Formato de hora de fim inválido. Use HH:MM"}), 400
    hora_fim_reserva = datetime.datetime.strptime(dados["hora_fim"], "%H:%M").time()

    if hora_inicio_reserva >= hora_fim_reserva:
        return jsonify({"erro": "A hora de início deve ser anterior à hora de fim"}), 400

    conflito_existente = Reserva.query.filter(
        Reserva.sala == dados["sala"],
        Reserva.data == data_reserva,
        and_(
            Reserva.hora_inicio < hora_fim_reserva,
            Reserva.hora_fim > hora_inicio_reserva
        )
    ).first()

    if conflito_existente:
        return jsonify({"erro": "Conflito de horário: A sala já está reservada neste período."}), 409

    reserva = Reserva(
        turma_id = turma_id,
        professor = nome_professor,
        sala=dados["sala"],
        data=data_reserva,
        hora_inicio=hora_inicio_reserva,
        hora_fim=hora_fim_reserva
    )

    db.session.add(reserva)
    db.session.commit()

    return jsonify({"mensagem": "Reserva criada com sucesso", "id_reserva": reserva.id_reserva}), 201

@routes.route("/reservas", methods=["GET"])
def listar_reservas():
    reservas = Reserva.query.all()
    return jsonify([
        {
            "id_reserva": r.id_reserva,
            "turma_id": r.turma_id,
            "professor": r.professor,
            "sala": r.sala,
            "data": r.data.isoformat(),
            "hora_inicio": r.hora_inicio.isoformat(),
            "hora_fim": r.hora_fim.isoformat()
        } for r in reservas
    ])

@routes.route("/reservas/<int:id_reserva>", methods=["GET"])
def obter_reserva_por_id(id_reserva):
    reserva = Reserva.query.get(id_reserva)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    return jsonify({
        "id_reserva": reserva.id_reserva,
        "turma_id": reserva.turma_id,
        "professor": reserva.professor,
        "sala": reserva.sala,
        "data": str(reserva.data),
        "hora_inicio": str(reserva.hora_inicio), 
        "hora_fim": str(reserva.hora_fim)
    }), 200


@routes.route("/reservas/<int:id_reserva>", methods=["PUT"])
def atualizar_reserva(id_reserva):
    reserva = Reserva.query.get(id_reserva)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    dados = request.json

    nova_turma_id = dados.get("turma_id", reserva.turma_id)
    nova_id_professor = dados.get("id_professor")
    nova_sala = dados.get("sala", reserva.sala)
    
    try:
        nova_data = datetime.datetime.strptime(dados["data"], "%Y-%m-%d").date() \
                    if "data" in dados else reserva.data
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    nova_hora_inicio = reserva.hora_inicio
    if "hora_inicio" in dados:
        if not validar_hora_formato(dados["hora_inicio"]):
            return jsonify({"erro": "Formato de hora de início inválido. Use HH:MM"}), 400
        nova_hora_inicio = datetime.datetime.strptime(dados["hora_inicio"], "%H:%M").time()

    nova_hora_fim = reserva.hora_fim
    if "hora_fim" in dados:
        if not validar_hora_formato(dados["hora_fim"]):
            return jsonify({"erro": "Formato de hora de fim inválido. Use HH:MM"}), 400
        nova_hora_fim = datetime.datetime.strptime(dados["hora_fim"], "%H:%M").time()

    if "turma_id" in dados and not validar_turma(nova_turma_id):
        return jsonify({"erro": "Turma não encontrada ou serviço de turmas indisponível"}), 400

    if "id_professor" in dados:
        nome_professor = validar_professor(nova_id_professor)
        if not nome_professor:
            return jsonify({"erro": "Professor não encontrado ou serviço de professores indisponível"}), 400
        reserva.professor = nome_professor 
    
    if nova_hora_inicio >= nova_hora_fim:
        return jsonify({"erro": "A hora de início deve ser anterior à hora de fim"}), 400


    conflito_existente = Reserva.query.filter(
        Reserva.sala == nova_sala,
        Reserva.data == nova_data,
        and_(
            Reserva.hora_inicio < nova_hora_fim,
            Reserva.hora_fim > nova_hora_inicio
        ),
        not_(Reserva.id_reserva == id_reserva)
    ).first()

    if conflito_existente:
        return jsonify({"erro": "Conflito de horário: A sala já está reservada neste período por outra reserva."}), 409

    reserva.turma_id = nova_turma_id
    reserva.sala = nova_sala
    reserva.data = nova_data
    reserva.hora_inicio = nova_hora_inicio
    reserva.hora_fim = nova_hora_fim

    db.session.commit()
    return jsonify({"mensagem": "Reserva atualizada com sucesso"}), 200



@routes.route("/reservas/<int:id_reserva>", methods=["DELETE"])
def deletar_reserva(id_reserva):
    reserva = Reserva.query.get(id_reserva)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    db.session.delete(reserva)
    db.session.commit()
    return jsonify({"mensagem": "Reserva deletada com sucesso"}), 200