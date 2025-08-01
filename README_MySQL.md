# AI人流分析系统 - MySQL数据库配置

## 概述

本项目已从SQLite数据库迁移到MySQL数据库，提供更好的并发性能和数据管理能力。

## 系统要求

- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+
- 足够的磁盘空间用于存储分析数据

## 安装步骤

### 1. 安装MySQL数据库

#### macOS (使用Homebrew)
```bash
# 安装MySQL
brew install mysql

# 启动MySQL服务
brew services start mysql

# 设置root密码（首次安装）
mysql_secure_installation
```

#### Ubuntu/Debian
```bash
# 安装MySQL
sudo apt update
sudo apt install mysql-server

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 设置root密码
sudo mysql_secure_installation
```

#### CentOS/RHEL
```bash
# 安装MySQL
sudo yum install mysql-server

# 启动MySQL服务
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 设置root密码
sudo mysql_secure_installation
```

### 2. 安装Python依赖

```bash
# 安装项目依赖
pip install -r requirements.txt
```

### 3. 配置数据库

#### 方法1: 使用环境变量（推荐）

创建 `.env` 文件：
```bash
# 复制示例配置文件
cp env_example.txt .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中设置数据库配置：
```env
# MySQL数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_people_analytics
DB_CHARSET=utf8mb4
```

#### 方法2: 直接修改代码配置

编辑 `src/db_config.py` 文件中的 `DEFAULT_CONFIG`：
```python
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'ai_people_analytics',
    'charset': 'utf8mb4',
    # ... 其他配置
}
```

### 4. 初始化数据库

```bash
# 运行数据库初始化脚本
python setup_mysql.py
```

### 5. 测试数据库连接

```bash
# 运行数据库测试
python test_mysql_database.py
```

## 数据库结构

### 主要数据表

1. **sessions** - 会话表
   - 存储分析会话的基本信息
   - 包含开始时间、结束时间、统计信息等

2. **persons** - 人员表
   - 存储检测到的人员信息
   - 包含轨迹ID、年龄、性别等

3. **positions** - 位置表
   - 存储人员的位置轨迹
   - 包含坐标、时间戳等

4. **faces** - 人脸表
   - 存储人脸检测结果
   - 包含年龄、性别、置信度等

5. **analysis_records** - 分析记录表
   - 存储定期生成的分析记录
   - 包含统计数据和JSON格式的附加信息

### 索引优化

系统自动创建以下索引以提高查询性能：
- `idx_session_id` - 会话ID索引
- `idx_track_id` - 轨迹ID索引
- `idx_person_id` - 人员ID索引
- `idx_timestamp` - 时间戳索引

## 使用方法

### 启动Web应用

```bash
# 使用默认配置启动
python run_web_app.py

# 指定主机和端口
python run_web_app.py --host 0.0.0.0 --port 8000

# 禁用SSL（使用HTTP）
python run_web_app.py --no-ssl
```

### 数据库管理

#### 查看会话列表
```python
from src.database import DatabaseManager

db = DatabaseManager()
sessions = db.get_sessions(limit=10)
for session in sessions:
    print(f"会话: {session['session_name']}, 开始时间: {session['start_time']}")
```

#### 查看分析记录
```python
# 获取所有分析记录
records = db.get_all_analysis_records(limit=20)

# 获取特定会话的分析记录
session_records = db.get_analysis_records(session_id=1, limit=50)
```

#### 清理旧数据
```python
# 清理30天前的数据
db.cleanup_old_data(days=30)
```

## 性能优化

### 1. MySQL配置优化

在 `my.cnf` 或 `my.ini` 中添加以下配置：

```ini
[mysqld]
# 内存配置
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M

# 连接配置
max_connections = 200
max_connect_errors = 1000

# 查询缓存
query_cache_type = 1
query_cache_size = 128M

# 临时表配置
tmp_table_size = 64M
max_heap_table_size = 64M
```

### 2. 定期维护

```bash
# 创建维护脚本
cat > mysql_maintenance.sql << EOF
-- 优化表
OPTIMIZE TABLE sessions, persons, positions, faces, analysis_records;

-- 分析表统计信息
ANALYZE TABLE sessions, persons, positions, faces, analysis_records;
EOF

# 定期执行维护
mysql -u root -p ai_people_analytics < mysql_maintenance.sql
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   ```
   Error: (2003, "Can't connect to MySQL server")
   ```
   解决：检查MySQL服务是否启动，端口是否正确

2. **认证失败**
   ```
   Error: (1045, "Access denied for user")
   ```
   解决：检查用户名和密码是否正确

3. **数据库不存在**
   ```
   Error: (1049, "Unknown database")
   ```
   解决：运行 `python setup_mysql.py` 创建数据库

4. **字符集问题**
   ```
   Error: (1366, "Incorrect string value")
   ```
   解决：确保使用 `utf8mb4` 字符集

### 日志查看

```bash
# 查看MySQL错误日志
sudo tail -f /var/log/mysql/error.log

# 查看应用程序日志
tail -f logs/app.log
```

## 备份和恢复

### 备份数据库

```bash
# 创建备份
mysqldump -u root -p ai_people_analytics > backup_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
gzip backup_*.sql
```

### 恢复数据库

```bash
# 恢复备份
mysql -u root -p ai_people_analytics < backup_20240101_120000.sql
```

## 监控和维护

### 1. 数据库监控

```sql
-- 查看数据库大小
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'ai_people_analytics'
GROUP BY table_schema;

-- 查看表大小
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'ai_people_analytics'
ORDER BY (data_length + index_length) DESC;
```

### 2. 性能监控

```sql
-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;

-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';
```

## 迁移指南

### 从SQLite迁移到MySQL

如果您有现有的SQLite数据需要迁移：

1. 导出SQLite数据
2. 转换数据格式
3. 导入到MySQL
4. 验证数据完整性

详细的迁移脚本请参考 `migrate_sqlite_to_mysql.py`（如果存在）。

## 技术支持

如果遇到问题，请：

1. 检查日志文件
2. 运行测试脚本
3. 查看本文档的故障排除部分
4. 提交Issue到项目仓库

## 更新日志

- **v2.0.0** - 从SQLite迁移到MySQL
- **v2.0.1** - 添加数据库连接池
- **v2.0.2** - 优化查询性能
- **v2.0.3** - 添加数据清理功能 