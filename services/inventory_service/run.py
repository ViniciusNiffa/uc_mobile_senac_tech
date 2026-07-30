import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from app.routes import main
app = Flask(__name__)
app.register_blueprint(main, url_prefix="/api/estoque")  
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("ERRO CRÍTICO: SECRET_KEY não configurada.")

app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)