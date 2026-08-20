import os
from app.database import init_db
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from app.routes import main
app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: SECRET_KEY não encontrada no ambiente (.env).")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # teto de 1 MB por request
app.register_blueprint(main, url_prefix="/api/auth")
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
