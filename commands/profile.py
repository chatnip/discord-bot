import discord
from discord import app_commands
from database import register_user, get_user, get_house_data, get_personality_list, get_all_house_roles
from database import update_user_name, update_user_size, update_user_appearance, update_user_house, update_user_personalities

class ProfileCommands(discord.app_commands.Group):
    """프로필 관련 명령어 그룹"""

    def __init__(self):
        super().__init__(name="프로필", description="프로필 관련 명령어 그룹")
        self.add_command(ProfileEditCommands(name="변경", description="프로필 정보를 변경하는 명령어 그룹"))

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
            line = f"{label1:<9}: {val1:<4}  {label2:<9}: {val2}"
            stats_lines.append(line)

        stats_block = "```" + "\n".join(stats_lines) + "```"
        embed.add_field(name=":star: 특성치", value=stats_block, inline=False)

        # ────────── [3] 보조 특성치 (코드 블록, 공백 축소) ──────────
        combat_left = [
            ("HP(체력)", hp),
            ("MP(마력)", mp),
            ("SAN(이성)", sanity),
            ("STA(상태)", status),
        ]
        combat_right = [
            ("LUK(행운)", luck),
            ("MOV(이동)", movement),
            ("DB(피해)", damage_bonus),
            ("BUILD(체구)", build),
        ]
        combat_lines = []
        for (label1, val1), (label2, val2) in zip(combat_left, combat_right):
            line = f"{label1:<9}: {val1:<4} {label2:<9}: {val2}"
            combat_lines.append(line)

        combat_block = "```" + "\n".join(combat_lines) + "```"
        embed.add_field(name=":jigsaw: 보조 특성치", value=combat_block, inline=False)

        # ────────── [4] 보유 재화 ──────────
        money_str = f"{galleons} 갈레온 {sickles} 시클 {knuts} 크넛"
        embed.add_field(name=":moneybag: 보유 재화", value=f"```\n{money_str}\n```", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        """사용자가 성격을 선택할 수 있도록 페이지네이션을 제공하는 명령어"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message(
                "❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True
            )
            return

        personality = user_data[3]  # (id, name, house, personality, ...)

        if personality and personality != "":
            await interaction.response.send_message(
                "❌ 이미 성격을 선택하셨습니다. 다시 변경할 수 없습니다!", ephemeral=True
            )
            return

        # 🔹 첫 번째 페이지의 데이터만 불러오도록 변경
        view = PersonalityPagesView(user_id, page=0)

        # 첫 페이지의 내용을 포함하여 응답 전송
        await interaction.response.send_message(
            content=f"**1 페이지**\n원하는 성격을 선택하세요! (최대 4개)",
            view=view,
            ephemeral=True
        )
   

class ProfileEditCommands(app_commands.Group):
    """프로필 변경 관련 명령어 그룹"""

    @app_commands.command(name="이름", description="캐릭터 이름을 변경합니다.")
    async def change_profile(self, interaction: discord.Interaction, new_name: str):
        """캐릭터 이름 변경"""
        user_id = str(interaction.user.id)
        user_data = get_user(user_id)

        if not user_data:
            await interaction.response.send_message("❌ 등록된 정보가 없습니다! `/프로필 등록`을 먼저 해주세요.", ephemeral=True)
            return

        success = update_user_name(user_id, new_name)
        if success:
            await interaction.response.send_message(f"✅ 이름이 `{new_name}`(으)로 변경되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 이름 변경에 실패했습니다.", ephemeral=True)

    @app_commands.command(name="크기", description="캐릭터 크기(SIZ) 스탯을 변경합니다.")
    async def change_size(self, interaction: discord.Interaction, new_size: int):
        """캐릭터 크기 변경"""
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
            await interaction.response.send_message(f"✅ 크기(SIZ)가 `{new_size}`(으)로 변경되었습니다!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 크기(SIZ) 변경에 실패했습니다.", ephemeral=True)

    @app_commands.command(name="외모", description="캐릭터 외모(APP) 스탯을 변경합니다.")
    async def change_appearance(self, interaction: discord.Interaction, new_appearance: int):
        """캐릭터 외모 변경"""
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
        house_data = get_house_data(house)
        if not house_data:
            await interaction.response.send_message("❌ 해당 기숙사를 DB에서 찾을 수 없습니다.", ephemeral=True)
            return

        role_id = house_data["role_id"]
        if not role_id:
            await interaction.response.send_message("❌ 이 기숙사에 연결된 역할 ID가 없습니다.", ephemeral=True)
            return

        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("❌ 해당 역할이 서버에 존재하지 않습니다. 관리자에게 문의해주세요.", ephemeral=True)
            return

        # 기존 기숙사 역할 제거
        try:
            all_house_role_ids = get_all_house_roles()
            for r in user.roles:
                if r.id in all_house_role_ids:
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

class PersonalityPagesView(discord.ui.View):
    def __init__(self, user_id, page=0):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.page = page
        self.selected_personalities = set()  # 🔹 선택한 성격을 저장하는 집합
        self.load_page_data()  # 현재 페이지 데이터 불러오기

    def load_page_data(self):
        """현재 페이지 데이터를 DB에서 불러옴 (최적화된 방식)"""
        self.personality_list = get_personality_list(page=self.page, page_size=7)
        self.update_options()

    def update_options(self):
        """현재 페이지에 맞게 SelectMenu 옵션을 갱신"""
        options = [discord.SelectOption(label=p["name"], value=p["name"]) for p in self.personality_list]

        # 기존 SelectMenu 제거 후 새로 추가
        if hasattr(self, "select_menu"):
            self.remove_item(self.select_menu)

        self.select_menu = PersonalitySelect(self)  # 🔹 `view` 대신 `self` 전달
        self.add_item(self.select_menu)

        # 페이지 버튼 상태 업데이트
        self.prev_page.disabled = (self.page == 0)
        self.next_page.disabled = (len(self.personality_list) < 7)

        # 선택 완료 버튼 추가 (선택한 성격이 있을 때만 활성화)
        if hasattr(self, "confirm_button"):
            self.remove_item(self.confirm_button)
        self.confirm_button = discord.ui.Button(label="선택 완료", style=discord.ButtonStyle.green)
        self.confirm_button.callback = self.confirm_selection
        self.add_item(self.confirm_button)

    async def confirm_selection(self, interaction: discord.Interaction):
        """선택한 성격을 최종적으로 저장"""
        if not self.selected_personalities:
            await interaction.response.send_message("❌ 최소 1개 이상의 성격을 선택해야 합니다.", ephemeral=True)
            return

        # DB 반영
        success = update_user_personalities(self.user_id, list(self.selected_personalities))
        if success:
            await interaction.response.send_message(
                f"✅ 성격 `{', '.join(self.selected_personalities)}` 이(가) 적용되었습니다!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ 성격 업데이트에 실패했습니다.", ephemeral=True)

        # 선택 후 UI 비활성화
        self.disable_all()
        await interaction.message.edit(view=self)

    def disable_all(self):
        """모든 UI 요소를 비활성화"""
        for child in self.children:
            child.disabled = True

    @discord.ui.button(label="이전", style=discord.ButtonStyle.gray, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """이전 페이지 버튼"""
        self.page -= 1
        self.load_page_data()
        await interaction.response.edit_message(
            content=f"**{self.page + 1} 페이지**\n원하는 성격을 선택하세요! (최대 4개)",
            view=self
        )

    @discord.ui.button(label="다음", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """다음 페이지 버튼"""
        self.page += 1
        self.load_page_data()
        await interaction.response.edit_message(
            content=f"**{self.page + 1} 페이지**\n원하는 성격을 선택하세요! (최대 4개)",
            view=self
        )

class PersonalitySelect(discord.ui.Select):
    def __init__(self, parent_view: PersonalityPagesView):
        options = [discord.SelectOption(label=p["name"], value=p["name"]) for p in parent_view.personality_list]
        super().__init__(placeholder="원하는 성격을 선택하세요!", min_values=1, max_values=4, options=options)
        self.parent_view = parent_view  # 🔹 `view` 대신 `parent_view`를 사용

    async def callback(self, interaction: discord.Interaction):
        """사용자가 성격을 선택하면 `PersonalityPagesView`에 저장 또는 삭제"""
        selected_values = set(self.values)  # 사용자가 선택한 값 (set 사용)
        
        # 선택 해제 로직 추가 (이미 선택된 성격이면 제거)
        for personality in selected_values:
            if personality in self.parent_view.selected_personalities:
                self.parent_view.selected_personalities.remove(personality)  # 🔹 기존 선택값 삭제
            else:
                if len(self.parent_view.selected_personalities) >= 4:
                    await interaction.response.send_message("❌ 최대 4개의 성격만 선택할 수 있습니다.", ephemeral=True)
                    return
                self.parent_view.selected_personalities.add(personality)  # 🔹 새 선택값 추가

        # UI 업데이트
        selected_list = ", ".join(self.parent_view.selected_personalities) if self.parent_view.selected_personalities else "없음"
        await interaction.response.send_message(f"✅ 현재 선택된 성격: `{selected_list}`", ephemeral=True)
