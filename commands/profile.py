import discord
from discord import app_commands
from database import get_user, update_user_name, update_user_size, update_user_house, update_user_appearance, update_user_personality, register_user, HOUSE_STATS, HOUSE_ROLES, PERSONALITY_STATS  # DB 함수 가져오기

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
        """유저 프로필(탐사자 정보)을 확인하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message(
                "❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.",
                ephemeral=True
            )
            return

        (
            user_name,
            house,
            personality,
            strength,
            constitution,
            size,
            intelligence,
            willpower,
            dexterity,
            appearance,
            education,
            money,
            luck,
            movement,
            damage_bonus,
            build,
            hp,
            mp,
            sanity,
            status
        ) = user_data[1:]

        # 재화 환산
        galleons = money // 493
        remainder = money % 493
        sickles = remainder // 29
        knuts = remainder % 29

        embed = discord.Embed(
            title=":scroll: 내 프로필",
            description="아래는 당신의 탐사자(캐릭터) 정보입니다.",
            color=0x3498db
        )

        # ────────── [1] 기본 정보 (코드 블록) ──────────
        basic_info_lines = []
        basic_info_lines.append(f"이름   : {user_name}")
        basic_info_lines.append(f"소속   : {house or '미정'}")
        basic_info_lines.append(f"성격   : {personality or '미정'}")

        basic_info_block = "```" + "\n".join(basic_info_lines) + "```"

        embed.add_field(name=":bust_in_silhouette: 기본 정보", value=basic_info_block, inline=False)

        # ────────── [2] 특성치 (코드 블록 2칼럼) ──────────
        stats_left = [
            ("STR(근력)", strength),
            ("DEX(민첩)", dexterity),
            ("APP(외모)", appearance),
            ("POW(정신)", willpower),
        ]
        stats_right = [
            ("CON(건강)", constitution),
            ("SIZ(크기)", size),
            ("INT(지능)", intelligence),
            ("EDU(교육)", education),
        ]

        stats_lines = []
        for (label1, val1), (label2, val2) in zip(stats_left, stats_right):
            line = f"{label1:<9}: {val1:<2}  {label2:<9}: {val2}"
            stats_lines.append(line)

        stats_block = "```" + "\n".join(stats_lines) + "```"
        embed.add_field(name=":star: 특성치", value=stats_block, inline=False)

        # ────────── [3] 보조 특성치 (코드 블록, 공백 축소) ──────────
        combat_left = [
            ("HP(체력)", hp),
            ("MP(마력)", mp),
            ("SAN(이성)", sanity),
            ("STAT(상태)", status),
        ]
        combat_right = [
            ("LUK(행운)", luck),
            ("MOV(이동)", movement),
            ("DB(피해)", damage_bonus),
            ("BUILD(체구)", build),
        ]
        combat_lines = []
        for (label1, val1), (label2, val2) in zip(combat_left, combat_right):
            line = f"{label1:<9}: {val1:<2} {label2:<9}: {val2}"
            combat_lines.append(line)

        combat_block = "```" + "\n".join(combat_lines) + "```"
        embed.add_field(name=":jigsaw: 보조 특성치", value=combat_block, inline=False)

        # ────────── [4] 보유 재화 ──────────
        money_str = f"{galleons} 갈레온 {sickles} 시클 {knuts} 크넛"
        embed.add_field(name=":moneybag: 보유 재화", value=f"```\n{money_str}\n```", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)




    @app_commands.command(name="이름변경", description="캐릭터 닉네임을 변경합니다.")
    async def change_profile(self, interaction: discord.Interaction, new_name: str):
        """유저 닉네임 정보를 변경하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if user_data:
            update_user_name(user_id, new_name)
            await interaction.response.send_message(f"✅ 이름이 `{new_name}`(으)로 변경되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)


    @app_commands.command(name="크기변경", description="캐릭터 크기(SIZ) 스탯을 변경합니다.")
    async def change_size(self, interaction: discord.Interaction, new_size: int):
        """유저가 직접 크기(SIZ)를 변경하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        if not (1 <= new_size <= 100):
            await interaction.response.send_message("❌ 크기(SIZ)는 1에서 100 사이의 값만 가능합니다.", ephemeral=True)
            return

        success = update_user_size(user_id, new_size)
        if success:
            await interaction.response.send_message(f"📏 크기(SIZ)가 `{new_size}`(으)로 변경되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 크기(SIZ) 변경에 실패했습니다.", ephemeral=True)


    @app_commands.command(name="외모변경", description="캐릭터 외모(APP) 스탯을 변경합니다.")
    async def change_appearance(self, interaction: discord.Interaction, new_appearance: int):
        """유저가 직접 외모(APP)를 변경하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        if not (1 <= new_appearance <= 100):
            await interaction.response.send_message("❌ 외모(APP)는 1에서 100 사이의 값만 가능합니다.", ephemeral=True)
            return

        success = update_user_appearance(user_id, new_appearance)
        if success:
            await interaction.response.send_message(f"🎭 외모(APP)가 `{new_appearance}`(으)로 변경되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 외모(APP) 변경에 실패했습니다.", ephemeral=True)


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

    @discord.ui.button(label="후플푸프 🦡", style=discord.ButtonStyle.gray)
    async def hufflepuff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.assign_house(interaction, "후플푸프")

    async def assign_house(self, interaction: discord.Interaction, house: str):
        """기숙사를 선택하면 DB 업데이트 후 역할 부여"""
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
        try:
            for r in user.roles:
                if r.id in HOUSE_ROLES.values():  # 기존 기숙사 역할이 있으면 제거
                    await user.remove_roles(r)
        except discord.Forbidden:
            await interaction.response.send_message("❌ 봇에게 역할을 제거할 권한이 없습니다. 관리자에게 문의하세요.", ephemeral=True)
            return

        # 새 역할 부여
        try:
            await user.add_roles(role)
        except discord.Forbidden:
            await interaction.response.send_message("❌ 봇에게 역할을 추가할 권한이 없습니다. 관리자에게 문의하세요.", ephemeral=True)
            return

        # DB 업데이트
        success = update_user_house(str(user.id), house)
        if success:
            try:
                # 버튼을 비활성화하여 중복 선택 방지
                for child in self.children:
                    child.disabled = True

                await interaction.response.edit_message(
                    content=f"🏠 **{user.display_name} 님이 {house} 기숙사에 배정되었습니다!** 역할이 자동으로 부여되었습니다.",
                    view=self  # 버튼 비활성화 적용된 View 업데이트
                )
            except discord.NotFound:
                await interaction.followup.send(
                    f"🏠 **{user.display_name} 님이 {house} 기숙사에 배정되었습니다!** 역할이 자동으로 부여되었습니다.",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message("❌ 기숙사 업데이트에 실패했습니다. 관리자에게 문의하세요.", ephemeral=True)

# 명령어 그룹 객체 생성
profile_group = ProfileCommands(name="프로필", description="프로필 관련 명령어 그룹")