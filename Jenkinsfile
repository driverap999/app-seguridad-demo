pipeline {
    agent any

    stages {
        // --- ETAPA 1: Preparación del Entorno ---
        stage('Setup Environment') {
            steps {
                script {
                    // Creamos el entorno virtual y aseguramos las herramientas
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install safety bandit flask
                    '''
                }
            }
        }

        // --- ETAPA 2: SCA - Análisis de Dependencias (Safety) ---
        // Falla si las librerías en requirements.txt son antiguas/inseguras
        stage('SCA - Safety Check') {
            steps {
                script {
                    echo "--- Iniciando Escaneo de Dependencias (SCA) ---"
                    
                    // 1. Ejecutar Safety y guardar reporte (|| true evita que pare aquí)
                    sh '. venv/bin/activate && safety check -r requirements.txt --full-report > safety_report.txt || true'
                    
                    // 2. Verificar si hubo error para detener el pipeline manualmente
                    def safetyExitCode = sh(script: '. venv/bin/activate && safety check -r requirements.txt', returnStatus: true)
                    
                    if (safetyExitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error("DETENIDO: Safety encontró vulnerabilidades críticas. Ver 'safety_report.txt'.")
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'safety_report.txt', allowEmptyArchive: true
                }
            }
        }

        // --- ETAPA 3: SAST - Análisis Estático de Código (Bandit) ---
        // Falla si tu código (app.py) tiene malas prácticas
        stage('SAST - Bandit Check') {
            steps {
                script {
                    echo "--- Iniciando Escaneo de Código Estático (SAST) ---"
                    
                    // 1. Ejecutar Bandit EXCLUYENDO venv (-x venv) para no escanear librerías ajenas
                    sh '. venv/bin/activate && bandit -r . -x venv -f html -o bandit_report.html || true'
                    
                    // 2. Verificar estatus (también excluyendo venv)
                    def banditExitCode = sh(script: '. venv/bin/activate && bandit -r . -x venv', returnStatus: true)
                    
                    if (banditExitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error("DETENIDO: Bandit encontró código inseguro en tus archivos. Ver 'bandit_report.html'.")
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit_report.html', allowEmptyArchive: true
                }
            }
        }

        // --- ETAPA 4: DAST & Despliegue (Solo llega aquí la Versión 3) ---
        stage('Deploy & DAST') {
            steps {
                script {
                    echo "--- Desplegando Aplicación para Pruebas ---"
                    // Ejecutamos la app en segundo plano
                    sh 'nohup venv/bin/python app.py > app_output.log 2>&1 &'
                    sh 'sleep 5' // Esperar a que levante
                    
                    echo "--- Ejecutando DAST (Prueba de conexión) ---"
                    // Si el curl responde éxito (código 200), la prueba pasa
                    sh 'curl -f http://127.0.0.1:5000'
                }
            }
            post {
                always {
                    // Limpieza: Matar el proceso de python al terminar
                    sh 'pkill -f "python app.py" || true'
                }
            }
        }
    }
}
