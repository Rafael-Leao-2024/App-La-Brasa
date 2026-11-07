from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Configuracao, Produto, Pedido, ItemPedido, db
from app.blueprints.utils import calcular_taxa_entrega
from app.blueprints.infinitypay import gerar_link_pagamento

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

@cliente_bp.route('/')
def index():
    config = Configuracao.query.first()
    produtos = Produto.query.filter_by(ativo=True).all()
    return render_template('cliente/index.html', produtos=produtos, loja_aberta=config.loja_aberta)


@cliente_bp.route('/api/fechar-pedido', methods=['POST'])
def fechar_pedido():
    data = request.json
    
    if not Configuracao.query.first().loja_aberta:
        return jsonify({"erro": "A loja está fechada no momento."}), 400

    # Calcula a taxa de entrega
    taxa = calcular_taxa_entrega(data.get('lat'), data.get('lng'))
    # if taxa == -1:
    #     return jsonify({"erro": "Endereço fora da área de entrega."}), 400

    # Cria o pedido
    novo_pedido = Pedido(
        cpf_cliente=data['cpf'],
        nome_cliente=data['nome'],
        telefone=data['telefone'],
        endereco=data['endereco'],
        lat=data.get('lat'),
        lng=data.get('lng'),
        taxa_entrega=taxa,
        forma_pagamento=data['pagamento'],
        total=float(data['total']) + taxa
    )
    db.session.add(novo_pedido)
    db.session.commit()

    # Adiciona os itens
    for item in data['itens']:
        novo_item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=item['id'],
            quantidade=item['quantidade'],
            observacao=item.get('observacao', '')
        )
        db.session.add(novo_item)
    
    db.session.commit()

    # Aqui entraria a integração com a InfinityPay
    if data['pagamento'] in ['pix', 'cartao']:
        from app.blueprints.infinitypay import gerar_link_pagamento
        
        # Define as URLs que a InfinitePay vai usar
        url_webhook = url_for('cliente.webhook_infinitypay', _external=True)
        
        # O redirecionamento passa o ID do pedido na URL para a tela de acompanhamento
        url_retorno = url_for('cliente.acompanhar_pedido', _external=True) 
        
        link_pagamento = gerar_link_pagamento(
            pedido_id=novo_pedido.id,
            total_reais=novo_pedido.total,
            nome_cliente=novo_pedido.nome_cliente,
            descricao_pedido=f"Pedido #{novo_pedido.id} - La Brasa",
            url_webhook=url_webhook,
            url_retorno=url_retorno
        )
        
        if link_pagamento:
            return jsonify({
                "sucesso": True, 
                "pedido_id": novo_pedido.id, 
                "link_pagamento": link_pagamento
            })
        else:
            # Se a API falhar, o pedido já foi criado, mas avisamos o cliente
            return jsonify({
                "sucesso": True, 
                "pedido_id": novo_pedido.id, 
                "aviso": "Pedido criado, mas não foi possível gerar o link de pagamento. Pague na entrega."
            })    

    return jsonify({"sucesso": True, "pedido_id": novo_pedido.id})



@cliente_bp.route('/api/status-pedido/<cpf>', methods=['GET', 'POST'])
def status_pedido(cpf):
    # Remove máscara do CPF (apenas números)
    # cpf_limpo = ''.join(filter(str.isdigit, cpf))
    # print(f"Buscando pedido para CPF: {cpf_limpo}")  # Debugging line
    
    # Busca o pedido mais recente do CPF
    pedido = Pedido.query.filter(Pedido.cpf_cliente.contains(cpf)).order_by(Pedido.data_criacao.desc()).first()
    
    if not pedido:
        return jsonify({"erro": "Nenhum pedido encontrado para este CPF."}), 404


    # Criar link de pagamento se o pedido não estiver pago e a forma de pagamento for pix ou cartão
    if not pedido.pago and pedido.forma_pagamento in ['pix', 'cartao']:
        from app.blueprints.infinitypay import gerar_link_pagamento
        
        url_webhook = url_for('cliente.webhook_infinitypay', _external=True)
        url_retorno = url_for('cliente.acompanhar_pedido', _external=True)
        
        link_pagamento = gerar_link_pagamento(
            pedido_id=pedido.id,
            total_reais=pedido.total,
            nome_cliente=pedido.nome_cliente,
            descricao_pedido=f"Pedido #{pedido.id} - La Brasa",
            url_webhook=url_webhook,
            url_retorno=url_retorno
        )
        
        if link_pagamento:
            pedido.link_pagamento = link_pagamento
            db.session.commit()
    
    # Monta a lista de itens para enviar para a tela
    itens_formatados = []
    print(pedido)  # Debugging line
    for item in pedido.itens:
        itens_formatados.append({
            "nome": item.produto.nome,
            "quantidade": item.quantidade,
            "preco": item.produto.preco,
            "observacao": item.observacao,
            "foto": item.produto.foto
        })

    print(pedido.link_pagamento)  # Debugging line

    return jsonify({
        "pedido_id": pedido.id,
        "status": pedido.status,
        "total": pedido.total,
        "taxa_entrega": pedido.taxa_entrega,
        "endereco": pedido.endereco,
        "pagamento": pedido.forma_pagamento,
        "pago": pedido.pago,
        "data": pedido.data_criacao.strftime('%d/%m/%Y %H:%M'),
        "itens": itens_formatados,
        "comprovante_url": pedido.comprovante_url,  # Adiciona o link do comprovante
        "link_pagamento": getattr(pedido, 'link_pagamento', None)  # Adiciona o link de pagamento se existir
    })



@cliente_bp.route('/checkout', methods=['GET'])
def checkout():
    config = Configuracao.query.first()
    # Se a loja estiver fechada, impede o acesso
    if not config.loja_aberta:
        return redirect(url_for('cliente.index'))
    return render_template('cliente/checkout.html')


# app.py (Adicione junto com as outras rotas do cliente)

@cliente_bp.route('/api/calcular-frete', methods=['POST'])
def api_calcular_frete():
    data = request.json
    lat = data.get('lat')
    lng = data.get('lng')
    
    taxa = calcular_taxa_entrega(lat, lng)
    print(f"Taxa de entrega calculada: {taxa}")  # Debugging line
    
    if taxa == -1:
        return jsonify({"erro": "Infelizmente seu endereço está fora da nossa área de entrega (máx 10km)."}), 400
        
    return jsonify({"taxa": taxa})


@cliente_bp.route('/acompanhar')
def acompanhar_pedido():
    return render_template('cliente/status.html')



# app.py (adicione esta rota)

@cliente_bp.route('/webhook/infinitypay', methods=['POST'])
def webhook_infinitypay():
    dados = request.json
    print(f"Webhook recebido da InfinitePay: {dados}")  # Debugging line
    
    # A InfinitePay envia o order_nsu que você definiu ao criar o link
    order_nsu = dados.get('order_nsu')
    transaction_nsu = dados.get('transaction_nsu')
    
    if not order_nsu:
        # Retorna 400 para a InfinitePay tentar reenviar depois [citation:2]
        return jsonify({"erro": "order_nsu ausente"}), 400
    
    pedido = Pedido.query.get(int(order_nsu))
    
    if not pedido:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    
    # Marca como pago se ainda não estiver
    if not pedido.pago:
        pedido.pago = True
        pedido.comprovante_url = dados.get('receipt_url') # 🚨 Salvando o link
        
        db.session.commit()
        # É crucial responder 200 OK rapidamente para a InfinitePay [citation:5]
    return jsonify({"status": "ok"}), 200
