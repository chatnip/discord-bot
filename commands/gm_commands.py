import discord
from discord import app_commands
from database import get_user, add_money, remove_money  # 데이터베이스 함수 가져오기

GM_ROLE_ID = 123456789012345678  # 실제 디스코드 서버의 GM 역할 ID로 변경

class GMCommands(discord.app_commands.Group):
    """GM 전용 명령어 그룹"""

    @app_commands.command(name="재화 지급", description="유저에게 재화를 지급합니다. (GM 전용)")
    async def give_money(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """GM이 유저에게 재화 지급"""
        if GM_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("❌ 이 명령어는 GM만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = str(member.id)

        if amount <= 0:
            await interaction.response.send_message("❌ 지급할 금액은 1 이상이어야 합니다.", ephemeral=True)
            return

        success = add_money(user_id, amount)
        if success:
            galleons = amount // 493
            remainder = amount % 493
            sickles = remainder // 29
            knuts = remainder % 29

            await interaction.response.send_message(
                f"💰 **{member.display_name}** 님에게 `{galleons} 갈레온 {sickles} 시클 {knuts} 크넛` 지급 완료!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ 재화 지급에 실패했습니다.", ephemeral=True)

    @app_commands.command(name="재화 차감", description="유저의 재화를 차감합니다. (GM 전용)")
    async def spend_money(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """GM이 유저 재화를 차감"""
        if GM_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("❌ 이 명령어는 GM만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = str(member.id)

        if amount <= 0:
            await interaction.response.send_message("❌ 차감할 금액은 1 이상이어야 합니다.", ephemeral=True)
            return

        success = remove_money(user_id, amount)
        if success:
            galleons = amount // 493
            remainder = amount % 493
            sickles = remainder // 29
            knuts = remainder % 29

            await interaction.response.send_message(
                f"💸 `{galleons} 갈레온 {sickles} 시클 {knuts} 크넛` 차감 완료!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ 재화 차감에 실패했습니다. 잔액을 확인하세요.", ephemeral=True)

# 명령어 그룹 객체 생성
gm_group = GMCommands(name="gm", description="GM 전용 명령어 그룹")