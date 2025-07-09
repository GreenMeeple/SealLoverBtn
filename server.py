from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, UTC
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import requests

app = Flask(__name__)
CORS(app, origins=["https://greenmeeple.github.io"])

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class SealMetadata(Base):
    __tablename__ = "seals"
    id = Column(Integer, primary_key=True)
    photographer = Column(String)
    profile = Column(String)
    image = Column(String, unique=True)  # Prevent duplicates
    timestamp = Column(DateTime, default=datetime.now(UTC).isoformat())

Base.metadata.create_all(engine)

@app.route("/save", methods=["POST"])
def save_metadata():
    data = request.get_json()
    required = ["photographer", "profile", "image"]

    if not all(key in data for key in required):
        return jsonify({"error": "Missing required fields"}), 400

    session = Session()
    # Check for duplicates
    if session.query(SealMetadata).filter_by(image=data["image"]).first():
        return jsonify({"status": "duplicate"}), 200

    seal = SealMetadata(
        photographer=data["photographer"],
        profile=data["profile"],
        image=data["image"]
    )
    session.add(seal)
    session.commit()
    session.close()
    return jsonify({"status": "saved"}), 200

@app.route("/")
def home():
    return "✅ PostgreSQL Seal Metadata Server is Live!"

@app.route("/data", methods=["GET"])
def get_data():
    session = Session()
    seals = session.query(SealMetadata).all()
    result = [{
        "photographer": s.photographer,
        "profile": s.profile,
        "image": s.image,
        "timestamp": s.timestamp.isoformat()
    } for s in seals]
    session.close()
    return jsonify(result)

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
