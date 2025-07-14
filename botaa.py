import discord
from discord.ext import commands
from discord import app_commands

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

def is_authorized(user):
    return user.id in AUTHORIZED_USER_IDS

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} command(s). Bot is ready: {bot.user}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# --- BASE EXAM RESULT ---
@bot.tree.command(name="base-exam-result", description="Send result of Base Theoretical or Practical Exam", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    user="Trainee to DM",
    greeting="Greeting (Dzień dobry or Dobry wieczór)",
    exam_type="theory or practical",
    outcome="pass or fail",
    points="Points scored",
    max_points="Max points of exam",
    attempts="How many times they’ve attempted (1, 2 or 3)"
)
async def base_exam_result(
    interaction: discord.Interaction,
    user: discord.Member,
    greeting: str,
    exam_type: str,
    outcome: str,
    points: float,
    max_points: float,
    attempts: int
):
    if not is_authorized(interaction.user):
        await interaction.response.send_message(f"{EMOJIS['Cross']} You are not authorized.", ephemeral=True)
        return

    exam_type = exam_type.lower()
    outcome = outcome.lower()
    percentage = round((points / max_points) * 100, 2)
    exam_title = "Base Theoretical Examination" if exam_type == "theory" else "Base Practical Examination"

    msg = f"{EMOJIS['LOTTail_Left']} **{exam_title} Results**\n\n"
    msg += f"{greeting} {user.mention},\n\n"
    msg += f"{EMOJIS['Arrow2']} I am __pleased__ to inform you that your __{exam_title}__ has been thoroughly graded and you have "
    msg += f"{EMOJIS['Tick']} **passed**. " if outcome == "pass" else f"{EMOJIS['Cross']} **failed**. "
    msg += (
        "To receive individual feedback, please DM an Academy Oversight Team member.\n\n"
        if exam_type == "practical" else
        "Detailed feedback is provided via email. Please check your inbox.\n\n"
    )
    msg += (
        f"{EMOJIS['Dot']} __Points Scored__: {points}/{max_points}\n"
        f"{EMOJIS['Dot']} __Percentage__: {percentage}%\n"
        f"{EMOJIS['Dot']} __Final Outcome__: "
        f"{EMOJIS['Tick']} **Pass**\n\n" if outcome == "pass" else f"{EMOJIS['Cross']} **Fail**\n\n"
    )
    msg += (
        "You are now eligible to take your Base Practical Examination. Good luck!"
        if outcome == "pass" and exam_type == "theory" else
        f"This will result in receiving the {EMOJIS['Academy']} **Base Training Completed Certification**. You can now begin department training."
        if outcome == "pass" else
        "You are not allowed to proceed until passing. Failing 3 times = dismissal from Academy."
        if attempts < 3 else
        "You have been **dismissed** from the LOT Flight Academy. You may apply in future hiring waves."
    )

    try:
        await user.send(msg)
        await interaction.response.send_message(f"{EMOJIS['Tick']} Sent exam result to {user.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"{EMOJIS['Cross']} Could not DM {user.mention}.", ephemeral=True)

# You can copy the same approach to department_exam_result if needed.

# Run the bot
bot.run("MTM5MzU5MjEwODY0ODIzNTEyOA.GCuyGZ.O3TIEek3Q-6LKtyXsSdu0Pyvd96YB76RsKM2BY")