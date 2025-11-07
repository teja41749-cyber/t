from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from app.services.diagram_generator import DiagramGenerator
from app.services.nlp_processor import NLPProcessor
import os

app = Flask(__name__)
CORS(app)

# ---- JSON error handler (prevents HTML error pages) ----
@app.errorhandler(Exception)
def handle_any_error(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.name, "detail": e.description}), e.code
    app.logger.exception(e)
    return jsonify({"error": "internal_server_error", "detail": str(e)}), 500

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

# quick ping for debugging
@app.get("/api/ping")
def ping():
    return jsonify({"ok": True})

processor = NLPProcessor()
diagrammer = DiagramGenerator()

@app.post("/api/extract")
def extract():
    data = request.get_json() or {}
    text = data.get("text", "")
    if len(text) < 50:
        return jsonify({"error": "Text too short (min 50 characters)"}), 400
    if len(text) > 10000:
        return jsonify({"error": "Text too long (max 10000 characters)"}), 400
    uml = processor.process_requirements(text)
    mermaid = diagrammer.convert_to_mermaid(uml)
    return jsonify({"uml_model": uml, "mermaid_code": mermaid})

# ---- serve the UI at "/" ----
ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(os.path.dirname(ROOT), "frontend", "public")

@app.get("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.get("/<path:path>")
def public_files(path):
    return send_from_directory(PUBLIC_DIR, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
