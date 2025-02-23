import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# 명령어 그룹 불러오기
from commands.profile import profile_group
from commands.gm_commands import gm_group

# 환경 변수 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 봇 설정
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 명령어 그룹 등록
bot.tree.add_command(profile_group)
bot.tree.add_command(gm_group)

# 봇 실행
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} 로그인 완료!")

@bot.tree.command(name="sync", description="슬래시 명령어를 동기화합니다.")
async def sync_commands(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message("✅ 슬래시 명령어가 동기화되었습니다!", ephemeral=True)


bot.run(TOKEN)