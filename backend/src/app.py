from flask import Flask
from flask_cors import CORS
from api.routes import api_bp
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(api_bp, url_prefix='/api')

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/')
def health_check():
    return {
        "status": "alive",
        "service": "LimpaAISPC",
        "cloud": "AWS Lambda"
    }, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)