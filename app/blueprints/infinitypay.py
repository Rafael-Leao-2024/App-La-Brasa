import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Substitua pela sua InfiniteTag (sem o $)


def gerar_link_pagamento(pedido_id, total_reais, nome_cliente, descricao_pedido, url_webhook, url_retorno):
    """
    Cria um link de checkout na InfinitePay.
    Retorna a URL de pagamento ou None se houver erro.
    """
    # A API exige o valor em centavos
    valor_centavos = int(round(total_reais * 100))
    
    payload = {
        "handle": os.getenv("INFINITE_TAG"),
        "order_nsu": str(pedido_id),
        "redirect_url": url_retorno,
        "webhook_url": url_webhook,
        "items": [
            {
                "quantity": 1,
                "price": valor_centavos,
                "description": descricao_pedido or f"Pedido #{pedido_id} - La Brasa"
            }
        ],
        "customer": {
            "name": nome_cliente
        }
    }

    try:
        # A documentação oficial indica este endpoint
        response = requests.post(
            "https://api.checkout.infinitepay.io/links",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        dados = response.json()
        # A API retorna a URL no campo "url"
        return dados.get("url")
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao gerar link InfinitePay: {e}")
        # Se houver resposta de erro, imprime para debug
        if hasattr(e, 'response') and e.response is not None:
            print(f"Detalhes: {e.response.text}")
        return None