from flask import Flask
from .models import db, Configuracao, Produto, Pedido, ItemPedido
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)
    migrate.init_app(app, db)


    
    # Additional configuration and route setup can be done here
    # Cria o banco de dados na primeira execução
    with app.app_context():
        db.create_all()
        if not Configuracao.query.first():
            db.session.add(Configuracao(loja_aberta=True))
            db.session.commit()

    from app.blueprints.admin import admin_bp
    from app.blueprints.cliente import cliente_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(cliente_bp)
    
    return app