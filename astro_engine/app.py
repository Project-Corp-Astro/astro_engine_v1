

# from flask import Flask
# from flask_cors import CORS
# import swisseph as swe
# import logging
# from .engine.routes.LahairiAyanmasa import bp
# from .engine.routes.KpNew import kp
# from .engine.routes.RamanAyanmasa import rl
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# logging.basicConfig(level=logging.DEBUG)

# # Set Swiss Ephemeris path
# swe.set_ephe_path('astro_engine/ephe')

# # Register the blueprint containing all routes
# app.register_blueprint(bp)   # lahairi
# app.register_blueprint(kp)      # KP System
# app.register_blueprint(rl)          # Raman  




# if __name__ == "__main__":
#     app.run(debug=True, port=5002)



# from flask import Flask
# from flask_cors import CORS
# import swisseph as swe
# import logging
# from .engine.routes.LahairiAyanmasa import bp
# from .engine.routes.KpNew import kp
# from .engine.routes.RamanAyanmasa import rl
# import sys
# import platform

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# logging.basicConfig(level=logging.DEBUG)

# # Set Swiss Ephemeris path
# swe.set_ephe_path('astro_engine/ephe')

# # Register the blueprint containing all routes
# app.register_blueprint(bp)   # Lahairi Ayanmasa
# app.register_blueprint(kp)      # KP System
# app.register_blueprint(rl)      # Raman Ayanmasa

# if __name__ == "__main__":
#     if len(sys.argv) > 1 and sys.argv[1] == "--production":
#         if platform.system() == 'Windows':
#             # Import and use Waitress on Windows
#             try:
#                 from waitress import serve
#             except ImportError:
#                 print("Waitress is not installed. Please install it with 'pip install waitress'.")
#                 sys.exit(1)
#             serve(app, host='0.0.0.0', port=5002)
#         else:
#             # Import and use Gunicorn on Unix-like systems
#             try:
#                 from gunicorn.app.base import BaseApplication
#             except ImportError:
#                 print("Gunicorn is not installed. Please install it with 'pip install gunicorn'.")
#                 sys.exit(1)

#             class StandaloneApplication(BaseApplication):
#                 def __init__(self, app, options=None):
#                     self.options = options or {}
#                     self.application = app
#                     super().__init__()

#                 def load_config(self):
#                     for key, value in self.options.items():
#                         if key in self.cfg.settings and value is not None:
#                             self.cfg.set(key, value)

#                 def load(self):
#                     return self.application

#             options = {
#                 'bind': '0.0.0.0:5002',
#                 'workers': 4,
#             }
#             StandaloneApplication(app, options).run()
#     else:
#         # Development mode with Flask's built-in server
#         app.run(debug=True, port=5002)




import platform
import sys
from flask import Flask
from flask_cors import CORS
import swisseph as swe
import logging

# Import blueprints (adjust paths as per your project structure)
from .engine.routes.KpNew import kp
from .engine.routes.LahairiAyanmasa import bp
from .engine.routes.RamanAyanmasa import rl

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.DEBUG)

# Set Swiss Ephemeris path (adjust path as needed)
swe.set_ephe_path('astro_engine/ephe')

# Register blueprints
app.register_blueprint(kp)  # KP System routes
app.register_blueprint(bp)  # Lahiri Ayanamsa routes
app.register_blueprint(rl)  # Raman Ayanamsa routes

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        if platform.system() == 'Windows':
            # Use Waitress on Windows
            try:
                from waitress import serve
            except ImportError:
                print("Waitress is not installed. Please install it with 'pip install waitress'.")
                sys.exit(1)
            serve(app, host='0.0.0.0', port=5002)
        else:
            # Use Gunicorn on Unix-like systems
            try:
                from gunicorn.app.base import BaseApplication
            except ImportError:
                print("Gunicorn is not installed. Please install it with 'pip install gunicorn'.")
                sys.exit(1)

            class StandaloneApplication(BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        if key in self.cfg.settings and value is not None:
                            self.cfg.set(key, value)

                def load(self):
                    return self.application

            options = {
                'bind': '0.0.0.0:5002',     # Bind to all interfaces on port 5002
                'workers': 2,               # Number of worker processes
                'worker_class': 'gthread',  # Use threaded workers
                'threads': 4,               # Number of threads per worker
                'timeout': 120              # Timeout for long-running requests
            }
            StandaloneApplication(app, options).run()
    else:
        # Development mode with Flask's built-in server
        app.run(debug=True, port=5002)