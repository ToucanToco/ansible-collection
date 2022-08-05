// This Jenkinsfile is dedicated to the jenkins job: ansible-collection
//
// This job is the CI for the ansible-collection project

@Library('toucan-jenkins-lib')_
import com.toucantoco.ToucanVars

RELEASE_BRANCH_NAMES = [
    'master',
]

pipeline {
    agent any

    options {
      // Enable color in logs
      ansiColor('gnome-terminal')
    }

    environment {
        BUILD_RANDOM_ID = Math.round(Math.random() * 1000000)
        GITHUB_TOKEN = credentials('GITHUB_TOUCANTOCO_TOKEN')
    }

    stages {
        stage('Test') {
            steps {
                storeStage()
                sh 'make docker-test'
            }
        }

        stage('Build and Deploy') {
            when {
                expression {
                  // Only when the latest commit messages is like vX.Y.Z
                  // and the branch is declared in RELEASE_BRANCH_NAMES
                  LAST_COMMIT_MESSAGE = sh(
                    script: 'git log --format=%B -n 1',
                    returnStdout: true
                  ).trim()
                  return RELEASE_BRANCH_NAMES.contains(BRANCH_NAME) && LAST_COMMIT_MESSAGE ==~ /v\d+\.\d+\.\d+$/
                }
            }

            stages {
                stage('Build archive') {
                    steps {
                        storeStage()
                        sh 'make docker-build'
                    }
                }
                stage('Create release and push archive') {
                    steps {
                        storeStage()
                        sh 'make release-version'
                    }
                }
            }
        }
    }

    post {
        failure {
          postSlackNotif()
        }

        cleanup {
          sh 'make clean'
        }

        always {
          // Store build result in a format parsable for our Elastic stack
          logKibana()
        }
      }
}
