import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1231624308615286815
VERIFIER_IDS = [1364297362079744143, 974792041315856464]
VERIFY_ROLE_MAP = {
    "Cabin Crew": "Cabin Crew Programme",
    "Ground Crew": "Ground Crew Programme",
    "Flight Deck": "Flight Deck Programme"
}

EMOJIS = {
    "LOTTail_Left": "<:LOTTail_Left:1393593666047709184>",
    "Tick": "<:Tick:1393593750072332381>",
    "Cross": "<:Cross:1393593491845808228>",
    "Arrow2": "<:Arrow2:1393593463848701972>",
    "Divider": "<:Divider:1393593530596855839>"
}

handled_requests = set()

class DenyReasonModal(Modal, title="Reason for Denial"):
    reason = TextInput(label="State your reason", required=False, max_length=300)

    def __init__(self, trainee, message, interaction):
        super().__init__()
        self.trainee = trainee
        self.message = message
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        await self.trainee.send(
            f"{EMOJIS['LOTTail_Left']} **Your verification request has been denied**\n\n"
            f"Dear, {self.trainee.mention},\n\n"
            f"{EMOJIS['Arrow2']} A member of the Academy Oversight has {EMOJIS['Cross']} **denied** your request.\n\n"
            f"{EMOJIS['Divider']} __Reason__: {self.reason.value if self.reason.value else 'Not provided'}"
        )
        await self.trainee.kick(reason="Verification Denied")
        await self.message.reply(f"{EMOJIS['Cross']} {self.trainee.mention}'s request has been denied and trainee has been kicked.")

@bot.tree.command(name="verify", description="Submit a verification request", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    roblox_username="Enter your Roblox username",
    department="Select your department",
    enrolment_date="Date of enrollment (e.g., 13 July 2025)"
)
@app_commands.choices(department=[
    app_commands.Choice(name="Cabin Crew", value="Cabin Crew"),
    app_commands.Choice(name="Ground Crew", value="Ground Crew"),
    app_commands.Choice(name="Flight Deck", value="Flight Deck")
])
async def verify(interaction: discord.Interaction, roblox_username: str, department: app_commands.Choice[str], enrolment_date: str):
    trainee = interaction.user

    request_text = (
        f"{EMOJIS['LOTTail_Left']} **New Verification Request**\n\n"
        f"Roblox Username: `{roblox_username}`\n"
        f"Training Department: `{department.name}`\n"
        f"Date of Enrollment: `{enrolment_date}`\n\n"
        f"**If {EMOJIS['Tick']} approved**, please be sure to rank them in the Roblox Group."
    )

    async def handle_reactions(message):
        await message.add_reaction(EMOJIS['Tick'])
        await message.add_reaction(EMOJIS['Cross'])

        def check(reaction, user):
            return user.id in VERIFIER_IDS and str(reaction.emoji) in [EMOJIS['Tick'], EMOJIS['Cross']] and reaction.message.id == message.id

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=300, check=check)
        except:
            return

        if message.id in handled_requests:
            await message.reply(f"This request has already been handled.")
            return

        handled_requests.add(message.id)

        if str(reaction.emoji) == EMOJIS['Tick']:
            guild = bot.get_guild(GUILD_ID)
            roles = [discord.utils.get(guild.roles, name=r) for r in ["LOT Academy", "Verified", VERIFY_ROLE_MAP[department.name], "Base Training In Progress"]]
            for role in roles:
                if role:
                    await trainee.add_roles(role)

            await trainee.send(
                f"{EMOJIS['LOTTail_Left']} **You have been successfully enrolled in the LOT Flight Academy, Welcome Aboard**\n\n"
                f"Dear, {trainee.mention},\n\n"
                f"{EMOJIS['Arrow2']} A member of the Academy Oversight has {EMOJIS['Tick']} **approved** your request.\n\n"
                f"__Trainee's Roblox Username__: `{roblox_username}`\n"
                f"__Date of Enrollment__: `{enrolment_date}`\n"
                f"__Training Department__: `{department.name}`"
            )
            await message.reply(f"{EMOJIS['Tick']} {trainee.mention} has been approved. Please rank them in the group.")

        elif str(reaction.emoji) == EMOJIS['Cross']:
            await interaction.response.send_modal(DenyReasonModal(trainee, message, interaction))

    for verifier_id in VERIFIER_IDS:
        user = await bot.fetch_user(verifier_id)
        dm = await user.send(request_text)
        await handle_reactions(dm)

    await interaction.response.send_message(f"{EMOJIS['Tick']} Your verification request has been sent to Academy Oversight.", ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    print(f"🤖 Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run("MTM5MzU5MjEwODY0ODIzNTEyOA.G9ucuU.chC1uBYVgMkFX2fHqs8iC27pB4crrevU0S3vfc")