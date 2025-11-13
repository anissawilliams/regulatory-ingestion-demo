from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/regulations")
def get_regulations():
    with open("regulations.json") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000)
