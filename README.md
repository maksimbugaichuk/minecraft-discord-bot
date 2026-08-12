# Minecraft Server Status Bot

A Discord bot I made that keeps track of a Minecraft server and posts a live status message in your discord, shows if it's online or offline, how many players are on, and the version. No need to check a website or ping it manually, the bot just updates the message every minute.

German version: README.de.md

## What it does

You run one command and the bot sets everything up for you:

- creates a text channel called #server-activity
- creates a role that controls who can see that channel
- posts a message in the channel showing the server status
- updates that same message every 60 seconds instead of spamming new ones
- saves the server address in a database so it remembers it after restarts

It also works per Discord server, so if you add the bot to multiple servers each one can track a different Minecraft server.

## Commands

!setup <host> [port] - admin only, sets up the channel/role and starts tracking the given server. port defaults to 25565 if you don't type one.

!info - gives you the role so you can see the status channel.

## How it's built

- Python 3.12
- discord.py for the bot itself, using the tasks.loop from discord.ext for the background update loop
- mcstatus to actually query the minecraft server
- sqlite3 to store server address, channel id, role id etc per Discord server
- python-dotenv so the bot token isn't hardcoded

## Setup

Clone it, install requirements:

```
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
python -m venv venv
venv\Scripts\activate   (or source venv/bin/activate on mac/linux)
pip install -r requirements.txt
```

Then make a bot in the Discord developer portal (discord.com/developers/applications), grab the token, and turn on these intents under the Bot tab:
- message content intent
- server members intent

When inviting the bot with OAuth2, give it these permissions: manage roles, manage channels, send messages, read message history.

Make a .env file in the project folder with:

```
DISCORD_TOKEN=your_token_here
```

Then just run:

```
python bot.py
```

The database file gets created automatically the first time you run it.

## How the update loop works

Every 60 seconds the bot goes through every server it's tracking (from the database), pings each one with mcstatus, and edits the existing status message instead of sending a new one. If one server is offline or unreachable it just shows offline for that one, it doesn't stop the loop for the others.

## Stuff that's not done yet / things I'd add

- a command to remove the setup (right now if you run !setup twice it just makes a second role and channel, there's no cleanup)

## Why I made this

I'm in 10th grade in Germany and looking for an Ausbildung as a software developer in Berlin, so I wanted something for my portfolio that actually does something end to end, talks to an external API, runs in the background, saves data, and deals with discord permissions and roles.

## License

MIT, do whatever you want with it.
