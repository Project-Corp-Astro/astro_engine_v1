

from flask import Flask
from flask_cors import CORS
import swisseph as swe
import logging
from .engine.routes.LahairiAyanmasa import bp
from .engine.routes.KpNew import kp
from .engine.routes.RamanAyanmasa import rl
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.DEBUG)

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Register the blueprint containing all routes
app.register_blueprint(bp)   # lahairi
app.register_blueprint(kp)      # KP System
app.register_blueprint(rl)          # Raman  




if __name__ == "__main__":
    app.run(debug=True, port=5002)