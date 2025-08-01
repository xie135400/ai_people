#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块
设计数据表结构和数据访问接口
"""

import pymysql
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import os
from contextlib import contextmanager

from db_config import DatabaseConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonRecord:
    """人员记录数据类"""
    id: Optional[int] = None
    track_id: int = 0
    first_seen: datetime = None
    last_seen: datetime = None
    total_frames: int = 0
    faces_detected: int = 0
    avg_age: Optional[float] = None
    dominant_gender: Optional[str] = None
    gender_confidence: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class PositionRecord:
    """位置记录数据类"""
    id: Optional[int] = None
    person_id: int = 0
    x: int = 0
    y: int = 0
    timestamp: datetime = None
    frame_number: int = 0

@dataclass
class FaceRecord:
    """人脸记录数据类"""
    id: Optional[int] = None
    person_id: int = 0
    age: Optional[int] = None
    gender: Optional[str] = None
    gender_confidence: float = 0.0
    bbox_x1: int = 0
    bbox_y1: int = 0
    bbox_x2: int = 0
    bbox_y2: int = 0
    confidence: float = 0.0
    timestamp: datetime = None

@dataclass
class SessionRecord:
    """会话记录数据类"""
    id: Optional[int] = None
    session_name: str = ""
    start_time: datetime = None
    end_time: Optional[datetime] = None
    total_people: int = 0
    total_frames: int = 0
    avg_age: Optional[float] = None
    male_count: int = 0
    female_count: int = 0
    notes: Optional[str] = None

@dataclass
class AnalysisRecord:
    """分析记录数据类"""
    id: Optional[int] = None
    session_id: int = 0
    record_name: str = ""
    timestamp: datetime = None
    total_people: int = 0
    active_tracks: int = 0
    avg_age: Optional[float] = None
    male_count: int = 0
    female_count: int = 0
    avg_dwell_time: float = 0.0
    engagement_score: float = 0.0
    shopper_count: int = 0
    browser_count: int = 0
    zone_data: str = ""  # JSON格式的区域数据
    additional_data: str = ""  # JSON格式的附加数据

class DatabaseManager:
    """MySQL数据库管理器"""
    
    def __init__(self, db_config: Dict[str, Any] = None):
        """
        初始化数据库管理器
        
        Args:
            db_config: 数据库配置字典，如果为None则使用默认配置
        """
        self.db_config = db_config or DatabaseConfig.get_pymysql_config()
        self._init_database()
        logger.info(f"MySQL数据库初始化完成: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            yield conn
        except Exception as e:
            logger.error(f"数据库连接错误: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {self.db_config['database']}")
            
            # 设置SQL模式以兼容MySQL 5.7+
            cursor.execute("SET sql_mode = 'NO_ENGINE_SUBSTITUTION'")
            
            # 创建表
            self._create_tables(cursor)
            conn.commit()
    
    def _create_tables(self, cursor):
        """创建数据表"""
        # 会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_name VARCHAR(255) NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NULL,
                total_people INT DEFAULT 0,
                total_frames INT DEFAULT 0,
                avg_age DECIMAL(5,2) NULL,
                male_count INT DEFAULT 0,
                female_count INT DEFAULT 0,
                notes TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 人员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                track_id INT NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                total_frames INT DEFAULT 0,
                faces_detected INT DEFAULT 0,
                avg_age DECIMAL(5,2) NULL,
                dominant_gender VARCHAR(10) NULL,
                gender_confidence DECIMAL(5,4) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
                INDEX idx_session_id (session_id),
                INDEX idx_track_id (track_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 位置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                person_id INT NOT NULL,
                x INT NOT NULL,
                y INT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                frame_number INT NOT NULL,
                FOREIGN KEY (person_id) REFERENCES persons (id) ON DELETE CASCADE,
                INDEX idx_person_id (person_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 人脸表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INT AUTO_INCREMENT PRIMARY KEY,
                person_id INT NOT NULL,
                age INT NULL,
                gender VARCHAR(10) NULL,
                gender_confidence DECIMAL(5,4) DEFAULT 0.0,
                bbox_x1 INT NOT NULL,
                bbox_y1 INT NOT NULL,
                bbox_x2 INT NOT NULL,
                bbox_y2 INT NOT NULL,
                confidence DECIMAL(5,4) DEFAULT 0.0,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (person_id) REFERENCES persons (id) ON DELETE CASCADE,
                INDEX idx_person_id (person_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 分析记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                record_name VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                total_people INT DEFAULT 0,
                active_tracks INT DEFAULT 0,
                avg_age DECIMAL(5,2) NULL,
                male_count INT DEFAULT 0,
                female_count INT DEFAULT 0,
                avg_dwell_time DECIMAL(10,2) DEFAULT 0.0,
                engagement_score DECIMAL(5,4) DEFAULT 0.0,
                shopper_count INT DEFAULT 0,
                browser_count INT DEFAULT 0,
                zone_data JSON NULL,
                additional_data JSON NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
                INDEX idx_session_id (session_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        logger.info("MySQL数据表创建完成")
    
    def create_session(self, session_name: str) -> int:
        """
        创建新会话
        
        Args:
            session_name: 会话名称
            
        Returns:
            会话ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_name, start_time)
                VALUES (%s, %s)
            ''', (session_name, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def end_session(self, session_id: int, stats: Dict):
        """
        结束会话
        
        Args:
            session_id: 会话ID
            stats: 会话统计信息
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sessions 
                SET end_time = %s, total_people = %s, total_frames = %s,
                    avg_age = %s, male_count = %s, female_count = %s
                WHERE id = %s
            ''', (
                datetime.now(),
                stats.get('total_people', 0),
                stats.get('total_frames', 0),
                stats.get('avg_age'),
                stats.get('male_count', 0),
                stats.get('female_count', 0),
                session_id
            ))
            conn.commit()
    
    def save_person(self, session_id: int, person_data: Dict) -> int:
        """
        保存人员记录
        
        Args:
            session_id: 会话ID
            person_data: 人员数据
            
        Returns:
            人员记录ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO persons (
                    session_id, track_id, first_seen, last_seen, total_frames,
                    faces_detected, avg_age, dominant_gender, gender_confidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                session_id,
                person_data['track_id'],
                person_data['first_seen'],
                person_data['last_seen'],
                person_data.get('total_frames', 0),
                person_data.get('faces_detected', 0),
                person_data.get('avg_age'),
                person_data.get('dominant_gender'),
                person_data.get('gender_confidence', 0.0)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_position(self, person_id: int, x: int, y: int, timestamp: datetime, frame_number: int):
        """
        保存位置记录
        
        Args:
            person_id: 人员ID
            x: X坐标
            y: Y坐标
            timestamp: 时间戳
            frame_number: 帧号
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO positions (person_id, x, y, timestamp, frame_number)
                VALUES (%s, %s, %s, %s, %s)
            ''', (person_id, x, y, timestamp, frame_number))
            conn.commit()
    
    def save_face(self, person_id: int, face_data: Dict):
        """
        保存人脸记录
        
        Args:
            person_id: 人员ID
            face_data: 人脸数据
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO faces (
                    person_id, age, gender, gender_confidence,
                    bbox_x1, bbox_y1, bbox_x2, bbox_y2, confidence, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                person_id,
                face_data.get('age'),
                face_data.get('gender'),
                face_data.get('gender_confidence', 0.0),
                face_data['bbox'][0],
                face_data['bbox'][1],
                face_data['bbox'][2],
                face_data['bbox'][3],
                face_data.get('confidence', 0.0),
                face_data.get('timestamp', datetime.now())
            ))
            conn.commit()
    
    def save_analysis_record(self, record_data: Dict) -> int:
        """
        保存分析记录
        
        Args:
            record_data: 分析记录数据
            
        Returns:
            记录ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_records (
                    session_id, record_name, timestamp, total_people, active_tracks,
                    avg_age, male_count, female_count, avg_dwell_time, engagement_score,
                    shopper_count, browser_count, zone_data, additional_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                record_data['session_id'],
                record_data['record_name'],
                record_data['timestamp'],
                record_data.get('total_people', 0),
                record_data.get('active_tracks', 0),
                record_data.get('avg_age'),
                record_data.get('male_count', 0),
                record_data.get('female_count', 0),
                record_data.get('avg_dwell_time', 0.0),
                record_data.get('engagement_score', 0.0),
                record_data.get('shopper_count', 0),
                record_data.get('browser_count', 0),
                json.dumps(record_data.get('zone_data', {})) if record_data.get('zone_data') else None,
                json.dumps(record_data.get('additional_data', {})) if record_data.get('additional_data') else None
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_sessions(self, limit: int = 50) -> List[Dict]:
        """
        获取会话列表
        
        Args:
            limit: 限制数量
            
        Returns:
            会话列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM sessions 
                ORDER BY created_at DESC 
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
    
    def get_session_persons(self, session_id: int) -> List[Dict]:
        """
        获取会话的人员列表
        
        Args:
            session_id: 会话ID
            
        Returns:
            人员列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM persons 
                WHERE session_id = %s 
                ORDER BY created_at DESC
            ''', (session_id,))
            return cursor.fetchall()
    
    def get_person_positions(self, person_id: int) -> List[Dict]:
        """
        获取人员位置记录
        
        Args:
            person_id: 人员ID
            
        Returns:
            位置记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM positions 
                WHERE person_id = %s 
                ORDER BY timestamp ASC
            ''', (person_id,))
            return cursor.fetchall()
    
    def get_person_faces(self, person_id: int) -> List[Dict]:
        """
        获取人员人脸记录
        
        Args:
            person_id: 人员ID
            
        Returns:
            人脸记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM faces 
                WHERE person_id = %s 
                ORDER BY timestamp ASC
            ''', (person_id,))
            return cursor.fetchall()
    
    def get_analysis_records(self, session_id: int, limit: int = 100) -> List[Dict]:
        """
        获取分析记录
        
        Args:
            session_id: 会话ID
            limit: 限制数量
            
        Returns:
            分析记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM analysis_records 
                WHERE session_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            ''', (session_id, limit))
            records = cursor.fetchall()
            
            # 解析JSON字段
            for record in records:
                if record.get('zone_data'):
                    try:
                        record['zone_data'] = json.loads(record['zone_data'])
                    except:
                        record['zone_data'] = {}
                if record.get('additional_data'):
                    try:
                        record['additional_data'] = json.loads(record['additional_data'])
                    except:
                        record['additional_data'] = {}
            
            return records
    
    def get_analysis_record(self, record_id: int) -> Optional[Dict]:
        """
        获取单个分析记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            分析记录
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM analysis_records 
                WHERE id = %s
            ''', (record_id,))
            record = cursor.fetchone()
            
            if record:
                # 解析JSON字段
                if record.get('zone_data'):
                    try:
                        record['zone_data'] = json.loads(record['zone_data'])
                    except:
                        record['zone_data'] = {}
                if record.get('additional_data'):
                    try:
                        record['additional_data'] = json.loads(record['additional_data'])
                    except:
                        record['additional_data'] = {}
            
            return record
    
    def get_session_statistics(self, session_id: int) -> Dict:
        """
        获取会话统计信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            统计信息
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 获取会话基本信息
            cursor.execute('''
                SELECT * FROM sessions WHERE id = %s
            ''', (session_id,))
            session = cursor.fetchone()
            
            if not session:
                return {}
            
            # 获取人员统计
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_persons,
                    AVG(avg_age) as avg_age,
                    SUM(CASE WHEN dominant_gender = 'male' THEN 1 ELSE 0 END) as male_count,
                    SUM(CASE WHEN dominant_gender = 'female' THEN 1 ELSE 0 END) as female_count,
                    AVG(total_frames) as avg_frames_per_person
                FROM persons 
                WHERE session_id = %s
            ''', (session_id,))
            person_stats = cursor.fetchone()
            
            # 获取位置统计
            cursor.execute('''
                SELECT COUNT(*) as total_positions
                FROM positions p
                JOIN persons per ON p.person_id = per.id
                WHERE per.session_id = %s
            ''', (session_id,))
            position_stats = cursor.fetchone()
            
            # 获取人脸统计
            cursor.execute('''
                SELECT COUNT(*) as total_faces
                FROM faces f
                JOIN persons p ON f.person_id = p.id
                WHERE p.session_id = %s
            ''', (session_id,))
            face_stats = cursor.fetchone()
            
            return {
                'session': session,
                'person_stats': person_stats,
                'position_stats': position_stats,
                'face_stats': face_stats
            }
    
    def get_all_analysis_records(self, limit: int = 100):
        """
        获取所有分析记录
        
        Args:
            limit: 限制数量
            
        Returns:
            分析记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('''
                SELECT ar.*, s.session_name
                FROM analysis_records ar
                JOIN sessions s ON ar.session_id = s.id
                ORDER BY ar.timestamp DESC 
                LIMIT %s
            ''', (limit,))
            records = cursor.fetchall()
            
            # 解析JSON字段
            for record in records:
                if record.get('zone_data'):
                    try:
                        record['zone_data'] = json.loads(record['zone_data'])
                    except:
                        record['zone_data'] = {}
                if record.get('additional_data'):
                    try:
                        record['additional_data'] = json.loads(record['additional_data'])
                    except:
                        record['additional_data'] = {}
            
            return records
    
    def cleanup_old_data(self, days: int = 30):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 删除旧的分析记录
            cursor.execute('''
                DELETE FROM analysis_records 
                WHERE created_at < %s
            ''', (cutoff_date,))
            
            # 删除旧的位置记录
            cursor.execute('''
                DELETE FROM positions 
                WHERE timestamp < %s
            ''', (cutoff_date,))
            
            # 删除旧的人脸记录
            cursor.execute('''
                DELETE FROM faces 
                WHERE timestamp < %s
            ''', (cutoff_date,))
            
            # 删除旧的人员记录
            cursor.execute('''
                DELETE FROM persons 
                WHERE created_at < %s
            ''', (cutoff_date,))
            
            # 删除旧的会话记录
            cursor.execute('''
                DELETE FROM sessions 
                WHERE created_at < %s
            ''', (cutoff_date,))
            
            conn.commit()
            logger.info(f"清理了{days}天前的数据")
    
    def close(self):
        """关闭数据库连接"""
        # MySQL连接会在上下文管理器中自动关闭
        pass

def test_database():
    """测试数据库功能"""
    try:
        db = DatabaseManager()
        logger.info("数据库连接测试成功")
        
        # 测试创建会话
        session_id = db.create_session("测试会话")
        logger.info(f"创建会话成功，ID: {session_id}")
        
        # 测试保存人员
        person_data = {
            'track_id': 1,
            'first_seen': datetime.now(),
            'last_seen': datetime.now(),
            'total_frames': 100,
            'faces_detected': 10,
            'avg_age': 25.5,
            'dominant_gender': 'male',
            'gender_confidence': 0.8
        }
        person_id = db.save_person(session_id, person_data)
        logger.info(f"保存人员成功，ID: {person_id}")
        
        # 测试获取会话
        sessions = db.get_sessions()
        logger.info(f"获取会话列表成功，数量: {len(sessions)}")
        
        logger.info("数据库测试完成")
        
    except Exception as e:
        logger.error(f"数据库测试失败: {e}")
        raise

if __name__ == "__main__":
    test_database() 