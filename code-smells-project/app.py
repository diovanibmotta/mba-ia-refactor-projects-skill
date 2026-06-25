import logging
from flask import Flask, jsonify
from flask_cors import CORS

from src.config.settings import SECRET_KEY, DEBUG, PORT, HOST
from src.views.product_routes import product_bp
from src.views.user_routes import user_bp
from src.views.order_routes import order_bp
from src.views.report_routes import report_bp
from src.middlewares.error_handler import register_error_handlers
from database import get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG

    CORS(app)

    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo a API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    @app.route("/health")
    def health_check():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
        }), 200

    return app


if __name__ == "__main__":
    get_db()
    app = create_app()
    import logging as _logging
    _logging.getLogger().info("Server starting at http://%s:%s", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)
