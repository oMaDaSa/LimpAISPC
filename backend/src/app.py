from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def helllo_world():
    return jsonify({
        "status": "success",
        "message": "Hello, World!"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)