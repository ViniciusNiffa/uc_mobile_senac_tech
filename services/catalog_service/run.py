import os
from flask import Flask
from app.routes import main
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: SECRET_KEY ausente.")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024  # teto de 6 MB por request (uploads)
app.register_blueprint(main)
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)