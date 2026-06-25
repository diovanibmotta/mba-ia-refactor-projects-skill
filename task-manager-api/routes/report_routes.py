from flask import Blueprint, jsonify
from controllers.report_controller import summary_report, user_report

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary():
    return jsonify(summary_report()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report_route(user_id):
    report, error, status = user_report(user_id)
    if error:
        return jsonify({'error': error}), status
    return jsonify(report), status
