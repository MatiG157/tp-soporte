from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos para registrar relaciones
from app.models.user import Usuario
from app.models.user_preferences import PreferenciasUsuario
from app.models.accommodation_type import TipoAlojamiento
from app.models.trip import Viaje
from app.models.cost import Costo
from app.models.itinerary import Itinerario
from app.models.activity import Actividad
from app.models.ai_recommendation import RecomendacionIA