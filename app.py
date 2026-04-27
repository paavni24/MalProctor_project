"""Flask backend for MalProctor APK Scanner."""
import os
import uuid
import tempfile
from flask import Flask, render_template, request, jsonify
from apk_scanner import scan_apk

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB max upload

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "temp_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def scan():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]

    if not f.filename or not f.filename.lower().endswith(".apk"):
        return jsonify({"error": "Please upload a valid .apk file"}), 400

    # Save to a temp location
    safe_name = f"{uuid.uuid4().hex}.apk"
    apk_path = os.path.join(UPLOAD_FOLDER, safe_name)

    try:
        f.save(apk_path)
        result = scan_apk(apk_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(apk_path):
            os.remove(apk_path)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model": "TUANDROMD LightGBM 99.55%"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] MalProctor starting on http://0.0.0.0:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)
