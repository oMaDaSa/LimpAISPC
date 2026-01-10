from flask import Flask
from api.routes import api_bp
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix='/api')

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