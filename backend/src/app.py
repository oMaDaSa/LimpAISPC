from flask import Flask
from api.routes import api_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return {"status": "alive"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)