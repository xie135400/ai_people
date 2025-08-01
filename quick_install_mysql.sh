#!/bin/bash

echo "=== AI人流分析系统 - MySQL快速安装脚本 ==="

# 检查是否已安装MySQL
if command -v mysql &> /dev/null; then
    echo "✓ MySQL已安装"
else
    echo "正在安装MySQL..."
    brew install mysql
fi

# 启动MySQL服务
echo "启动MySQL服务..."
brew services start mysql

# 等待服务启动
sleep 3

# 检查服务状态
if brew services list | grep mysql | grep started > /dev/null; then
    echo "✓ MySQL服务已启动"
else
    echo "✗ MySQL服务启动失败"
    echo "请手动运行: brew services start mysql"
    exit 1
fi

# 测试连接
echo "测试MySQL连接..."
python3 -c "
import pymysql
try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        charset='utf8mb4'
    )
    print('✓ MySQL连接成功!')
    conn.close()
except Exception as e:
    print(f'✗ MySQL连接失败: {e}')
    print('请检查MySQL配置或运行: mysql_secure_installation')
"

echo ""
echo "=== 安装完成 ==="
echo "下一步操作:"
echo "1. 运行: python setup_mysql.py"
echo "2. 运行: python test_mysql_database.py"
echo "3. 运行: python run_web_app.py --port 8443 --no-ssl"
echo "4. 访问: http://localhost:8443" 