pipeline {
    agent any

    environment {
        // Allure 报告路径
        ALLURE_RESULTS = 'allure-results'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Start Services') {
            steps {
                // 先停掉上一次可能残留的容器
                sh 'docker compose down --volumes --remove-orphans || true'

                // 启动基础设施（MySQL + Redis + Bank Server），测试容器先不启动
                sh 'docker compose up -d --build db redis bank-server'

                // 等待银行服务完全就绪（healthcheck 最多等 90 秒）
                sh '''
                    echo "等待银行服务就绪..."
                    for i in $(seq 1 30); do
                        if docker compose exec -T bank-server curl -sf http://localhost:8000/ > /dev/null 2>&1; then
                            echo "银行服务已就绪 (耗时约 ${i} 秒)"
                            exit 0
                        fi
                        echo "等待中... ($i/30)"
                        sleep 3
                    done
                    echo "银行服务启动超时！"
                    docker compose logs bank-server
                    exit 1
                '''
            }
        }

        stage('Run Tests') {
            steps {
                // 单独启动测试容器（不加 abort-on-container-exit，不互相影响）
                sh 'docker compose run --rm api-tests'

                // 把 allure-results 从容器持久化目录复制出来
                // （docker compose run 的 volume 如果映射了就自动保留）
            }
        }

        stage('Generate Report') {
            steps {
                // 如果安装了 allure 命令行工具，生成 HTML 报告
                sh 'allure generate ${ALLURE_RESULTS} -o allure-report --clean || echo "Allure CLI 未安装，跳过报告生成"'
            }
        }
    }

    post {
        always {
            // 打印测试日志方便排查
            sh 'docker compose logs api-tests 2>/dev/null || true'
            // 始终清理容器（保留镜像加速下次构建）
            sh 'docker compose down --remove-orphans || true'
        }
        success {
            echo '✅ 自动化测试全部通过！'
        }
        failure {
            echo '❌ 自动化测试存在失败用例，请检查上方日志。'
        }
    }
}
