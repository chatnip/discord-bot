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
    async def select_house(self, interaction: discord.Interaction):
        """기숙사 선택 버튼을 보여주는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        view = HouseSelectionView(user_id)
        await interaction.response.send_message("🏠 **기숙사를 선택하세요!**", view=view, ephemeral=True)

    @app_commands.command(name="성격선택", description="성격을 선택합니다.")
    async def select_personality(self, interaction: discord.Interaction):
        """성격 선택 버튼을 보여주는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        view = PersonalitySelectionView(user_id)  # 동적으로 버튼 생성
        await interaction.response.send_message("😃 **성격을 선택하세요!**", view=view, ephemeral=True)

class HouseSelectionView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)  # 60초 후 버튼 비활성화
        self.user_id = user_id

    @discord.ui.button(label="그리핀도르 🦁", style=discord.ButtonStyle.red)
    async def gryffindor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_house(interaction, "그리핀도르")

    @discord.ui.button(label="슬리데린 🐍", style=discord.ButtonStyle.green)
    async def slytherin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_house(interaction, "슬리데린")

    @discord.ui.button(label="래번클로 🦅", style=discord.ButtonStyle.blurple)
    async def ravenclaw_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_house(interaction, "래번클로")

    @discord.ui.button(label="후플푸프 🦡", style=discord.ButtonStyle.grey)
    async def hufflepuff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_house(interaction, "후플푸프")

    async def assign_house(self, interaction: discord.Interaction, house: str):
        """기숙사 선택 시 DB 업데이트 후 역할 부여"""
        guild = interaction.guild  # 서버 정보 가져오기
        user = interaction.user  # 유저 정보 가져오기
        role_id = HOUSE_ROLES.get(house)  # 선택한 기숙사 역할 ID 가져오기

        if not role_id:
            await interaction.response.send_message("❌ 해당 기숙사 역할을 찾을 수 없습니다.", ephemeral=True)
            return

        role = guild.get_role(role_id)  # 역할 객체 가져오기
        if not role:
            await interaction.response.send_message("❌ 해당 역할이 존재하지 않습니다. 서버 관리자에게 문의하세요.", ephemeral=True)
            return

        # 기존 기숙사 역할 제거
        for r in user.roles:
            if r.id in HOUSE_ROLES.values():  # 기존 기숙사 역할이 있으면 제거
                await user.remove_roles(r)

        # 새 역할 부여
        await user.add_roles(role)

        # DB 업데이트
        success = update_user_house(str(user.id), house)
        if success:
            await interaction.response.edit_message(
                content=f"🏠 **{user.display_name} 님이 {house} 기숙사에 배정되었습니다!** 역할이 자동으로 부여되었습니다.",
                view=None
            )
        else:
            await interaction.response.send_mess
            
# 명령어 그룹 객체 생성
profile_group = ProfileCommands(name="프로필", description="프로필 관련 명령어 그룹")
