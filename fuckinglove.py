import discord
from discord.ext import commands
from discord import app_commands
import asyncio

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
    "LOTTail_Left": "<:LOTTail_Left:1393593666047709184>",
    "Arrow2": "<:Arrow2:1393593463848701972>",
    "Tick": "<:Tick:1393593750072332381>",
    "Cross": "<:Cross:1393593491845808228>",
    "Dot": "<:Dot:1393593394231513198>",
    "Academy": "<:Academy:1393593606027350036>",
    "Divider": "<:Divider:1393593530596855839>",
    "Dash": "<:Dash:1393593510506139741>",
    "LogoBlue": "<:LogoBlue:1393980615526846595>",
    "Documents": "<:Documents:1393593547315478549>",
    "Announcement": "<:Announcement:1393593323586850957>",
    "Link": "<:Link:1393995752702869585>"
}

ROLE_IDS = {
    "Base": 1232757036249514114,
    "Departmental": 1231627662783549570
}

def is_authorized(user):
    return user.id in AUTHORIZED_USER_IDS

@bot.event
async def on_ready():
    if not getattr(bot, "synced", False):
        bot.synced = True
        try:
            synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"✅ Synced {len(synced)} command(s) for {bot.user}")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")

@bot.tree.command(name="joiningtime", description="Announce joining time for a session", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    airport="Full name of the airport",
    link="Teleport/game link to the session",
    channel="Channel to post the joining time message",
    training_type="Select training type"
)
@app_commands.choices(training_type=[
    app_commands.Choice(name="Base", value="Base"),
    app_commands.Choice(name="Departmental", value="Departmental")
])
async def joiningtime(
    interaction: discord.Interaction,
    airport: str,
    link: str,
    channel: discord.TextChannel,
    training_type: app_commands.Choice[str]
):
    if not is_authorized(interaction.user):
        await interaction.response.send_message(f"{EMOJIS['Cross']} You are not authorized to use this command.", ephemeral=True)
        return

    role_id = ROLE_IDS[training_type.value]
    ghost_ping = await channel.send(f"<@&{role_id}>")
    await ghost_ping.delete()

    joining_message = (
        f"{EMOJIS['LogoBlue']} **Joining Time**, *czas dołączenia*\n\n"
        f"{EMOJIS['Arrow2']} **{airport}** is now open for all LOT Flight Academy students.\n"
        f"> {EMOJIS['Link']} **[{airport}]({link})**\n\n"
        f"{EMOJIS['Divider']} {EMOJIS['Dash']} The server will automatically lock in **5 minutes** time. "
        f"After the lock time, you will no longer be able to access this session."
    )

    await channel.send(joining_message)
    await interaction.response.send_message(f"{EMOJIS['Tick']} Session Scheduled in {channel.mention}.", ephemeral=True)

    await asyncio.sleep(300)  # 5 minutes

    lock_message = f"{EMOJIS['Announcement']} The **training server** is now {EMOJIS['Cross']} **locked**."
    await channel.send(lock_message)

# Run the bot
if __name__ == "__main__":
    bot.run("MTM5MzU5MjEwODY0ODIzNTEyOA.G9ucuU.chC1uBYVgMkFX2fHqs8iC27pB4crrevU0S3vfc")