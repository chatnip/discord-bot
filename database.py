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

# ---------------------------------------
# 1. 초기 테이블 생성 파트
# ---------------------------------------
# try:
#     db_config = get_db_config()
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()

#     cursor.execute('''
#         CREATE TABLE users (
#             id VARCHAR(255) PRIMARY KEY,
#             name VARCHAR(255),
#             house VARCHAR(50) DEFAULT NULL,
#             personality VARCHAR(100) DEFAULT NULL,
#             strength INT DEFAULT 50,
#             constitution INT DEFAULT 50,
#             size INT DEFAULT 50,
#             intelligence INT DEFAULT 50,
#             willpower INT DEFAULT 50,
#             dexterity INT DEFAULT 50,
#             appearance INT DEFAULT 50,
#             education INT DEFAULT 50
#         )
#     ''')
#     conn.commit()
#     print("✅ 새로운 users 테이블 생성 완료!")

# except Exception as e:
#     print(f"❌ MySQL 오류 발생: {e}")

# finally:
#     cursor.close()
#     conn.close()
#     print("🔌 MySQL 연결 종료")


# ---------------------------------------
# 2. 데이터베이스 함수 파트
# ---------------------------------------
def get_user(user_id):
    """유저 정보 조회"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result  # 유저가 없다면 None 반환
    except mysql.connector.Error as e:
        print(f"❌ 유저 조회 실패: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def register_user(user_id, user_name):
    """유저 등록"""
    try:
        db_config = get_db_config()  # DB 설정 불러오기
        conn = mysql.connector.connect(**db_config)  # 새로운 DB 연결
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (id, name, house, personality, strength, constitution, size, intelligence, willpower, dexterity, appearance, education) "
            "VALUES (%s, %s, NULL, NULL, 50, 50, 50, 50, 50, 50, 50, 50)",
            (user_id, user_name)
        )
        conn.commit()
        print(f"✅ 유저 등록 완료: {user_id} - {user_name}")

    except mysql.connector.Error as e:
        print(f"❌ 유저 등록 실패: {e}")

    finally:
        cursor.close()
        conn.close()


def update_user_name(user_id, new_name):
    """유저 이름 변경"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"❌ 이름 변경 실패: {e}")
    finally:
        cursor.close()
        conn.close()

def update_user_size(user_id, new_size):
    """유저가 크기(size) 값을 변경"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET size = %s WHERE id = %s", (new_size, user_id))
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 크기(size) 변경 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def update_user_appearance(user_id, new_appearance):
    """유저가 외모(appearance) 값을 변경"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET appearance = %s WHERE id = %s", (new_appearance, user_id))
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 외모(appearance) 변경 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()



def update_user_house(user_id, house):
    """유저가 기숙사를 선택하면 해당 기숙사의 능력치를 반영"""
    if house not in HOUSE_STATS:
        return False  # 잘못된 기숙사 입력

    stats = HOUSE_STATS[house]

    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET house = %s,
                strength = COALESCE(strength, 0) + %s,
                constitution = COALESCE(constitution, 0) + %s,
                size = COALESCE(size, 0) + %s,
                intelligence = COALESCE(intelligence, 0) + %s,
                willpower = COALESCE(willpower, 0) + %s,
                dexterity = COALESCE(dexterity, 0) + %s
            WHERE id = %s
            """,
            (
                house,
                stats["strength"],
                stats["constitution"],
                stats["size"],
                stats["intelligence"],
                stats["willpower"],
                stats["dexterity"],
                user_id,
            )
        )
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 기숙사 업데이트 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def update_user_personality(user_id, personality):
    """유저가 성격을 선택하면 해당 성격의 능력치를 반영"""
    if personality not in PERSONALITY_STATS:
        return False  # 잘못된 성격 입력

    stats = PERSONALITY_STATS[personality]

    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET personality = %s,
                strength = COALESCE(strength, 0) + %s,
                constitution = COALESCE(constitution, 0) + %s,
                size = COALESCE(size, 0) + %s,
                intelligence = COALESCE(intelligence, 0) + %s,
                willpower = COALESCE(willpower, 0) + %s,
                dexterity = COALESCE(dexterity, 0) + %s
            WHERE id = %s
            """,
            (
                personality,
                stats["strength"],
                stats["constitution"],
                stats["size"],
                stats["intelligence"],
                stats["willpower"],
                stats["dexterity"],
                user_id,
            )
        )
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 성격 업데이트 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------
# 3. 스탯 딕셔너리들
# ---------------------------------------
HOUSE_STATS = {
    "그리핀도르": {
        "strength": 10,
        "constitution": 0,
        "size": 0,
        "intelligence": -5,
        "willpower": 5,
        "dexterity": 0
    },
    "슬리데린": {
        "strength": 0,
        "constitution": 0,
        "size": 0,
        "intelligence": 10,
        "willpower": -5,
        "dexterity": 0
    },
    "래번클로": {
        "strength": -5,
        "constitution": 0,
        "size": 0,
        "intelligence": 10,
        "willpower": 0,
        "dexterity": -5
    },
    "후플푸프": {
        "strength": 0,
        "constitution": 10,
        "size": 0,
        "intelligence": 0,
        "willpower": -5,
        "dexterity": -5
    }
}

HOUSE_ROLES = {
    "그리핀도르": 1342843501645135933,
    "슬리데린": 1342843439578087445,
    "래번클로": 1342843569668489268,
    "후플푸프": 1342843627637968976
}

PERSONALITY_STATS = {
    "대담한":     {"strength": 15,  "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 10,  "dexterity": 0},
    "신중한":     {"strength": -10, "constitution": 10, "size": 0,  "intelligence": 15,  "willpower": -10, "dexterity": 0},
    "정확한":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": 10,  "willpower": 10,  "dexterity": -15},
    "용감한":     {"strength": 10,  "constitution": 10, "size": 0,  "intelligence": 0,   "willpower": 0,   "dexterity": -10},
    "냉정한":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 15,  "dexterity": -5},
    "활발한":     {"strength": 0,   "constitution": -10,"size": 0,  "intelligence": 0,   "willpower": 0,   "dexterity": 15},
    "지적인":     {"strength": -10, "constitution": 0,  "size": 0,  "intelligence": 15,  "willpower": 0,   "dexterity": -10},
    "온화한":     {"strength": 0,   "constitution": 10, "size": 0,  "intelligence": 0,   "willpower": 10,  "dexterity": -15},
    "신뢰감":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": 10,  "willpower": -10, "dexterity": 10},
    "자립적":     {"strength": 10,  "constitution": -10,"size": 0,  "intelligence": 0,   "willpower": 0,   "dexterity": 0},
    "논리적":     {"strength": -10, "constitution": 0,  "size": 0,  "intelligence": 15,  "willpower": 0,   "dexterity": -10},
    "감성적":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 10,  "dexterity": 10},
    "차분한":     {"strength": 0,   "constitution": 10, "size": 0,  "intelligence": 0,   "willpower": 10,  "dexterity": -15},
    "유연한":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": 10,  "willpower": 0,   "dexterity": 10},
    "책임감":     {"strength": 10,  "constitution": 10, "size": 0,  "intelligence": -10, "willpower": 0,   "dexterity": -10},
    "집중력":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": 15,  "willpower": -10, "dexterity": -10},
    "유머감":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 10,  "dexterity": 10},
    "도전적":     {"strength": 10,  "constitution": 0,  "size": 0,  "intelligence": 0,   "willpower": 10,  "dexterity": -10},
    "사교적":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 0,   "dexterity": 15},
    "직관적":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 10,  "dexterity": 10},
    "도덕적":     {"strength": -10, "constitution": 10, "size": 0,  "intelligence": 10,  "willpower": 0,   "dexterity": -10},
    "공감형":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 10,  "dexterity": 10},
    "완벽한":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": 10,  "willpower": -10, "dexterity": 10},
    "적극적":     {"strength": 10,  "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 0,   "dexterity": 10},
    "성실한":     {"strength": 10,  "constitution": 10, "size": 0,  "intelligence": 0,   "willpower": 0,   "dexterity": -15},
    "즉흥적":     {"strength": 0,   "constitution": -10,"size": 0,  "intelligence": -10, "willpower": 0,   "dexterity": 15},
    "긍정적":     {"strength": 0,   "constitution": 0,  "size": 0,  "intelligence": -10, "willpower": 10,  "dexterity": 10},
    "창의적":     {"strength": -10, "constitution": 0,  "size": 0,  "intelligence": 15,  "willpower": 0,   "dexterity": -10},
    "조용한":     {"strength": 0,   "constitution": 10, "size": 0,  "intelligence": 0,   "willpower": 10,  "dexterity": -15}
}
