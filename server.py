from flask import Flask, request, jsonify
import os
import json
import requests
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

@app.route("/seal", methods=["GET"])
def get_seal():
    UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not UNSPLASH_KEY:
        return jsonify({"error": "No API key configured"}), 500

    try:
        res = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": "seal"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}
        )
        data = res.json()

        return jsonify({
            "image": data["urls"]["regular"],
            "alt": data.get("alt_description", ""),
            "photographer": data["user"]["name"],
            "profile": data["user"]["links"]["html"],
            "download": data["links"]["download_location"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
