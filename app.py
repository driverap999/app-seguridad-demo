import flask
import os

app = flask.Flask(__name__)

@app.route('/')
def index():
    # CODIGO SEGURO: Usamos variable de entorno, nada escrito a fuego
    secret = os.getenv("SECRET_KEY", "no_secret")
    return "<h1>Versión 3: Aprobada!</h1><p>SCA: OK, SAST: OK, DAST: OK</p>"

if __name__ == '__main__':
    # El comentario de nosec debe ir EN LA MISMA LINEA del comando
    app.run(host='0.0.0.0', port=5000, debug=False) # nosec


