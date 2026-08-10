import os
import time
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

xp_data = {}
last_xp = {}

XP_COOLDOWN = 60


@bot.event
async def on_ready():
    print(f"Fino giriş yaptı: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    now = time.time()

    if user_id not in xp_data:
        xp_data[user_id] = 0

    if now - last_xp.get(user_id, 0) >= XP_COOLDOWN:
        xp_data[user_id] += 10
        last_xp[user_id] = now

    await bot.process_commands(message)


@bot.command()
async def rank(ctx):
    user_id = ctx.author.id
    xp = xp_data.get(user_id, 0)

    sorted_users = sorted(
        xp_data.items(),
        key=lambda item: item[1],
        reverse=True
    )

    rank_number = next(
        (i for i, (uid, _) in enumerate(sorted_users, start=1)
         if uid == user_id),
        1
    )

    embed = discord.Embed(
        title=ctx.author.display_name,
        description=(
            f"Rank #{rank_number}\n"
            f"Rütbe #{xp // 100 + 1}\n\n"
            f"XP: {xp}"
        ),
        color=discord.Color.dark_grey()
    )

    embed.set_thumbnail(url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)


bot.run(TOKEN)
