from database import db

class Reserva(db.Model):
    __tablename__ = 'reservas'

    id_reserva = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, nullable=False)
    professor = db.Column(db.String(50), nullable=False)
    sala = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

class ReservaNaoEncontrada(Exception):
    pass