import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1231624308615286815
AUTHORIZED_USER_IDS = {
    974792041315856464, 1364297362079744143, 1333951128148381698,
    840293520879386655, 655464957286285352, 696024064384434267,
    733597686351134770, 266108247725834240, 1106565652468211784,
    919516260713234432, 898927651253801021, 1163206127295676478,
    851856544277987349, 1066785549605670942, 739525723789852712
}

EMOJIS = {
    "LOTTail_Left": "<:LOTTail_Left:1379040389108994048>",
    "Arrow2": "<:Arrow2:1231625145051910195>",
    "Tick": "<:Tick:1393593750072332381>",
    "Cross": "<:Cross:1231625431023878154>",
    "Dot": "<:Dot:1231654362447740988>",
    "Academy": "<:Academy:1373036077748715601>"
}

VERIFY_ROLE_MAP = {
    "Cabin Crew": "Cabin Crew Programme",
    "Ground Crew": "Ground Crew Programme",
    "Flight Deck": "Flight Deck Programme"
}

VERIFIER_IDS = [1364297362079744143, 974792041315856464]

class VerifyView(View):
    def __init__(self, trainee: discord.Member, dept: str, timezone: str, roblox_user: str):
        super().__init__(timeout=None)
        self.trainee = trainee
        self.dept = dept
        self.timezone = timezone
        self.roblox_user = roblox_user

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in VERIFIER_IDS:
            await interaction.response.send_message("You are not authorized to approve.", ephemeral=True)
            return

        guild = interaction.guild
        role_names = ["LOT Academy", "Verified", VERIFY_ROLE_MAP[self.dept], "Base Training In Progress"]
        roles = [discord.utils.get(guild.roles, name=role_name) for role_name in role_names]
        for role in roles:
            if role:
                await self.trainee.add_roles(role)

        dm_msg = (
            f"✨ **You're Verified!** ✨\n\n"
            f"{EMOJIS['LOTTail_Left']} Welcome aboard, {self.trainee.mention}!\n"
            f"You've officially been verified for the **{self.dept}** Programme under {EMOJIS['Academy']} LOT Flight Academy.\n"
            f"📍 Timezone: `{self.timezone}`\n💼 Roblox Username: `{self.roblox_user}`\n\n"
            f"You now have access to your training — please await further instructions. 🚀💙"
        )
        await self.trainee.send(dm_msg)

        await interaction.response.send_message(
            f"Approved and roles assigned to {self.trainee.mention}. **Note:** Please manually rank them in the Roblox group. Their username is `{self.roblox_user}`.",
            ephemeral=True
        )

@bot.tree.command(name="verify", description="Verify a new trainee", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    department="Choose training department",
    timezone="Enter your timezone",
    roblox_username="Enter your Roblox username"
)
@app_commands.choices(department=[
    app_commands.Choice(name="Cabin Crew", value="Cabin Crew"),
    app_commands.Choice(name="Ground Crew", value="Ground Crew"),
    app_commands.Choice(name="Flight Deck", value="Flight Deck")
])
async def verify(interaction: discord.Interaction, department: app_commands.Choice[str], timezone: str, roblox_username: str):
    trainee = interaction.user
    for verifier_id in VERIFIER_IDS:
        verifier = await bot.fetch_user(verifier_id)
        embed = discord.Embed(title="📋 New Verification Request", color=0x62c1ff)
        embed.add_field(name="👤 Trainee", value=f"{trainee.mention} ({trainee.name})", inline=False)
        embed.add_field(name="🎓 Department", value=department.name, inline=True)
        embed.add_field(name="🌍 Timezone", value=timezone, inline=True)
        embed.add_field(name="🤖 Roblox Username", value=roblox_username, inline=False)
        view = VerifyView(trainee, department.name, timezone, roblox_username)
        try:
            await verifier.send(embed=embed, view=view)
        except discord.Forbidden:
            await interaction.response.send_message(f"{EMOJIS['Cross']} Could not DM a verifier. Please contact staff.", ephemeral=True)
            return

    await interaction.response.send_message(f"{EMOJIS['Tick']} Your verification request has been sent! You’ll be notified once approved. 🙓", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

if __name__ == "__main__":
    bot.run("MTM5MzUwNTA1Njk2MzQyODQ5Mw.G_Bm57.3QZGWVfwEne5TNh-q05-axJX8FmonnX0M5i6Y8")