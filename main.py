import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import sqlite3
from mcstatus import JavaServer

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

DB_FILE = "bot_data.db"

def init_db():
    """Initializes the database table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,
            role_id INTEGER,
            channel_id INTEGER,
            message_id INTEGER,
            mc_host TEXT,
            mc_port INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_all_guilds():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT guild_id, role_id, channel_id, message_id, mc_host, mc_port FROM guild_settings")
    rows = c.fetchall()
    conn.close()
    return rows

def get_guild_settings(guild_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role_id, channel_id, message_id, mc_host, mc_port FROM guild_settings WHERE guild_id = ?", (guild_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_guild_settings(guild_id, role_id, channel_id, message_id, mc_host, mc_port):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO guild_settings (guild_id, role_id, channel_id, message_id, mc_host, mc_port)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (guild_id, role_id, channel_id, message_id, mc_host, mc_port))
    conn.commit()
    conn.close()

init_db()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    if not update_minecraft_status.is_running():
        update_minecraft_status.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)



@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, host: str, port: int = 25565):
    """Sets up the tracking system for this specific discord server's minecraft server"""
    guild = ctx.guild
    await ctx.send("⏳ Setting up channels and roles, please wait...")

    try:
        role_name = "Server Info Access"
        new_role = await guild.create_role(
            name=role_name,
            color=discord.Color.green(),
            mentionable=True,
            reason="Created automatically via !setup."
        )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            new_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name="server-activity",
            overwrites=overwrites,
            reason="Created automatically via !setup."
        )

        embed = discord.Embed(title="Minecraft Server Status", description="Loading data...", color=discord.Color.dark_gray())
        message = await channel.send(embed=embed)

        # Save everything to SQLite database
        save_guild_settings(guild.id, new_role.id, channel.id, message.id, host, port)

        await ctx.send(f"Setup complete! Created channel {channel.mention} for Minecraft server `{host}:{port}`.")

    except Exception as e:
        await ctx.send(f"Setup failed: {e}")

@tasks.loop(seconds=60)
async def update_minecraft_status():
    """Loops through all registered guilds in the database, pings their specific minecraft server and updates messages"""
    all_guilds = get_all_guilds()
    if not all_guilds:
        return

    for guild_id, role_id, channel_id, message_id, mc_host, mc_port in all_guilds:
        try:
            server = JavaServer(mc_host, mc_port)
            status = server.status()

            player_count = status.players.online
            max_players = status.players.max
            version = status.version.name

            embed = discord.Embed(title="Minecraft Server Status", color=discord.Color.green())
            embed.add_field(name="Status", value="🟢 Online", inline=False)
            embed.add_field(name="Players", value=f"{player_count}/{max_players}", inline=True)
            embed.add_field(name="Version", value=version, inline=True)
        except Exception as e:
            embed = discord.Embed(title="Minecraft Server Status", color=discord.Color.red())
            embed.add_field(name="Status", value="🔴 Offline", inline=False)
            embed.add_field(name="Players", value="0/0", inline=True)
            print(f"Ping failed for guild {guild_id} ({mc_host}:{mc_port}): {e}")

        try:
            channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
            if channel:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
        except Exception as e:
            print(f"Could not update message for guild {guild_id}: {e}")

@update_minecraft_status.before_loop
async def before_update():
    await bot.wait_until_ready()

@bot.command()
async def info(ctx: commands.Context):
    """Assigns the created role to the user who ran the command"""
    guild = ctx.guild
    member = ctx.author

    settings = get_guild_settings(guild.id)
    if not settings:
        await ctx.send("This server hasn't been set up yet. An admin needs to run `!setup <ip>`.")
        return

    role_id = settings[0]
    role = guild.get_role(role_id)

    if role:
        if role in member.roles:
            await ctx.send(f"You already have the {role.name} role!")
        else:
            try:
                await member.add_roles(role)
                await ctx.send(f"Success! You have been given the **{role.name}** role.")
            except discord.Forbidden:
                await ctx.send("I don't have permission to assign that role. Check my role hierarchy position!")
    else:
        await ctx.send("I couldn't find the custom role. It might have been deleted.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
