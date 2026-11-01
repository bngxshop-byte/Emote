import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
