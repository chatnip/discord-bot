import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 봇 설정 (슬래시 명령어 지원)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 데이터 저장 파일 경로
DATA_FILE = "users.json"

# JSON 파일에서 유저 데이터 불러오기
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

# JSON 파일에 유저 데이터 저장
def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

# 유저 등록 명령어 (슬래시 명령어)
@bot.tree.command(name="등록", description="유저를 등록합니다.")
async def register(interaction: discord.Interaction):
    users = load_users()
    user_id = str(interaction.user.id)
    
    if user_id in users:
        await interaction.response.send_message("이미 등록된 유저입니다!", ephemeral=True)
    else:
        users[user_id] = {
            "name": interaction.user.display_name  # 닉네임을 캐릭터 이름으로 등록
        }
        save_users(users)
        await interaction.response.send_message(f"🎉 등록 완료! 환영합니다, **{interaction.user.display_name}**!", ephemeral=True)

# 봇이 준비되었을 때 실행 (슬래시 명령어 동기화)
@bot.event
async def on_ready():
    await bot.tree.sync()  # 슬래시 명령어 동기화
    print(f"✅ {bot.user} 로그인 완료!")

# 봇 실행
bot.run(TOKEN)
