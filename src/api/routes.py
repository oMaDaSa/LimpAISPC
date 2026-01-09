from flask import Blueprint, jsonify, request
#from services.ai import ai_response

'''
api_bp = Blueprint('api', __name__)

@api_bp.route('/ai', methods=['POST'])
def ai():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            "error": "'text' field is required",
            }), 400
    
    try:
        response = ai_response(data['text'])
        
        return jsonify({
            "status": "success",
            "ai_response": response
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''