import os
import urllib.parse
import mysql.connector
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# DATABASE_URL을 안전하게 분석하는 함수
def get_db_config():
    if not DATABASE_URL:
        raise ValueError("❌ ERROR: DATABASE_URL 환경 변수가 설정되지 않았습니다.")

    url = urllib.parse.urlparse(DATABASE_URL)

    return {
        "host": url.hostname,
        "user": url.username,
        "password": url.password,
        "database": url.path.lstrip("/"),
        "port": url.port or 3306  # 포트가 없으면 기본값(3306) 사용
    }

# MySQL 연결
try:
    db_config = get_db_config()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 유저 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255)
        )
    ''')
    conn.commit()
    print("✅ MySQL 데이터베이스 연결 성공!")
except Exception as e:
    print(f"❌ MySQL 연결 실패: {e}")
    exit(1)  # 프로그램 종료

# 데이터베이스 함수
def get_user(user_id):
    """유저 정보 조회"""
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

def register_user(user_id, user_name):
    """유저 등록"""
    cursor.execute("INSERT INTO users (id, name) VALUES (%s, %s)", (user_id, user_name))
    conn.commit()

def update_user_name(user_id, new_name):
    """유저 이름 변경"""
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    conn.commit()
