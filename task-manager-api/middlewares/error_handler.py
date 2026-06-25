import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Método não permitido'}), 405

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error("Unhandled exception: %s: %s", type(e).__name__, str(e), exc_info=True)
        return jsonify({'error': 'Erro interno do servidor'}), 500
