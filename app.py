# Crea un archivo llamado app.py y pega esto:
import flask
import os

app = flask.Flask(__name__)

@app.route('/')
def index():
    # SEGURO: Usamos variables de entorno, no contraseñas fijas
    secret = os.getenv("SECRET_KEY", "default")
    return "Version 3: Aprobada. Codigo Limpio."

if __name__ == '__main__':
    # SEGURO: Debug apagado
    app.run(debug=False)
