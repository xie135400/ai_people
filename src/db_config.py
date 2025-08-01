#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库配置文件
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """数据库配置类"""
    
    # 默认MySQL配置
    DEFAULT_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'starunion',
        'database': 'ai_people_analytics',
        'charset': 'utf8mb4',
        'autocommit': True,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        获取数据库配置
        
        优先级：
        1. 环境变量
        2. 配置文件
        3. 默认配置
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        # 从环境变量读取配置
        env_mapping = {
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_USER': 'user',
            'DB_PASSWORD': 'password',
            'DB_NAME': 'database',
            'DB_CHARSET': 'charset'
        }
        
        for env_key, config_key in env_mapping.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                if config_key == 'port':
                    config[config_key] = int(env_value)
                else:
                    config[config_key] = env_value
        
        return config
    
    @classmethod
    def get_connection_string(cls) -> str:
        """获取数据库连接字符串"""
        config = cls.get_config()
        return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
    
    @classmethod
    def get_pymysql_config(cls) -> Dict[str, Any]:
        """获取PyMySQL配置"""
        config = cls.get_config()
        return {
            'host': config['host'],
            'port': config['port'],
            'user': config['user'],
            'password': config['password'],
            'database': config['database'],
            'charset': config['charset'],
            'autocommit': config['autocommit']
        } 