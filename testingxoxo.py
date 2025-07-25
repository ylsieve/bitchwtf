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
    "Academy": "<:Academy:1373036077748715601>",
    "LogoBlue": "<:LogoBlue:1393980615526846595>",
    "Divider": "<:Divider:1393593530596855839>",
    "Heart": "<:Heart:1393593572380377208>"
}

ROLE_IDS = {
    "base": 1232757036249514114,
    "departmental": 1231627662783549570
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
async def base_exam_result(interaction: discord.Interaction, user: discord.Member, greeting: str, exam_type: str, outcome: str, points: float, max_points: float, attempts: int):
    if not is_authorized(interaction.user):
        await interaction.response.send_message(f"{EMOJIS['Cross']} You are not authorized to use this command.", ephemeral=True)
        return

    exam_type = exam_type.lower()
    outcome = outcome.lower()
    percentage = round((points / max_points) * 100, 2)
    exam_title = "Base Theoretical Examination" if exam_type == "theory" else "Base Practical Examination"

    msg = f"{EMOJIS['LOTTail_Left']} **{exam_title} Results**\n\n"
    msg += f"{greeting} {user.mention},\n\n"
    msg += f"{EMOJIS['Arrow2']} I am __pleased__ to inform you that your __{exam_title}__ has been thoroughly graded and you have "

    if outcome == "pass":
        msg += f"{EMOJIS['Tick']} **passed**. "
        msg += "To receive individual feedback, please direct message a member of the Academy Oversight Team.\n\n" if exam_type == "practical" else "Detailed feedback is provided in the email you provided; please do check your inbox.\n\n"
    else:
        msg += f"{EMOJIS['Cross']} **failed**. "
        msg += "To receive individual feedback, please direct message a member of the Academy Oversight Team.\n\n" if exam_type == "practical" else "Detailed feedback is provided in the email you provided; please do check your inbox.\n\n"

    msg += (
        f"{EMOJIS['Dot']} __Points Scored__: {points}/{max_points}\n"
        f"{EMOJIS['Dot']} __Percentage__: {percentage}%\n"
        f"{EMOJIS['Dot']} __Final Outcome__: "
    )
    msg += f"{EMOJIS['Tick']} **Pass**\n\n" if outcome == "pass" else f"{EMOJIS['Cross']} **Fail**\n\n"

    if outcome == "pass":
        if exam_type == "theory":
            msg += "You are now eligible to take your Base Practical Examination, thank you & good luck."
        else:
            msg += f"This will result you to obtain the {EMOJIS['Academy']} **Base Training Completed Certification**. You will now be able to begin training in your department. If you have any questions, do not hesitate to ask. Thank you for choosing LOT Polish Airlines."
    else:
        if attempts >= 3:
            msg += "You have been **dismissed** from the LOT Flight Academy due to failing the exam three times in a row. You are allowed to apply for the upcoming hiring waves, thank you & good luck."
        else:
            msg += f"You will not be able to move on with the course until you have re-attempt the examination & pass. Please note that three failures strikes in **dismissal** from {EMOJIS['Academy']} LOT Flight Academy."

    try:
        await user.send(msg)
        await interaction.response.send_message(f"{EMOJIS['Tick']} Sent exam result to {user.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"{EMOJIS['Cross']} Could not DM {user.mention}. Please ask them to enable DMs.", ephemeral=True)

# --- DEPARTMENT EXAM RESULT ---
@bot.tree.command(name="department-exam-result", description="Send Department Exam Result", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    user="Trainee to DM result to",
    greeting="Dzień dobry or Dobry wieczór",
    exam_type="Theoretical or Practical",
    outcome="Pass or Fail",
    points="Points scored by trainee",
    max_points="Maximum points of exam",
    department="Cabin Crew, Ground Crew, or Flight Deck",
    failed_three_times="Has the trainee failed 3 times?",
    personnel_invite="Personnel server invite (if passed)",
    department_invite="Department server invite (optional, if passed)"
)
async def department_exam_result(
    interaction: discord.Interaction,
    user: discord.Member,
    greeting: str,
    exam_type: str,
    outcome: str,
    points: float,
    max_points: float,
    department: str,
    failed_three_times: bool = False,
    personnel_invite: str = None,
    department_invite: str = None
):
    if not is_authorized(interaction.user):
        await interaction.response.send_message(f"{EMOJIS['Cross']} You are not authorized to use this command.", ephemeral=True)
        return

    percentage = round((points / max_points) * 100, 2)
    exam_type_lower = exam_type.lower()
    department_title = department.title()
    exam_full_title = "Theoretical Examination" if exam_type_lower == "theoretical" else "Practical Examination"
    exam_result_title = f"{department_title} {exam_full_title}"

    if outcome.lower() == "pass":
        msg = (
            f"{EMOJIS['LOTTail_Left']} **{exam_result_title} Results**\n\n"
            f"{greeting} {user.mention},\n\n"
            f"{EMOJIS['Arrow2']} I am __pleased__ to inform you that your __{exam_result_title}__ has been thoroughly graded and you have {EMOJIS['Tick']} **passed**. "
        )
        msg += (
            "Detailed feedback is provided in the email you provided; please do check your inbox.\n\n"
            if exam_type_lower == "theoretical"
            else "To receive individual feedback, please direct message one of the Academy Oversight Team.\n\n"
        )
        msg += (
            f"{EMOJIS['Dot']} __Points Scored__: {points}/{max_points}\n"
            f"{EMOJIS['Dot']} __Percentage__: {percentage}%\n"
            f"{EMOJIS['Dot']} __Final Outcome__: {EMOJIS['Tick']} **Pass**\n\n"
        )
        if exam_type_lower == "theoretical":
            msg += f"You are now eligible to take your {department_title} Practical Examination, thank you & good luck."
        else:
            msg += (
                f"As you now hold official personnel status, we congratulate you for completing our multi-stage training programme. Please join the following server(s):\n"
                f"{personnel_invite or ''}\n{department_invite or ''}"
            )
    else:
        msg = (
            f"{EMOJIS['LOTTail_Left']} **{exam_result_title} Results**\n\n"
            f"{greeting} {user.mention},\n\n"
            f"{EMOJIS['Arrow2']} I am __pleased__ to inform you that your __{exam_result_title}__ has been thoroughly graded and you have {EMOJIS['Cross']} **failed**. "
        )
        msg += (
            "Detailed feedback is provided in the email you provided; please do check your inbox.\n\n"
            if exam_type_lower == "theoretical"
            else "To receive individual feedback, please direct message a member of the Academy Oversight Team.\n\n"
        )
        msg += (
            f"{EMOJIS['Dot']} __Points Scored__: {points}/{max_points}\n"
            f"{EMOJIS['Dot']} __Percentage__: {percentage}%\n"
            f"{EMOJIS['Dot']} __Final Outcome__: {EMOJIS['Cross']} **Fail**\n\n"
        )
        if failed_three_times:
            msg += "You have been **dismissed** from the LOT Flight Academy due to failing the exam three times in a row. You are allowed to apply for the upcoming hiring waves, thank you & good luck."
        else:
            msg += f"You will not be able to move on with the course until you have re-attempt the examination & pass. Please note that three failures strikes in **dismissal** from {EMOJIS['Academy']} LOT Flight Academy."

    try:
        await user.send(msg)
        await interaction.response.send_message(f"{EMOJIS['Tick']} Sent {exam_full_title} Results to {user.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"{EMOJIS['Cross']} Could not DM {user.mention}. Please ask them to enable DMs.", ephemeral=True)

# --- SCHEDULE TRAINING ---
@bot.tree.command(name="schedule-training", description="Schedule a LOT Academy Training Session", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    training_type="Base or Departmental",
    department="Cabin Crew, Ground Crew or Flight Deck (optional)",
    module_number="Training Module Number (1, 2, 3...etc)",
    channel="Channel to send session to",
    instructor="Ping the Training Instructor",
    place_emoji="Emoji for the location",
    place_name="Full name of the location",
    datetime="Training date & time (Discord timestamp)"
)
async def schedule_training(
    interaction: discord.Interaction,
    training_type: str,
    module_number: str,
    channel: discord.TextChannel,
    instructor: str,
    place_emoji: str,
    place_name: str,
    datetime: str,
    department: str = None  # ← This makes it optional
):
    if not is_authorized(interaction.user):
        await interaction.response.send_message(f"{EMOJIS['Cross']} You are not authorized to use this command.", ephemeral=True)
        return

    department_display = f"{department} " if department else ""
    role_ping_id = ROLE_IDS['base'] if training_type.lower() == "base" else ROLE_IDS['departmental']
    role_ping = f"<@&{role_ping_id}>"

    msg = (
        f"{EMOJIS['LogoBlue']} **Scheduled Session**, *nowo zaplanowana sesja*\n\n"
        f"A new {department_display}**Module {module_number}** training session has been scheduled. Please review the details below.\n"
        f"> {EMOJIS['Arrow2']}*Training Instructor*: {instructor}\n"
        f"> {EMOJIS['Arrow2']}*Place*: {place_emoji} {place_name}\n"
        f"> {EMOJIS['Arrow2']}*Date & Time*: {datetime}\n\n"
        f"{EMOJIS['Divider']}{EMOJIS['Academy']} **LOT Flight Academy** is hosting its {department_display}Module {module_number} training session at {place_name}.\n"
        f"{EMOJIS['Arrow2']} __Secure your spot__ now and take a step further to a *rewarding career* in LOT Polish Airlines. {EMOJIS['Heart']}"
    )

    try:
        ping = await channel.send(role_ping)
        await ping.delete()
        sent_msg = await channel.send(msg)
        await sent_msg.add_reaction(EMOJIS['Tick'])
        await interaction.response.send_message(f"{EMOJIS['Tick']} Session Scheduled.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"{EMOJIS['Cross']} Failed to send session message: {e}", ephemeral=True)

# --- RUN THE BOT ---
if __name__ == "__main__":
    bot.run("MTM5MzU5MjEwODY0ODIzNTEyOA.G9ucuU.chC1uBYVgMkFX2fHqs8iC27pB4crrevU0S3vfc")  # Replace with your new token!