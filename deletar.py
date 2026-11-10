from app import create_app
from app.models import Pedido, ItemPedido

# Deletar itens de pedidos e pedios

app = create_app()

with app.app_context():
    # Deletar todos os itens de pedidos
    ItemPedido.query.delete()
    # Deletar todos os pedidos
    Pedido.query.delete()
    # Commit das alterações no banco de dados
    from app import db
    db.session.commit()
