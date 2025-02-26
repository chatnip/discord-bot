import os
import urllib.parse
import mysql.connector
import random
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
try:
    db_config = get_db_config()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN skill_point INT DEFAULT 0")
        print("✅ 완료!")
    except mysql.connector.Error as e:
        print(f"❌ 실패: {e}")

    conn.commit()

except Exception as e:
    print(f"❌ MySQL 오류 발생: {e}")

finally:
    cursor.close()
    conn.close()
    print("🔌 MySQL 연결 종료")


# ---------------------------------------
# 2. 데이터베이스 함수 파트
# ---------------------------------------
def get_user(user_id):
    """유저 정보 조회"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, name, house, personality, strength, constitution, size, intelligence, 
                   willpower, dexterity, appearance, education, money, luck, movement, damage_bonus, 
                   build, hp, mp, sanity, status 
            FROM users WHERE user_id = %s
        """, (user_id,))
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

        # 행운 주사위 굴리기
        luck_value = roll_luck()

        # 기본값 계산
        base_strength = base_constitution = base_size = base_dexterity = base_willpower = base_appearance = base_education = 50

        cursor.execute(
            "INSERT INTO users (user_id, name, house, personality,strength, constitution, size, dexterity, willpower, appearance, education, luck, hp, mp, sanity, status)"
            "VALUES (%s, %s, NULL, NULL, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 'N')",
            (user_id, user_name, base_strength, base_constitution, base_size, base_dexterity, base_willpower, base_appearance, base_education, luck_value)
        )

        if cursor.rowcount > 0:
            print(f"✅ 유저 등록 완료: {user_id} - {user_name}")

            default_skills = {
                "감정": 5, "고고학": 1, "관찰력": 25, "근접전(격투)": 25, "기계수리": 10,
                "도약": 20, "듣기": 20, "말재주": 5, "매혹": 15, "법률": 5,
                "변장": 5, "사격(권총)": 20, "사격(라/산)": 25, "설득": 10, "손놀림":10,
                "수영": 20, "승마": 5, "심리학": 10, "언어(모국어)": base_education, "역사": 5,
                "열쇠공": 1, "오르기": 20, "오컬트": 5, "위협": 15, "은밀행동": 20,
                "응급처치": 30, "의료": 1, "인류학": 1, "자동차 운전": 20, "자료조사": 20,
                "자연": 10, "전기수리": 10, "정신분석": 1, "중장비 조작": 1, "추적": 10,
                "크툴루 신화": 0, "투척": 20, "항법": 10, "회계": 5, "회피": base_dexterity // 2
            }

            for skill_name, basic_point in default_skills.items():
                cursor.execute(
                    "INSERT INTO investigator (user_id, name, basic_point, add_point) VALUES (%s, %s, %s, 0)",
                    (user_id, skill_name, basic_point)
                )

            print(f"✅ {user_name}의 기본 기능치 추가 완료!")
        conn.commit()

        updated = (cursor.rowcount > 0)
        if updated:
            print(f"✅ 유저 등록 완료: {user_id} - {user_name}")
            update_user_state(user_id)
        return updated
    
    except mysql.connector.Error as e:
        print(f"❌ 유저 등록 실패: {e}")
        return False

    finally:
        cursor.close()
        conn.close()

def update_user_name(user_id, new_name):
    """유저 이름 변경"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET name = %s WHERE user_id = %s", (new_name, user_id))
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

        cursor.execute("UPDATE users SET size = %s WHERE user_id = %s", (new_size, user_id))
        conn.commit()

        updated = (cursor.rowcount > 0)
        if updated:
            update_user_state(user_id)
        return updated

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

        cursor.execute("UPDATE users SET appearance = %s WHERE user_id = %s", (new_appearance, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"❌ 외모(appearance) 변경 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_house(user_id, house_name):
    """유저 기숙사 적용"""
    house_data = get_house_data(house_name)
    if not house_data:
        return False

    strength_boost      = house_data["strength"]
    constitution_boost  = house_data["constitution"]
    size_boost          = house_data["size"]
    intelligence_boost  = house_data["intelligence"]
    willpower_boost     = house_data["willpower"]
    dexterity_boost     = house_data["dexterity"]

    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET house = %s,
                strength      = COALESCE(strength, 0) + %s,
                constitution  = COALESCE(constitution, 0) + %s,
                size          = COALESCE(size, 0) + %s,
                intelligence  = COALESCE(intelligence, 0) + %s,
                willpower     = COALESCE(willpower, 0) + %s,
                dexterity     = COALESCE(dexterity, 0) + %s
            WHERE user_id = %s
        """, (
            house_name,
            strength_boost,
            constitution_boost,
            size_boost,
            intelligence_boost,
            willpower_boost,
            dexterity_boost,
            user_id
        ))
        conn.commit()

        updated = (cursor.rowcount > 0)
        if updated:
            update_user_state(user_id)
        return updated
    
    except mysql.connector.Error as e:
        print(f"❌ 기숙사 업데이트 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_personalities(user_id: str, personality_list: list[str]) -> bool:
    """
    유저 성격 적용
    """
    if not personality_list:
        return False

    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        in_clause = ",".join(["%s"] * len(personality_list))
        query = f"SELECT * FROM personalities WHERE name IN ({in_clause})"
        cursor.execute(query, tuple(personality_list))
        rows = cursor.fetchall()  # [{}, {}, ...]

        if not rows:
            return False

        total_str = total_con = total_int = total_pow = total_dex = 0
        for row in rows:
            total_str += row["strength"]
            total_con += row["constitution"]
            total_int += row["intelligence"]
            total_pow += row["willpower"]
            total_dex += row["dexterity"]

        personality_str = ",".join(personality_list)

        update_query = """
            UPDATE users
            SET personality = %s,
                strength     = COALESCE(strength, 0) + %s,
                constitution = COALESCE(constitution, 0) + %s,
                intelligence = COALESCE(intelligence, 0) + %s,
                willpower    = COALESCE(willpower, 0) + %s,
                dexterity    = COALESCE(dexterity, 0) + %s
            WHERE user_id = %s
        """

        cursor.execute(update_query, (
            personality_str,
            total_str,
            total_con,
            total_int,
            total_pow,
            total_dex,
            user_id
        ))
        conn.commit()

        updated = (cursor.rowcount > 0)
        if updated:
            update_user_state(user_id)

        return updated

    except mysql.connector.Error as e:
        print(f"❌ update_user_personalities 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_personality_list(page=0, page_size=7):
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        offset = page * page_size  # 페이지에 맞는 OFFSET 계산
        cursor.execute(
            "SELECT name, strength, constitution, intelligence, willpower, dexterity "
            "FROM personalities ORDER BY id LIMIT %s OFFSET %s",
            (page_size, offset)
        )
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as e:
        print(f"❌ get_personality_list 실패: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_money(user_id, amount):
    """유저에게 재화 추가 (크넛 단위)"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET money = money + %s WHERE user_id = %s", (amount, user_id))
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 재화 추가 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def remove_money(user_id, amount):
    """유저 재화 감소 (최소 0 유지)"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET money = GREATEST(money - %s, 0) WHERE user_id = %s", (amount, user_id))
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 재화 감소 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_user(user_id):
    """DB에서 해당 유저(id)의 데이터를 삭제"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()

        return cursor.rowcount > 0  # 삭제된 row가 있으면 True 반환
    except mysql.connector.Error as e:
        print(f"❌ 유저 삭제 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def roll_luck():
    """3d6 * 5 행운값 굴리기"""
    return sum(random.randint(1, 6) for _ in range(3)) * 5

def update_user_state(user_id):
    """
    유저 상태 업데이트
    """
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT strength, constitution, size, dexterity, willpower, intelligence, education, hp, mp, sanity FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False

        strength = row["strength"]
        constitution = row["constitution"]
        size = row["size"]
        dexterity = row["dexterity"]
        willpower = row["willpower"]
        intelligence = row["intelligence"]
        education = row["education"]

        hp = (constitution + size) // 10
        mp = willpower // 5
        san = min(willpower, 99)

        if strength < size and dexterity < size:
            mov = 7
        elif strength > size or dexterity > size:
            mov = 9
        else:
            mov = 8
        
        total_str_siz = strength + size
        if total_str_siz <= 64:
            damage_bonus = "-2d6"
            build = -2
        elif total_str_siz <= 84:
            damage_bonus = "-1d6"
            build = -1
        elif total_str_siz <= 124:
            damage_bonus = "0"
            build = 0
        elif total_str_siz <= 164:
            damage_bonus = "+1d4"
            build = 1
        elif total_str_siz <= 204:
            damage_bonus = "+1d6"
            build = 2
        else:
            damage_bonus = "+2d6"
            build = 3

        # 5) 상태(status) 계산
        # HP<1 => 빈사, SAN<=0 => 영구적 광기, 아니면 정상
        # (여기서는 새로 계산된 hp, san을 기준으로 판단)
        if hp < 1:
            status = "D"
        elif san <= 0:
            status = "M"
        else:
            status = "N"

        job_skill_point = education * 4  # 직업 기능 점수 = EDU * 4
        interest_skill_point = intelligence * 2  # 관심 기능 점수 = INT * 2
        skill_point = job_skill_point + interest_skill_point

        cursor.execute("""
            UPDATE users
            SET hp = %s,
                mp = %s,
                sanity = %s,
                movement = %s,
                damage_bonus = %s,
                build = %s,
                status = %s,
                skill_point = %s
            WHERE user_id = %s
        """, (hp, mp, san, mov, damage_bonus, build, status, skill_point, user_id))
        conn.commit()

        return True
    except mysql.connector.Error as e:
        print(f"❌ 보조 스탯 계산 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_house_data(house_name: str):
    """
    DB의 houses 테이블에서 name이 house_name인 row를 가져옴.
    반환: { 'name': str, 'role_id': int, 'strength': int, ... } 형태의 dict
    """
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM houses WHERE name = %s"
        cursor.execute(query, (house_name,))
        row = cursor.fetchone()  # dict 형태로 반환됨
        return row  # 없다면 None
    except mysql.connector.Error as e:
        print(f"❌ get_house_data 실패: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_personality_data(personality_name: str):
    """
    DB의 personalities 테이블에서 name이 personality_name인 row를 가져옴.
    반환: { 'name': str, 'strength': int, ... } 형태의 dict
    """
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM personalities WHERE name = %s"
        cursor.execute(query, (personality_name,))
        row = cursor.fetchone()
        return row
    except mysql.connector.Error as e:
        print(f"❌ get_personality_data 실패: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_house_roles():
    """
    houses 테이블의 모든 row에서 role_id를 추출해
    정수들의 리스트(혹은 세트)로 반환.
    """
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT role_id FROM houses")
        rows = cursor.fetchall()  # 예: [(1342...), (1342...), (None)...]

        # role_id가 None인 경우도 있을 수 있으니 필터링
        role_ids = [row[0] for row in rows if row[0] is not None]
        return role_ids

    except mysql.connector.Error as e:
        print(f"❌ get_all_house_roles 실패: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


