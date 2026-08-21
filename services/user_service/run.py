import os
from dotenv import load_dotenv
from app.database import init_db

load_dotenv()

from flask import Flask
from flask_cors import CORS
from app.routes import main
app = Flask(__name__)

# Todos os serviços compartilham a mesma SECRET_KEY: é ela que faz um JWT
# emitido pelo auth_service valer aqui também.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: SECRET_KEY não configurada no User Service.")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # teto de 1 MB por request
app.register_blueprint(main, url_prefix='/api')
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    init_db()
    app.run(host='127.0.0.1', port=5003, debug=True)
