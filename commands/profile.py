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

    # @app_commands.command(name="조회", description="내 프로필 정보를 확인합니다.")
    # async def view_profile(self, interaction: discord.Interaction):
    #     """유저 프로필을 확인하는 명령어"""
    #     user_id = str(interaction.user.id)
    #     user_data = get_user(user_id)

    #     if user_data:
    #         (user_name, house, personality, strength, constitution, size, intelligence,
    #         willpower, dexterity, appearance, education, money, luck, movement, damage_bonus,
    #         build, hp, mp, sanity) = user_data[1:]

    #         galleons = money // 493  # 1 갈레온 = 493 크넛
    #         remainder = money % 493
    #         sickles = remainder // 29  # 1 시클 = 29 크넛
    #         knuts = remainder % 29  # 나머지 크넛

    #         embed = discord.Embed(title="📜 내 프로필", color=0x3498db)

    #         embed.add_field(name="이름", value=user_name, inline=False)
    #         embed.add_field(name="🏠 기숙사", value=house if house else "미정", inline=False)
    #         embed.add_field(name="🙂 성격", value=personality if personality else "미정", inline=False)

    #         embed.add_field(name="💪 근력 (STR)", value=str(strength), inline=True)
    #         embed.add_field(name="❤️ 건강 (CON)", value=str(constitution), inline=True)
    #         embed.add_field(name="📏 크기 (SIZ)", value=str(size), inline=True)
    #         embed.add_field(name="⚡ 민첩 (DEX)", value=str(dexterity), inline=True)
    #         embed.add_field(name="🎭 외모 (APP)", value=str(appearance), inline=True)
    #         embed.add_field(name="🧠 지능 (INT)", value=str(intelligence), inline=True)
    #         embed.add_field(name="🛡️ 정신 (POW)", value=str(willpower), inline=True)
    #         embed.add_field(name="📖 교육 (EDU)", value=str(education), inline=True)

    #         embed.add_field(name="🍀 행운 (LUK)", value=str(luck), inline=True)
    #         embed.add_field(name="🏃 이동력 (MOV)", value=str(movement), inline=True)
    #         embed.add_field(name="🛡️ 피해보너스 (DB)", value=str(damage_bonus), inline=True)
    #         embed.add_field(name="📏 체구 (BUILD)", value=str(build), inline=True)
    #         embed.add_field(name="🛡️ 체력 (HP)", value=str(hp), inline=True)
    #         embed.add_field(name="🔮 마력 (MP)", value=str(mp), inline=True)
    #         embed.add_field(name="🛡️ 이성 (SAN)", value=str(sanity), inline=True)

    #         embed.add_field(name="💰 재화", value=f"{galleons} 갈레온 {sickles} 시클 {knuts} 크넛", inline=False)

    #         await interaction.response.send_message(embed=embed, ephemeral=True)
    #     else:
    #         await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)


    @app_commands.command(name="조회", description="내 프로필 정보를 확인합니다.")
    async def view_profile(self, interaction: discord.Interaction):
        """유저 프로필(탐사자 정보)을 확인하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        # DB에서 가져온 데이터가 없으면 안내 후 종료
        if not user_data:
            await interaction.response.send_message(
                "❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.",
                ephemeral=True
            )
            return

        # user_data[0]이 id이므로 [1:]부터가 우리가 쓸 필드들
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
            sanity
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

        # ───────────── [기본 정보] 2컬럼 예시 ─────────────
        # 왼쪽: 이름, 기숙사 | 오른쪽: 성격, (원하면 다른 항목도)
        # 예시는 총 4줄 정도만 쓴 뒤 코드 블록으로 감쌉니다.
        basic_left = [
            ("이름", user_name),
            ("기숙사", house if house else "미정")
        ]
        basic_right = [
            ("성격", personality if personality else "미정"),
            ("교육", f"{education}")  # 혹은 다른 항목
        ]
        # 두 리스트의 길이가 같아야 zip으로 묶어서 한 줄씩 출력 가능
        # 길이가 안 맞으면 맞춰주세요(비거나, 더 적으면).
        # 각 항목을 폭 8~10 정도로 맞춰 주면 깔끔.

        basic_info_lines = []
        for (label1, val1), (label2, val2) in zip(basic_left, basic_right):
            line = f"{label1:<6}: {val1:<10}   {label2:<6}: {val2}"
            basic_info_lines.append(line)

        # 코드 블록으로 묶어서 고정폭 폰트 적용
        basic_info_block = "```" + "\n".join(basic_info_lines) + "```"
        embed.add_field(name=":bust_in_silhouette: 기본 정보", value=basic_info_block, inline=False)

        # ───────────── [능력치] 2컬럼 예시 ─────────────
        # 왼쪽에 STR,DEX,APP,POW / 오른쪽에 CON,SIZ,INT,EDU 등
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
            # 왼쪽 폭 14 / 오른쪽 폭 14 정도로 맞춤 (원하는 대로 조정)
            line = f"{label1:<10}: {str(val1):<3}   {label2:<10}: {str(val2)}"
            stats_lines.append(line)

        stats_block = "```" + "\n".join(stats_lines) + "```"
        embed.add_field(name=":muscle: 능력치", value=stats_block, inline=False)

        # ───────────── [전투/정신 정보] 2컬럼 ─────────────
        # HP, MP, SAN, LUK, MOV, DB, BUILD 등등
        # 필요에 따라 7개라 짝이 안 맞으면 빈 칸으로 맞춰도 되고,
        # 3개 vs 4개 이런 식으로 분배할 수도 있습니다.
        combat_left = [
            ("HP(체력)", hp),
            ("MP(마력)", mp),
            ("SAN(이성)", sanity),
        ]
        combat_right = [
            ("LUK(행운)", luck),
            ("MOV(이동력)", movement),
            ("DB(피해보너스)", damage_bonus),
            ("BUILD(체구)", build),
        ]
        combat_lines = []
        # zip()은 짧은쪽에 맞춰 돌아감 → 길이 다르면 주의
        for (label1, val1), (label2, val2) in zip(combat_left, combat_right):
            line = f"{label1:<12}: {val1:<3}   {label2:<14}: {val2}"
            combat_lines.append(line)

        # 만약 combat_right가 더 길다면 남은 아이템을 추가로 처리해야 함
        # 여기서는 예시로 생략. 필요하면 while문 등에 넣어서 남은 부분도 출력 가능.

        combat_block = "```" + "\n".join(combat_lines) + "```"
        embed.add_field(name=":shield: 생존/정신 정보", value=combat_block, inline=False)

        # ───────────── [재화] ─────────────
        money_str = f"{galleons} 갈레온 {sickles} 시클 {knuts} 크넛"
        embed.add_field(name=":moneybag: 보유 재화", value=f"```\n{money_str}\n```", inline=False)

        # 임베드 전송(개인 메시지처럼 보이려면 ephemeral=True)
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