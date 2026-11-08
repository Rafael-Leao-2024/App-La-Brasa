# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

def agora_brasil():
    return datetime.utcnow() - timedelta(hours=3)

db = SQLAlchemy()

class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loja_aberta = db.Column(db.Boolean, default=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), default='lanche')
    foto = db.Column(db.String(200), nullable=True)
    ativo = db.Column(db.Boolean, default=True)  # Novo campo para ativar/desativar o produto
    permite_extra = db.Column(db.Boolean, default=False) 

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf_cliente = db.Column(db.String(14), nullable=True) # Pode ser nulo se for manual sem CPF
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    taxa_entrega = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Recebido')
    comprovante_url = db.Column(db.String(500), nullable=True) # 🚨 Nova coluna
    
    # 🚨 NOVOS CAMPOS AQUI
    pago = db.Column(db.Boolean, default=False) 
    origem = db.Column(db.String(20), default='online') # 'online' ou 'manual'
    
    total = db.Column(db.Float, nullable=False)
    data_criacao = db.Column(db.DateTime, default=agora_brasil)

    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    observacao = db.Column(db.Text, nullable=True)
    
    produto = db.relationship('Produto')