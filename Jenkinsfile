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
                // 先停掉上一次可能残留的容器（使用 jenkins 前缀避免冲突）
                sh 'docker compose -p jenkins_bank down --volumes --remove-orphans || true'

                // 启动基础设施（MySQL + Redis），测试容器先不启动
                sh 'docker compose -p jenkins_bank up -d --build db redis'
                
                // 等待 MySQL 和 Redis 完全就绪
                sh '''
                    echo "等待 MySQL 就绪..."
                    for i in $(seq 1 30); do
                        if docker compose -p jenkins_bank exec -T db mysqladmin ping -h localhost --silent 2>/dev/null; then
                            echo "MySQL 已就绪 (耗时约 $((i*2)) 秒)"
                            break
                        fi
                        echo "MySQL 等待中... ($i/30)"
                        sleep 2
                    done
                    
                    echo "等待 Redis 就绪..."
                    for i in $(seq 1 10); do
                        if docker compose -p jenkins_bank exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
                            echo "Redis 已就绪"
                            break
                        fi
                        echo "Redis 等待中... ($i/10)"
                        sleep 1
                    done
                '''
                
                // 启动银行服务
                sh 'docker compose -p jenkins_bank up -d --build bank-server'

                // 等待银行服务完全就绪（healthcheck 最多等 90 秒）
                sh '''
                    echo "等待银行服务就绪..."
                    for i in $(seq 1 30); do
                        if docker compose -p jenkins_bank exec -T bank-server curl -sf http://localhost:8000/ > /dev/null 2>&1; then
                            echo "银行服务已就绪 (耗时约 ${i} 秒)"
                            exit 0
                        fi
                        echo "等待中... ($i/30)"
                        sleep 3
                    done
                    echo "银行服务启动超时！"
                    docker compose -p jenkins_bank logs bank-server
                    docker compose -p jenkins_bank logs db
                    exit 1
                '''
            }
        }

        stage('Run Tests') {
            steps {
                // 单独启动测试容器（不加 abort-on-container-exit，不互相影响）
                sh 'docker compose -p jenkins_bank run --rm api-tests'

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
            sh 'docker compose -p jenkins_bank logs api-tests 2>/dev/null || true'
            // 始终清理容器（保留镜像加速下次构建）
            sh 'docker compose -p jenkins_bank down --remove-orphans || true'
        }
        success {
            echo '✅ 自动化测试全部通过！'
        }
        failure {
            echo '❌ 自动化测试存在失败用例，请检查上方日志。'
        }
    }
}
