import os
from flask import Flask
from api.routes import api_bp

app = Flask(__name__)

app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return {
        "status": "alive",
        "service": "LimpaAISPC",
        "cloud": "AWS App Runner"
    }, 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)