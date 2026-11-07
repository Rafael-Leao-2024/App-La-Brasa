from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import Produto, db, Pedido, ItemPedido, Configuracao
import os
import uuid
from flask import current_app as app

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def admin_dashboard():
    # Busca todos os pedidos, ordenando do mais novo para o mais antigo
    # Você pode filtrar por status se quiser (ex: Pedido.query.filter_by(status='Recebido'))
    pedidos = Pedido.query.order_by(Pedido.id.desc()).all()
    config = Configuracao.query.first()
    return render_template('admin/dashboard.html', pedidos=pedidos, loja_aberta=config.loja_aberta)


@admin_bp.route('/produtos', methods=['GET', 'POST'])
def admin_produtos():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        categoria = request.form.get('categoria')
        foto = request.files.get('foto')

        nome_arquivo = None
        
        # 🚨 CORREÇÃO AQUI: Lógica robusta de Upload
        if foto and foto.filename != '':
            # Pega a extensão do arquivo (ex: .jpg, .png)
            extensao = os.path.splitext(foto.filename)[1].lower()
            
            # Gera um nome único usando UUID (ex: 550e8400-e29b-41d4-a716.jpg)
            nome_arquivo = f"{uuid.uuid4().hex}{extensao}"
            
            # Salva o arquivo fisicamente na pasta
            caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
            foto.save(caminho_completo)

        novo_produto = Produto(
            nome=nome, 
            descricao=descricao, 
            preco=float(preco), 
            categoria=categoria, 
            foto=nome_arquivo
        )
        db.session.add(novo_produto)
        db.session.commit()
        return redirect(url_for('admin.admin_produtos'))

    produtos = Produto.query.all()
    return render_template('admin/produtos.html', produtos=produtos)

@admin_bp.route('/novo-pedido')
def admin_novo_pedido():
    produtos = Produto.query.all()
    return render_template('admin/novo_pedido.html', produtos=produtos)


@admin_bp.route('/api/salvar-pedido-manual', methods=['POST'])
def salvar_pedido_manual():
    data = request.json
    
    # Cria o pedido manual
    novo_pedido = Pedido(
        nome_cliente=data['nome_cliente'],
        telefone=data.get('telefone', ''),
        endereco=data.get('endereco', 'Retirada no Balcão'),
        taxa_entrega=float(data.get('taxa_entrega', 0)),
        forma_pagamento=data['pagamento'],
        pago=data['pago'], # Recebe True ou False do checkbox
        origem='manual',
        total=float(data['total'])
    )
    db.session.add(novo_pedido)
    db.session.commit()

    for item in data['itens']:
        novo_item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=item['id'],
            quantidade=item['quantidade'],
            observacao=item.get('observacao', '')
        )
        db.session.add(novo_item)
    
    db.session.commit()
    return jsonify({"sucesso": True, "pedido_id": novo_pedido.id})

@admin_bp.route('/api/marcar-pago/<int:pedido_id>', methods=['POST'])
def marcar_pago(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.pago = not pedido.pago # Inverte o status (pago/nao pago)
    db.session.commit()
    return jsonify({"sucesso": True, "pago": pedido.pago})


@admin_bp.route('/imprimir/<int:pedido_id>')
def imprimir_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/imprimir.html', pedido=pedido)


@admin_bp.route('/api/alterar-status/<int:pedido_id>', methods=['POST'])
def alterar_status(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    novo_status = request.json.get('status')
    
    # Status permitidos: Recebido, Em Preparo, Saiu para Entrega, Concluido, Cancelado
    pedido.status = novo_status
    db.session.commit()
    return jsonify({"sucesso": True, "novo_status": pedido.status})


@admin_bp.route('/api/toggle-loja', methods=['POST'])
def toggle_loja():
    config = Configuracao.query.first()
    config.loja_aberta = not config.loja_aberta
    db.session.commit()
    return jsonify({"loja_aberta": config.loja_aberta})


@admin_bp.route('/pedido/<int:pedido_id>')
def detalhes_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/detalhe.html', pedido=pedido)


