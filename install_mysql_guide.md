# MySQL安装指南

## 问题诊断

您遇到的安装报错可能是因为MySQL数据库服务器未安装或未启动。以下是解决方案：

## 方案1: 使用Homebrew安装MySQL (推荐)

### 1. 安装MySQL
```bash
# 安装MySQL
brew install mysql

# 启动MySQL服务
brew services start mysql

# 设置root密码（首次安装）
mysql_secure_installation
```

### 2. 验证安装
```bash
# 检查MySQL服务状态
brew services list | grep mysql

# 测试连接
mysql -u root -p
```

## 方案2: 使用Docker运行MySQL

如果您不想安装MySQL到系统，可以使用Docker：

### 1. 安装Docker (如果未安装)
```bash
brew install --cask docker
```

### 2. 运行MySQL容器
```bash
# 启动MySQL容器
docker run --name mysql-ai-people \
  -e MYSQL_ROOT_PASSWORD=starunion \
  -e MYSQL_DATABASE=ai_people_analytics \
  -p 3306:3306 \
  -d mysql:8.0

# 检查容器状态
docker ps
```

## 方案3: 使用云数据库

您也可以使用云数据库服务，如：
- AWS RDS
- Google Cloud SQL
- Azure Database for MySQL

## 验证连接

安装完成后，运行以下命令验证：

```bash
# 测试数据库连接
python test_mysql_database.py

# 启动Web应用
python run_web_app.py --port 8443 --no-ssl
```

## 常见问题解决

### 1. 连接被拒绝
```
Error: (2003, "Can't connect to MySQL server")
```
**解决**: 确保MySQL服务正在运行
```bash
brew services start mysql
```

### 2. 认证失败
```
Error: (1045, "Access denied for user")
```
**解决**: 检查用户名和密码
```bash
mysql -u root -p
```

### 3. 数据库不存在
```
Error: (1049, "Unknown database")
```
**解决**: 运行初始化脚本
```bash
python setup_mysql.py
```

## 配置检查

确保您的数据库配置正确：

1. 检查 `src/db_config.py` 中的配置
2. 确认MySQL服务正在运行
3. 验证端口3306是否可用

## 快速测试

运行以下命令快速测试：

```bash
# 1. 检查MySQL是否运行
brew services list | grep mysql

# 2. 测试Python连接
python -c "
import pymysql
try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='starunion',
        charset='utf8mb4'
    )
    print('MySQL连接成功!')
    conn.close()
except Exception as e:
    print(f'MySQL连接失败: {e}')
"

# 3. 运行数据库测试
python test_mysql_database.py
```

## 下一步

安装完成后：
1. 运行 `python setup_mysql.py` 初始化数据库
2. 运行 `python test_mysql_database.py` 测试功能
3. 运行 `python run_web_app.py --port 8443 --no-ssl` 启动Web应用
4. 访问 http://localhost:8443 开始使用

## 技术支持

如果仍然遇到问题，请：
1. 检查错误日志
2. 确认MySQL服务状态
3. 验证网络连接
4. 检查防火墙设置 