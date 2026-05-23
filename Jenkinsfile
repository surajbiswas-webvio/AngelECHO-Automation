pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }

    parameters {
        choice(name: 'SUITE', choices: ['smoke', 'regression', 'e2e', 'api'], description: 'Pytest marker to execute')
        choice(name: 'ENV', choices: ['qa', 'staging'], description: 'Target environment')
        string(name: 'WORKERS', defaultValue: 'auto', description: 'pytest-xdist workers')
    }

    environment {
        HEADLESS = 'true'
        CUSTOMER_EMAIL = credentials('customer-email')
        CUSTOMER_PASSWORD = credentials('customer-password')
    }

    stages {
        stage('Install') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'pip install -r requirements.txt'
                bat 'playwright install'
            }
        }

        stage('Test') {
            steps {
                bat 'pytest -m %SUITE% --env %ENV% -n %WORKERS%'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**, screenshots/**, logs/**', allowEmptyArchive: true
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'html-report.html',
                reportName: 'Pytest HTML Report',
                keepAll: true,
                alwaysLinkToLastBuild: true,
                allowMissing: true
            ])
        }
    }
}

