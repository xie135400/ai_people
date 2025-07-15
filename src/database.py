#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块
设计数据表结构和数据访问接口
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import os

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
    """数据库管理器"""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_database()
        logger.info(f"数据库初始化完成: {db_path}")
    
    def _init_database(self):
        """初始化数据库表结构"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        
        # 创建表
        self._create_tables()
    
    def _create_tables(self):
        """创建数据表"""
        cursor = self.conn.cursor()
        
        # 会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                total_people INTEGER DEFAULT 0,
                total_frames INTEGER DEFAULT 0,
                avg_age REAL,
                male_count INTEGER DEFAULT 0,
                female_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 人员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                total_frames INTEGER DEFAULT 0,
                faces_detected INTEGER DEFAULT 0,
                avg_age REAL,
                dominant_gender TEXT,
                gender_confidence REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # 位置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                frame_number INTEGER NOT NULL,
                FOREIGN KEY (person_id) REFERENCES persons (id)
            )
        ''')
        
        # 人脸表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                age INTEGER,
                gender TEXT,
                gender_confidence REAL DEFAULT 0.0,
                bbox_x1 INTEGER NOT NULL,
                bbox_y1 INTEGER NOT NULL,
                bbox_x2 INTEGER NOT NULL,
                bbox_y2 INTEGER NOT NULL,
                confidence REAL DEFAULT 0.0,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (person_id) REFERENCES persons (id)
            )
        ''')
        
        # 分析记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                record_name TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                total_people INTEGER DEFAULT 0,
                active_tracks INTEGER DEFAULT 0,
                avg_age REAL,
                male_count INTEGER DEFAULT 0,
                female_count INTEGER DEFAULT 0,
                avg_dwell_time REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                shopper_count INTEGER DEFAULT 0,
                browser_count INTEGER DEFAULT 0,
                zone_data TEXT,
                additional_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_persons_session_id ON persons (session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_persons_track_id ON persons (track_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_positions_person_id ON positions (person_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_faces_person_id ON faces (person_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_positions_timestamp ON positions (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_faces_timestamp ON faces (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_records_session_id ON analysis_records (session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_records_timestamp ON analysis_records (timestamp)')
        
        self.conn.commit()
        logger.info("数据表创建完成")
    
    def create_session(self, session_name: str) -> int:
        """
        创建新会话
        
        Args:
            session_name: 会话名称
            
        Returns:
            会话ID
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_name, start_time)
            VALUES (?, ?)
        ''', (session_name, datetime.now()))
        
        session_id = cursor.lastrowid
        self.conn.commit()
        
        logger.info(f"创建新会话: {session_name} (ID: {session_id})")
        return session_id
    
    def end_session(self, session_id: int, stats: Dict):
        """
        结束会话并更新统计信息
        
        Args:
            session_id: 会话ID
            stats: 统计信息
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE sessions SET
                end_time = ?,
                total_people = ?,
                total_frames = ?,
                avg_age = ?,
                male_count = ?,
                female_count = ?
            WHERE id = ?
        ''', (
            datetime.now(),
            stats.get('total_people', 0),
            stats.get('frame_count', 0),
            stats.get('avg_age'),
            stats.get('male_count', 0),
            stats.get('female_count', 0),
            session_id
        ))
        
        self.conn.commit()
        logger.info(f"会话结束: {session_id}")
    
    def save_person(self, session_id: int, person_data: Dict) -> int:
        """
        保存人员信息
        
        Args:
            session_id: 会话ID
            person_data: 人员数据
            
        Returns:
            人员ID
        """
        cursor = self.conn.cursor()
        
        # 检查是否已存在该轨迹ID的人员
        cursor.execute('''
            SELECT id FROM persons 
            WHERE session_id = ? AND track_id = ?
        ''', (session_id, person_data['track_id']))
        
        result = cursor.fetchone()
        
        if result:
            # 更新现有人员
            person_id = result[0]
            cursor.execute('''
                UPDATE persons SET
                    last_seen = ?,
                    total_frames = ?,
                    faces_detected = ?,
                    avg_age = ?,
                    dominant_gender = ?,
                    gender_confidence = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (
                person_data['last_seen'],
                person_data['total_frames'],
                person_data['faces_detected'],
                person_data['avg_age'],
                person_data['dominant_gender'],
                person_data['gender_confidence'],
                datetime.now(),
                person_id
            ))
        else:
            # 创建新人员
            cursor.execute('''
                INSERT INTO persons (
                    session_id, track_id, first_seen, last_seen, 
                    total_frames, faces_detected, avg_age, 
                    dominant_gender, gender_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                person_data['track_id'],
                person_data['first_seen'],
                person_data['last_seen'],
                person_data['total_frames'],
                person_data['faces_detected'],
                person_data['avg_age'],
                person_data['dominant_gender'],
                person_data['gender_confidence']
            ))
            
            person_id = cursor.lastrowid
        
        self.conn.commit()
        return person_id
    
    def save_position(self, person_id: int, x: int, y: int, timestamp: datetime, frame_number: int):
        """
        保存位置信息
        
        Args:
            person_id: 人员ID
            x: X坐标
            y: Y坐标
            timestamp: 时间戳
            frame_number: 帧号
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO positions (person_id, x, y, timestamp, frame_number)
            VALUES (?, ?, ?, ?, ?)
        ''', (person_id, x, y, timestamp, frame_number))
        
        self.conn.commit()
    
    def save_face(self, person_id: int, face_data: Dict):
        """
        保存人脸信息
        
        Args:
            person_id: 人员ID
            face_data: 人脸数据
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO faces (
                person_id, age, gender, gender_confidence,
                bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                confidence, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            person_id,
            face_data['age'],
            face_data['gender'],
            face_data.get('gender_confidence', 0.0),
            face_data['bbox'][0],
            face_data['bbox'][1],
            face_data['bbox'][2],
            face_data['bbox'][3],
            face_data['confidence'],
            face_data['timestamp']
        ))
        
        self.conn.commit()
    
    def save_analysis_record(self, record_data: Dict) -> int:
        """
        保存分析记录
        
        Args:
            record_data: 分析记录数据
            
        Returns:
            记录ID
        """
        cursor = self.conn.cursor()
        
        # 将字典数据转换为JSON字符串
        zone_data = json.dumps(record_data.get('zone_data', {}), ensure_ascii=False)
        additional_data = json.dumps(record_data.get('additional_data', {}), ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO analysis_records (
                session_id, record_name, timestamp,
                total_people, active_tracks, avg_age,
                male_count, female_count, avg_dwell_time,
                engagement_score, shopper_count, browser_count,
                zone_data, additional_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_data['session_id'],
            record_data['record_name'],
            record_data.get('timestamp', datetime.now()),
            record_data.get('total_people', 0),
            record_data.get('active_tracks', 0),
            record_data.get('avg_age'),
            record_data.get('male_count', 0),
            record_data.get('female_count', 0),
            record_data.get('avg_dwell_time', 0.0),
            record_data.get('engagement_score', 0.0),
            record_data.get('shopper_count', 0),
            record_data.get('browser_count', 0),
            zone_data,
            additional_data
        ))
        
        record_id = cursor.lastrowid
        self.conn.commit()
        
        logger.info(f"创建分析记录: {record_data['record_name']} (ID: {record_id})")
        return record_id
    
    def get_sessions(self, limit: int = 50) -> List[Dict]:
        """
        获取会话列表
        
        Args:
            limit: 最大返回数量
            
        Returns:
            会话列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        ''', (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append(dict(row))
        
        return sessions
    
    def get_session_persons(self, session_id: int) -> List[Dict]:
        """
        获取会话中的人员列表
        
        Args:
            session_id: 会话ID
            
        Returns:
            人员列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM persons
            WHERE session_id = ?
            ORDER BY first_seen
        ''', (session_id,))
        
        persons = []
        for row in cursor.fetchall():
            persons.append(dict(row))
        
        return persons
    
    def get_person_positions(self, person_id: int) -> List[Dict]:
        """
        获取人员的位置历史
        
        Args:
            person_id: 人员ID
            
        Returns:
            位置列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM positions
            WHERE person_id = ?
            ORDER BY timestamp
        ''', (person_id,))
        
        positions = []
        for row in cursor.fetchall():
            positions.append(dict(row))
        
        return positions
    
    def get_person_faces(self, person_id: int) -> List[Dict]:
        """
        获取人员的人脸记录
        
        Args:
            person_id: 人员ID
            
        Returns:
            人脸列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM faces
            WHERE person_id = ?
            ORDER BY timestamp
        ''', (person_id,))
        
        faces = []
        for row in cursor.fetchall():
            faces.append(dict(row))
        
        return faces
    
    def get_analysis_records(self, session_id: int, limit: int = 100) -> List[Dict]:
        """
        获取会话的分析记录
        
        Args:
            session_id: 会话ID
            limit: 最大返回数量
            
        Returns:
            分析记录列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM analysis_records
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        records = []
        for row in cursor.fetchall():
            record = dict(row)
            # 解析JSON字段
            try:
                if record.get('zone_data'):
                    record['zone_data'] = json.loads(record['zone_data'])
                if record.get('additional_data'):
                    record['additional_data'] = json.loads(record['additional_data'])
            except json.JSONDecodeError:
                logger.warning(f"解析分析记录JSON数据失败: {record['id']}")
            
            records.append(record)
        
        return records
    
    def get_analysis_record(self, record_id: int) -> Optional[Dict]:
        """
        获取单个分析记录详情
        
        Args:
            record_id: 记录ID
            
        Returns:
            分析记录详情
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM analysis_records
            WHERE id = ?
        ''', (record_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        record = dict(row)
        # 解析JSON字段
        try:
            if record.get('zone_data'):
                record['zone_data'] = json.loads(record['zone_data'])
            if record.get('additional_data'):
                record['additional_data'] = json.loads(record['additional_data'])
        except json.JSONDecodeError:
            logger.warning(f"解析分析记录JSON数据失败: {record['id']}")
        
        return record
    
    def get_session_statistics(self, session_id: int) -> Dict:
        """
        获取会话统计信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            统计信息
        """
        cursor = self.conn.cursor()
        
        # 获取会话基本信息
        cursor.execute('''
            SELECT * FROM sessions
            WHERE id = ?
        ''', (session_id,))
        
        session = dict(cursor.fetchone() or {})
        
        # 获取人员数量
        cursor.execute('''
            SELECT COUNT(*) FROM persons
            WHERE session_id = ?
        ''', (session_id,))
        
        person_count = cursor.fetchone()[0]
        
        # 获取人脸数量
        cursor.execute('''
            SELECT COUNT(*) FROM faces
            WHERE person_id IN (SELECT id FROM persons WHERE session_id = ?)
        ''', (session_id,))
        
        face_count = cursor.fetchone()[0]
        
        # 获取位置数量
        cursor.execute('''
            SELECT COUNT(*) FROM positions
            WHERE person_id IN (SELECT id FROM persons WHERE session_id = ?)
        ''', (session_id,))
        
        position_count = cursor.fetchone()[0]
        
        # 获取分析记录数量
        cursor.execute('''
            SELECT COUNT(*) FROM analysis_records
            WHERE session_id = ?
        ''', (session_id,))
        
        record_count = cursor.fetchone()[0]
        
        # 组合统计信息
        stats = {
            'session_id': session_id,
            'session_name': session.get('session_name', '未知会话'),
            'start_time': session.get('start_time'),
            'end_time': session.get('end_time'),
            'duration': None,
            'total_people': session.get('total_people', 0),
            'total_frames': session.get('total_frames', 0),
            'avg_age': session.get('avg_age'),
            'male_count': session.get('male_count', 0),
            'female_count': session.get('female_count', 0),
            'person_count': person_count,
            'face_count': face_count,
            'position_count': position_count,
            'record_count': record_count
        }
        
        # 计算持续时间
        if stats['start_time'] and stats['end_time']:
            try:
                start = datetime.fromisoformat(stats['start_time'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(stats['end_time'].replace('Z', '+00:00'))
                stats['duration'] = (end - start).total_seconds()
            except (ValueError, TypeError):
                stats['duration'] = None
        
        return stats
    
    def cleanup_old_data(self, days: int = 30):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor = self.conn.cursor()
        
        # 获取旧会话ID
        cursor.execute('''
            SELECT id FROM sessions
            WHERE start_time < ?
        ''', (cutoff_date,))
        
        old_sessions = [row[0] for row in cursor.fetchall()]
        
        if not old_sessions:
            logger.info(f"没有找到{days}天前的旧数据")
            return
        
        logger.info(f"清理{len(old_sessions)}个旧会话数据")
        
        # 删除相关数据
        for session_id in old_sessions:
            # 获取会话中的人员ID
            cursor.execute('''
                SELECT id FROM persons
                WHERE session_id = ?
            ''', (session_id,))
            
            person_ids = [row[0] for row in cursor.fetchall()]
            
            # 删除人脸和位置数据
            for person_id in person_ids:
                cursor.execute('DELETE FROM faces WHERE person_id = ?', (person_id,))
                cursor.execute('DELETE FROM positions WHERE person_id = ?', (person_id,))
            
            # 删除人员数据
            cursor.execute('DELETE FROM persons WHERE session_id = ?', (session_id,))
            
            # 删除分析记录
            cursor.execute('DELETE FROM analysis_records WHERE session_id = ?', (session_id,))
            
            # 删除会话
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        
        self.conn.commit()
        logger.info(f"成功清理{len(old_sessions)}个旧会话数据")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

def test_database():
    """测试数据库功能"""
    db = DatabaseManager("data/test_analytics.db")
    
    # 创建会话
    session_id = db.create_session("测试会话")
    
    # 添加人员
    person_data = {
        'track_id': 1,
        'first_seen': datetime.now(),
        'last_seen': datetime.now(),
        'total_frames': 10,
        'faces_detected': 5,
        'avg_age': 30.5,
        'dominant_gender': 'Male',
        'gender_confidence': 0.85
    }
    person_id = db.save_person(session_id, person_data)
    
    # 添加位置
    db.save_position(person_id, 100, 200, datetime.now(), 1)
    
    # 添加人脸
    face_data = {
        'age': 31,
        'gender': 'Male',
        'gender_confidence': 0.9,
        'bbox': (50, 50, 100, 100),
        'confidence': 0.95,
        'timestamp': datetime.now()
    }
    db.save_face(person_id, face_data)
    
    # 添加分析记录
    record_data = {
        'session_id': session_id,
        'record_name': '测试记录',
        'timestamp': datetime.now(),
        'total_people': 5,
        'active_tracks': 3,
        'avg_age': 35.2,
        'male_count': 3,
        'female_count': 2,
        'avg_dwell_time': 45.5,
        'engagement_score': 0.75,
        'shopper_count': 2,
        'browser_count': 3,
        'zone_data': {'zone1': {'count': 2}, 'zone2': {'count': 3}},
        'additional_data': {'frame_rate': 25, 'processing_time': 0.05}
    }
    record_id = db.save_analysis_record(record_data)
    
    # 结束会话
    stats = {
        'total_people': 1,
        'frame_count': 10,
        'avg_age': 30.5,
        'male_count': 1,
        'female_count': 0
    }
    db.end_session(session_id, stats)
    
    # 查询数据
    print("会话:", db.get_sessions())
    print("人员:", db.get_session_persons(session_id))
    print("位置:", db.get_person_positions(person_id))
    print("人脸:", db.get_person_faces(person_id))
    print("分析记录:", db.get_analysis_records(session_id))
    print("统计:", db.get_session_statistics(session_id))
    
    # 关闭连接
    db.close()

if __name__ == "__main__":
    test_database() 