import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Leer las variables de entorno
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD', '') # Cadena vacía por defecto si no hay pass
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# Configuramos la conexión a MySQL usando pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Un pequeño modelo de ejemplo
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)

@app.route("/")
def index():
    return {"mensaje": "¡Servidor Flask conectado a MySQL correctamente!"}

if __name__ == "__main__":
    # Importante: La base de datos (DB_NAME) ya debe existir en tu MySQL Server.
    # Estas líneas solo crean las tablas, no la base de datos en sí.
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000)