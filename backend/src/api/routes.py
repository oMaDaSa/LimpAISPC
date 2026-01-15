from flask import Blueprint, jsonify, request
from services.debt_analysis import run_analysis
from core.config import API_PASSWORD

api_bp = Blueprint('api', __name__)

@api_bp.before_request
def verify_password():
    #middleware para verificar senha em todas as rotas da API
    data = request.get_json() or {}
    password = data.get('password', '')
    
    if password != API_PASSWORD:
        return jsonify({"error": "Senha incorreta"}), 401

@api_bp.route('/debt-analysis', methods=['POST'])
def debt_analysis():
    data = request.get_json()
    
    try:
        result = run_analysis(data or {})
        
        return jsonify({
            "status": "success",
            "analysis_json": result["analysis_json"],
            "ai_response": result["ai_response"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500