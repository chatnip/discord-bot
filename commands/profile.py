import discord
from discord import app_commands
from database import get_user, update_user_name, register_user  # DB 함수 가져오기

class ProfileCommands(discord.app_commands.Group):
    """프로필 관련 명령어 그룹"""

    @app_commands.command(name="등록", description="유저를 등록합니다.")
    async def register(self, interaction: discord.Interaction):
        """유저를 등록하는 명령어"""
        user_id = str(interaction.user.id)
        user_name = interaction.user.display_name

        existing_user = get_user(user_id)
        if existing_user:
            await interaction.response.send_message("이미 등록된 유저입니다!", ephemeral=True)
        else:
            register_user(user_id, user_name)
            await interaction.response.send_message(f"🎉 등록 완료! 환영합니다, **{user_name}**!", ephemeral=True)

    @app_commands.command(name="조회", description="내 프로필 정보를 확인합니다.")
    async def view_profile(self, interaction: discord.Interaction):
        """유저 프로필을 확인하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if user_data:
            user_name = user_data[1]  # DB에서 가져온 이름
            embed = discord.Embed(title="📜 내 프로필", color=0x3498db)
            embed.add_field(name="이름", value=user_name, inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)

    @app_commands.command(name="변경", description="내 프로필 정보를 변경합니다.")
    async def change_profile(self, interaction: discord.Interaction, new_name: str):
        """유저 프로필 정보를 변경하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if user_data:
            update_user_name(user_id, new_name)
            await interaction.response.send_message(f"✅ 이름이 `{new_name}`(으)로 변경되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)

# 명령어 그룹 객체 생성
profile_group = ProfileCommands(name="프로필", description="프로필 관련 명령어 그룹")