import discord
from discord import app_commands
from database import get_user, update_user_name, update_user_house, update_user_personality, register_user, HOUSE_STATS, PERSONALITY_STATS  # DB 함수 가져오기

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
            user_name, house, personality, STR, CON, SIZ, INT, POW, DEX, APP, EDU = user_data[1:]

            embed = discord.Embed(title="📜 내 프로필", color=0x3498db)
            embed.add_field(name="이름", value=user_name, inline=False)
            embed.add_field(name="🏠 기숙사", value=house if house else "미정", inline=False)
            embed.add_field(name="😃 성격", value=personality if personality else "미정", inline=False)
            embed.add_field(name="💪 힘 (STR)", value=str(STR), inline=True)
            embed.add_field(name="❤️ 건강 (CON)", value=str(CON), inline=True)
            embed.add_field(name="📏 크기 (SIZ)", value=str(SIZ), inline=True)
            embed.add_field(name="🧠 지능 (INT)", value=str(INT), inline=True)
            embed.add_field(name="🛡️ 이성 (POW)", value=str(POW), inline=True)
            embed.add_field(name="⚡ 민첩 (DEX)", value=str(DEX), inline=True)

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

    @app_commands.command(name="기숙사선택", description="기숙사를 선택합니다.")
    async def select_house(self, interaction: discord.Interaction, house: str):
        """유저가 기숙사를 선택하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        if house.lower() not in [h.lower() for h in HOUSE_STATS.keys()]:
            await interaction.response.send_message("❌ 올바른 기숙사를 선택해주세요! (그리핀도르, 슬리데린, 래번클로, 후플푸프)", ephemeral=True)
            return

        success = update_user_house(user_id, house)
        if success:
            await interaction.response.send_message(f"🏠 {interaction.user.display_name} 님이 **{house}** 기숙사에 배정되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 기숙사 업데이트에 실패했습니다. 관리자에게 문의하세요.", ephemeral=True)

    @app_commands.command(name="성격선택", description="성격을 선택합니다.")
    async def select_personality(self, interaction: discord.Interaction, personality: str):
        """유저가 성격을 선택하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        personality = personality.lower()
        if personality not in PERSONALITY_STATS:
            await interaction.response.send_message("❌ 올바른 성격을 선택해주세요!", ephemeral=True)
            return

        success = update_user_personality(user_id, personality)
        if success:
            await interaction.response.send_message(f"✅ 성격이 `{personality}`(으)로 설정되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 성격 업데이트에 실패했습니다. 관리자에게 문의하세요.", ephemeral=True)

# 명령어 그룹 객체 생성
profile_group = ProfileCommands(name="프로필", description="프로필 관련 명령어 그룹")
