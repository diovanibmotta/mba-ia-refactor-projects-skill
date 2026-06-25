from flask import Blueprint, jsonify
from src.controllers import report_controller

report_bp = Blueprint("reports", __name__)


@report_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    relatorio = report_controller.sales_report()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
