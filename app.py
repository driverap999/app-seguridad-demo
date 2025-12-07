# Modifica app.py con esto:
import flask
import subprocess

app = flask.Flask(__name__)

@app.route('/')
def index():
    # ERROR SAST: Contraseña hardcodeada (Bandit B105)
    password = "admin123_password_super_secreta"
    
    # ERROR SAST: Ejecución de shell (Bandit B602)
    subprocess.call("ls -la", shell=True)
    
    return "Version 2: Falla en SAST (Bandit)"

if __name__ == '__main__':
    app.run(debug=True)
