import os
import urllib.parse
import mysql.connector
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
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
        "database": url.path.lstrip("/"),  # "/railway"에서 "/" 제거
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

# 봇 설정
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 유저 등록 명령어
@bot.tree.command(name="등록", description="유저를 등록합니다.")
async def register(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_name = interaction.user.display_name

    # 이미 등록된 유저인지 확인
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await interaction.response.send_message("이미 등록된 유저입니다!", ephemeral=True)
    else:
        cursor.execute("INSERT INTO users (id, name) VALUES (%s, %s)", (user_id, user_name))
        conn.commit()
        await interaction.response.send_message(f"🎉 등록 완료! 환영합니다, **{user_name}**!", ephemeral=True)

# 봇이 준비되었을 때 실행
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} 로그인 완료!")

# 봇 실행
bot.run(TOKEN)