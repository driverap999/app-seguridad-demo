pipeline {
    agent any

    stages {
        // ETAPA 1: Preparación del Entorno Virtual
        stage('Setup Environment') {
            steps {
                // Kali es estricto con Python (PEP 668), por eso USAMOS venv OBLIGATORIAMENTE
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install safety bandit flask
                '''
            }
        }

        // ETAPA 2: SCA - Safety (Falla aquí la v1)
        stage('SCA - Safety Check') {
            steps {
                script {
                    echo "--- Iniciando Escaneo de Dependencias ---"
                    // Ejecutamos Safety y guardamos el reporte. "|| true" evita que Jenkins pare aquí.
                    sh '. venv/bin/activate && safety check -r requirements.txt --full-report > safety_report.txt || true'
                    
                    // Verificamos si hubo error
                    def safetyExitCode = sh(script: '. venv/bin/activate && safety check -r requirements.txt', returnStatus: true)
                    
                    if (safetyExitCode != 0) {
                        // Marcamos el error visualmente para el profesor
                        currentBuild.result = 'FAILURE'
                        error("DETENIDO: Safety encontró vulnerabilidades. Ver reporte adjunto.")
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'safety_report.txt', allowEmptyArchive: true
                }
            }
        }

        // ETAPA 3: SAST - Bandit (Falla aquí la v2)
        stage('SAST - Bandit Check') {
            steps {
                script {
                    echo "--- Iniciando Escaneo de Código Estático ---"
                    sh '. venv/bin/activate && bandit -r . -f html -o bandit_report.html || true'
                    
                    def banditExitCode = sh(script: '. venv/bin/activate && bandit -r .', returnStatus: true)
                    
                    if (banditExitCode != 0) {
                        currentBuild.result = 'FAILURE'
                        error("DETENIDO: Bandit encontró código inseguro. Ver reporte adjunto.")
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit_report.html', allowEmptyArchive: true
                }
            }
        }

        // ETAPA 4: DAST & Deploy (Solo llega la v3)
        stage('Deploy & DAST') {
            steps {
                script {
                    echo "--- Desplegando App Segura ---"
                    // Ejecutamos en background (&)
                    sh 'nohup venv/bin/python app.py > app_output.log 2>&1 &'
                    sh 'sleep 5'
                    
                    echo "--- Ejecutando Test Dinámico ---"
                    // Prueba simple de conexión
                    sh 'curl -f http://127.0.0.1:5000'
                }
            }
            post {
                always {
                    // Matar el proceso al terminar para liberar el puerto 5000
                    sh 'pkill -f "python app.py" || true'
                }
            }
        }
    }
}
