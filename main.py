import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# AYARLAR: Kendi anahtarlarını buraya gir!
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/") 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "SENIN_GROQ_KEYIN_BURAYA")
DB_NAME = "unitfire_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.7}
    )
    return jsonify(resp.json())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
