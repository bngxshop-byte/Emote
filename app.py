import os
import requests
from flask import Flask, send_from_directory, jsonify, request, Response

app = Flask(__name__, static_folder=".", static_url_path="")

# ===== إعدادات مصدر البيانات =====
IMAGE_BASE = "https://raw.githubusercontent.com/KillerSharmaBot/Emote/refs/heads/main/emote_image"
DATA_URL = "https://raw.githubusercontent.com/KillerSharmaBot/Emote/main/itemData.json"


# ===== الصفحة الرئيسية والملفات الثابتة =====
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


# ===== API: جلب صورة الإيموجي بالـ ID =====
@app.route("/api/emote")
def get_emote():
    emote_id = request.args.get("id")
    mode = request.args.get("mode", "image")

    # التحقق من وجود ID
    if not emote_id:
        return jsonify({
            "error": "Missing 'id' parameter",
            "example": "/api/emote?id=909042007"
        }), 400

    # التحقق أن ID رقمي
    if not emote_id.isdigit():
        return jsonify({
            "error": "ID must be numeric",
            "example": "/api/emote?id=909042007"
        }), 400

    image_url = f"{IMAGE_BASE}/{emote_id}.png"

    # وضع الرابط فقط (JSON)
    if mode == "url":
        return jsonify({"id": emote_id, "url": image_url})

    # جلب الصورة والتحقق من وجودها
    try:
        r = requests.get(image_url, timeout=10)
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch image", "details": str(e)}), 502

    if r.status_code != 200 or not r.content:
        return jsonify({"error": f"Emote with ID {emote_id} not found"}), 404

    # إرجاع الصورة مباشرة
    return Response(
        r.content,
        mimetype="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ===== API: معلومات الإيموجي (اسم + رابط) =====
@app.route("/api/emote/info")
def emote_info():
    emote_id = request.args.get("id")
    if not emote_id or not emote_id.isdigit():
        return jsonify({"error": "Missing or invalid 'id' parameter"}), 400

    try:
        data = requests.get(DATA_URL, timeout=10).json()
    except Exception as e:
        return jsonify({"error": "Failed to load emote data", "details": str(e)}), 502

    for item in data:
        if str(item.get("Id")) == emote_id:
            return jsonify({
                "id": emote_id,
                "name": item.get("name"),
                "url": f"{IMAGE_BASE}/{emote_id}.png",
            })

    return jsonify({"error": f"Emote with ID {emote_id} not found"}), 404


# ===== CORS =====
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
