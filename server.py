from flask import Flask, request, jsonify
import os
import shutil

app = Flask(__name__)

@app.route('/move', methods=['POST'])
def move_file():
    data = request.get_json()
    filename = data.get("filename")
    
    src = os.path.join("images", filename)
    dst = os.path.join("new", filename)

    if not os.path.exists(src):
        return jsonify({"error": "File not found"}), 404

    shutil.move(src, dst)
    return jsonify({"status": "moved", "file": filename}), 200

@app.route("/")
def home():
    return "✅ Seal Server is Running!"
