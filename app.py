"""Punto de entrada de la aplicación Flask."""

import os

from flask import Flask
from controllers.polizas_controller import polizas_bp

app = Flask(
    __name__,
    template_folder="views",
    static_folder="public/static",
    static_url_path="/static",
)

# Configuración para subida de archivos
app.secret_key = os.environ.get("SECRET_KEY", "cambiar-esta-clave-en-produccion")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB máximo

# Crear carpetas de uploads y output si no existen
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(os.path.join("output", "avisos"), exist_ok=True)

# Registrar el Blueprint del controlador
app.register_blueprint(polizas_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
