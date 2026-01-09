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
    app.run(host='0.0.0.0', port=8080, debug=False)