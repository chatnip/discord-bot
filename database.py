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
# try:
#     db_config = get_db_config()
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()

#     try:
#         # 1) houses 테이블
#         cursor.execute('''
#             ALTER TABLE personalities DROP COLUMN size
#         ''')

#         conn.commit()
#         print("✅ 테이블 삭제 완료!")

#     except mysql.connector.Error as e:
#         print(f"❌ SQL 실행 실패: {e}")

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

        # 행운 주사위 굴리기
        luck_value = roll_luck()

        # 기본값 계산
        base_strength = base_constitution = base_size = base_dexterity = base_willpower = base_appearance = base_education = 50

        cursor.execute(
            "INSERT INTO users (id, name, house, personality,strength, constitution, size, dexterity, willpower, appearance, education, luck, hp, mp, sanity, status)"
            "VALUES (%s, %s, NULL, NULL, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, '정상')",
            (user_id, user_name, base_strength, base_constitution, base_size, base_dexterity, base_willpower, base_appearance, base_education, luck_value)
        )
        conn.commit()

        updated = (cursor.rowcount > 0)
        if updated:
            print(f"✅ 유저 등록 완료: {user_id} - {user_name}")
            calculate_derived_stats(user_id)
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

        updated = (cursor.rowcount > 0)
        if updated:
            calculate_derived_stats(user_id)
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

        cursor.execute("UPDATE users SET appearance = %s WHERE id = %s", (new_appearance, user_id))
        conn.commit()
        return cursor.rowcount > 0  # 업데이트 성공 여부 반환
    except mysql.connector.Error as e:
        print(f"❌ 외모(appearance) 변경 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_house(user_id, house_name):
    """유저가 기숙사를 선택하면 해당 기숙사의 능력치를 반영"""
    house_data = get_house_data(house_name)
    if not house_data:
        return False  # 존재하지 않는 기숙사

    # 2) 보정치 추출
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

        # 3) 유저 테이블 업데이트
        cursor.execute("""
            UPDATE users
            SET house = %s,
                strength      = COALESCE(strength, 0) + %s,
                constitution  = COALESCE(constitution, 0) + %s,
                size          = COALESCE(size, 0) + %s,
                intelligence  = COALESCE(intelligence, 0) + %s,
                willpower     = COALESCE(willpower, 0) + %s,
                dexterity     = COALESCE(dexterity, 0) + %s
            WHERE id = %s
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
            calculate_derived_stats(user_id)
        return updated
    
    except mysql.connector.Error as e:
        print(f"❌ 기숙사 업데이트 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_personality(user_id, personality_name):
    """유저가 성격을 선택하면 해당 성격의 능력치를 반영"""
    personality_data = get_personality_data(personality_name)
    if not personality_data:
        return False  # 없는 성격

    # 보정치 추출
    str_boost = personality_data["strength"]
    con_boost = personality_data["constitution"]
    int_boost = personality_data["intelligence"]
    pow_boost = personality_data["willpower"]
    dex_boost = personality_data["dexterity"]

    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET personality = %s,
                strength     = COALESCE(strength, 0) + %s,
                constitution = COALESCE(constitution, 0) + %s,
                intelligence = COALESCE(intelligence, 0) + %s,
                willpower    = COALESCE(willpower, 0) + %s,
                dexterity    = COALESCE(dexterity, 0) + %s
            WHERE id = %s
        """, (
            personality_name,
            str_boost,
            con_boost,
            int_boost,
            pow_boost,
            dex_boost,
            user_id
        ))
        conn.commit()

        updated = (cursor.rowcount > 0)
        if updated:
            calculate_derived_stats(user_id)
        return updated
    
    except mysql.connector.Error as e:
        print(f"❌ 성격 업데이트 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_money(user_id, amount):
    """유저에게 재화 추가 (크넛 단위)"""
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET money = money + %s WHERE id = %s", (amount, user_id))
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

        cursor.execute("UPDATE users SET money = GREATEST(money - %s, 0) WHERE id = %s", (amount, user_id))
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

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
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

def calculate_derived_stats(user_id):
    """
    유저의 STR, SIZ, HP, SAN 등을 바탕으로 MOV, DB, Build, 상태(status)를 재계산하여 DB에 반영.
    성공하면 True, 실패면 False.
    """
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 1) 현재 캐릭터 정보 가져오기
        cursor.execute("SELECT strength, constitution, size, dexterity, willpower, hp, mp, sanity FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False  # 없는 유저

        strength = row["strength"]
        constitution = row["constitution"]
        size = row["size"]
        dexterity = row["dexterity"]
        willpower = row["willpower"]

        # 2) HP, MP, SAN 계산
        #    (CoC 7판 기준 가정)
        hp = (constitution + size) // 10
        mp = willpower // 5
        san = min(willpower, 99)  # 최대치 99로 가정

        # 3) 이동력(MOV) 계산 예시
        # (단순화: STR< SIZ and DEX< SIZ => mov=7,  STR> SIZ or DEX> SIZ => mov=9, else 8)
        if strength < size and dexterity < size:
            mov = 7
        elif strength > size or dexterity > size:
            mov = 9
        else:
            mov = 8
        
        # 4) 피해 보너스(DB) & Build
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
            status = "빈사"
        elif san <= 0:
            status = "영구적 광기"
        else:
            status = "정상"

        # 6) DB 업데이트
        cursor.execute("""
            UPDATE users
            SET hp = %s,
                mp = %s,
                sanity = %s,
                movement = %s,
                damage_bonus = %s,
                build = %s,
                status = %s
            WHERE id = %s
        """, (hp, mp, san, mov, damage_bonus, build, status, user_id))
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


