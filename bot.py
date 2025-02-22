import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# 명령어 그룹 불러오기
from commands.profile import profile_group

# 환경 변수 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 봇 설정
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 명령어 그룹 등록
bot.tree.add_command(profile_group)

# 봇 실행
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} 로그인 완료!")

bot.run(TOKEN)
