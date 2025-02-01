import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONFESSION_CHANNEL_ID = os.getenv("CONFESSION_CHANNEL_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
COOLDOWN_TIME = os.getenv("COOLDOWN_TIME")

print(BOT_TOKEN)
print(LOG_CHANNEL_ID)
print(CONFESSION_CHANNEL_ID)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.dm_messages = True
bot = commands.Bot(command_prefix=".", intents=intents)
tree = bot.tree

cooldowns = {}

@bot.event
async def on_ready():
    print(f'Logged in as The Boba Booth')
    activity = discord.Activity(type=discord.ActivityType.listening, name="/confess")
    await bot.change_presence(activity=activity)
    await tree.sync()
    print("Slash commands synced!")

@tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! The Boba Booth is online! 🧋", ephemeral=True)

@tree.command(name="confess", description="Send an anonymous confession")
async def confess(interaction: discord.Interaction, title: str, confession: str):
    if isinstance(interaction.channel, discord.DMChannel):
        user_id = interaction.user.id
        current_time = asyncio.get_event_loop().time()

        if user_id in cooldowns and (current_time - cooldowns[user_id]) < COOLDOWN_TIME:
            await interaction.response.send_message("⏳ Please wait before submitting another confession! 🍵", ephemeral=True)
            return

        try:
            confession_channel = await bot.fetch_channel(CONFESSION_CHANNEL_ID)
            log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except discord.NotFound:
            await interaction.response.send_message("❌ Error: Channels not found. Please check your configuration.", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("❌ Error: Bot lacks permission to access the channels.", ephemeral=True)
            return

        if confession_channel and log_channel:
            confession_embed = discord.Embed(
                title=f"🧋 {title} 🧋",
                description=confession,
                color=discord.Color.purple()
            )
            await confession_channel.send(embed=confession_embed)

            log_embed = discord.Embed(
                title="📝 Boba Confession Logged 📝",
                description=f"**Boba Lover:** {interaction.user} ({interaction.user.id})\n**Title:** {title}\n**Confession:** {confession}",
                color=discord.Color.purple()
            )
            await log_channel.send(embed=log_embed)

            await interaction.response.send_message("✅ Your juicy confession has been sent anonymously! 🍹", ephemeral=True)

            cooldowns[user_id] = current_time
        else:
            await interaction.response.send_message("❌ Error: Boba confession or log channel not found. Please contact a board member.", ephemeral=True)

bot.run(BOT_TOKEN)

