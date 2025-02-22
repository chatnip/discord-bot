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

    # 유저 테이블 생성 (기숙사 및 성격 포함)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            house VARCHAR(50) DEFAULT NULL,
            personality VARCHAR(100) DEFAULT NULL,
            strength INT DEFAULT 50,
            constitution INT DEFAULT 50,
            size INT DEFAULT 50,
            intelligence INT DEFAULT 50,
            willpower INT DEFAULT 50,
            dexterity INT DEFAULT 50,
            appearance INT DEFAULT 50,
            education INT DEFAULT 50
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
    result = cursor.fetchone()
    if not result:
        return None  # 유저가 없는 경우 None 반환
    return result

def register_user(user_id, user_name):
    """유저 등록"""
    cursor.execute("INSERT INTO users (id, name, house, personality) VALUES (%s, %s, NULL, NULL)", (user_id, user_name))
    conn.commit()

def update_user_name(user_id, new_name):
    """유저 이름 변경"""
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    conn.commit()

def update_user_house(user_id, house):
    """유저가 기숙사를 선택하면 해당 기숙사의 능력치를 반영"""
    house = house.capitalize()
    if house not in HOUSE_STATS.keys():
        return False  # 잘못된 기숙사 입력

    stats = HOUSE_STATS[house]

    cursor.execute("""
        UPDATE users SET house = %s, STR = STR + %s, CON = CON + %s, 
        SIZ = SIZ + %s, INT = INT + %s, POW = POW + %s, DEX = DEX + %s WHERE id = %s
    """, (house, stats["STR"], stats["CON"], stats["SIZ"], stats["INT"], stats["POW"], stats["DEX"], user_id))
    conn.commit()
    return cursor.rowcount > 0  # 업데이트 성공 여부 반환

def update_user_personality(user_id, personality):
    """유저가 성격을 선택하면 해당 성격의 능력치를 반영"""
    personality = personality.capitalize()
    if personality not in PERSONALITY_STATS.keys():
        return False  # 잘못된 성격 입력

    stats = PERSONALITY_STATS[personality]

    cursor.execute("""
        UPDATE users SET personality = %s, STR = STR + %s, CON = CON + %s, 
        SIZ = SIZ + %s, INT = INT + %s, POW = POW + %s, DEX = DEX + %s WHERE id = %s
    """, (personality, stats["STR"], stats["CON"], stats["SIZ"], stats["INT"], stats["POW"], stats["DEX"], user_id))
    conn.commit()
    return cursor.rowcount > 0  # 업데이트 성공 여부 반환




HOUSE_STATS = {
    "그리핀도르": {"STR": 10, "CON": 0, "SIZ": 0, "INT": -5, "POW": 5, "DEX": 0},
    "슬리데린": {"STR": 0, "CON": 0, "SIZ": 0, "INT": 10, "POW": -5, "DEX": 0},
    "래번클로": {"STR": -5, "CON": 0, "SIZ": 0, "INT": 10, "POW": 0, "DEX": -5},
    "후플푸프": {"STR": 0, "CON": 10, "SIZ": 0, "INT": 0, "POW": -5, "DEX": -5}
}

PERSONALITY_STATS = {
    "대담한": {"STR": 15, "CON": 0, "SIZ": 0, "INT": -10, "POW": 10, "DEX": 0},
    "신중한": {"STR": -10, "CON": 10, "SIZ": 0, "INT": 15, "POW": -10, "DEX": 0},
    "정확한": {"STR": 0, "CON": 0, "SIZ": 0, "INT": 10, "POW": 10, "DEX": -15},
    "용감한": {"STR": 10, "CON": 10, "SIZ": 0, "INT": 0, "POW": 0, "DEX": -10},
    "냉정한": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 15, "DEX": -5},
    "활발한": {"STR": 0, "CON": -10, "SIZ": 0, "INT": 0, "POW": 0, "DEX": 15},
    "지적인": {"STR": -10, "CON": 0, "SIZ": 0, "INT": 15, "POW": 0, "DEX": -10},
    "온화한": {"STR": 0, "CON": 10, "SIZ": 0, "INT": 0, "POW": 10, "DEX": -15},
    "신뢰감": {"STR": 0, "CON": 0, "SIZ": 0, "INT": 10, "POW": -10, "DEX": 10},
    "자립적": {"STR": 10, "CON": -10, "SIZ": 0, "INT": 0, "POW": 0, "DEX": 0},
    "논리적": {"STR": -10, "CON": 0, "SIZ": 0, "INT": 15, "POW": 0, "DEX": -10},
    "감성적": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 10, "DEX": 10},
    "차분한": {"STR": 0, "CON": 10, "SIZ": 0, "INT": 0, "POW": 10, "DEX": -15},
    "유연한": {"STR": 0, "CON": 0, "SIZ": 0, "INT": 10, "POW": 0, "DEX": 10},
    "책임감": {"STR": 10, "CON": 10, "SIZ": 0, "INT": -10, "POW": 0, "DEX": -10},
    "집중력": {"STR": 0, "CON": 0, "SIZ": 0, "INT": 15, "POW": -10, "DEX": -10},
    "유머감": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 10, "DEX": 10},
    "도전적": {"STR": 10, "CON": 0, "SIZ": 0, "INT": 0, "POW": 10, "DEX": -10},
    "사교적": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 0, "DEX": 15},
    "직관적": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 10, "DEX": 10},
    "도덕적": {"STR": -10, "CON": 10, "SIZ": 0, "INT": 10, "POW": 0, "DEX": -10},
    "공감형": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 10, "DEX": 10},
    "완벽한": {"STR": 0, "CON": 0, "SIZ": 0, "INT": 10, "POW": -10, "DEX": 10},
    "적극적": {"STR": 10, "CON": 0, "SIZ": 0, "INT": -10, "POW": 0, "DEX": 10},
    "성실한": {"STR": 10, "CON": 10, "SIZ": 0, "INT": 0, "POW": 0, "DEX": -15},
    "즉흥적": {"STR": 0, "CON": -10, "SIZ": 0, "INT": -10, "POW": 0, "DEX": 15},
    "긍정적": {"STR": 0, "CON": 0, "SIZ": 0, "INT": -10, "POW": 10, "DEX": 10},
    "창의적": {"STR": -10, "CON": 0, "SIZ": 0, "INT": 15, "POW": 0, "DEX": -10},
    "조용한": {"STR": 0, "CON": 10, "SIZ": 0, "INT": 0, "POW": 10, "DEX": -15}
}