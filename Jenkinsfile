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

        // --- ETAPA NUEVA: Análisis de Calidad y Seguridad (SonarQube) ---
        // Se coloca aquí para que analice el código antes de que Safety/Bandit puedan bloquear el pipeline
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "--- Iniciando Análisis con SonarQube ---"
                    // "SonarScanner" es el nombre configurado en Global Tool Configuration
                    def scannerHome = tool 'SonarScanner'
                    
                    // "SonarQube" es el nombre del servidor en System Configuration
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
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

                    // CORRECCIÓN: Escaneamos DIRECTAMENTE 'app.py' en lugar de '.'
                    // Esto evita que se meta en la carpeta venv por error.
                    sh '. venv/bin/activate && bandit app.py -f html -o bandit_report.html || true'

                    // Verificamos estatus solo sobre app.py
                    def banditExitCode = sh(script: '. venv/bin/activate && bandit app.py', returnStatus: true)

                    if (banditExitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error("DETENIDO: Bandit encontró código inseguro en 'app.py'. Ver 'bandit_report.html'.")
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
