from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Categoria(db.Model):
    __tablename__ = 'categoria'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita', 'despesa', 'ambos'
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'

class Transacao(db.Model):
    __tablename__ = 'transacao'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita' ou 'despesa'
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    
    categoria = db.relationship('Categoria', backref='transacoes')
    
    def __repr__(self):
        return f'<Transacao {self.descricao} - R$ {self.valor}>'