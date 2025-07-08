from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "saved_metadata.json"

@app.route("/save", methods=["POST"])
def save_metadata():
    data = request.get_json()
    required = ["photographer", "profile", "image"]

    if not all(key in data for key in required):
        return jsonify({"error": "Missing required fields"}), 400

    # Add timestamp
    data["timestamp"] = datetime.utcnow().isoformat()

    try:
        # Load existing data if file exists
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                saved = json.load(f)
        else:
            saved = []

        saved.append(data)

        # Write updated data
        with open(DATA_FILE, "w") as f:
            json.dump(saved, f, indent=2)

        return jsonify({"status": "saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Seal Metadata Server is Live!"
