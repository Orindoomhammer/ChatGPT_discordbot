import os
import discord
import openai
import subprocess
import re
import sys
import youtube_dl
from discord import FFmpegPCMAudio
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks

def install_missing_packages():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        exit(1)

install_missing_packages()

load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BOT_NAME = os.environ.get("BOT_NAME")
DISCORD_USER_ID = int(os.environ.get("DISCORD_USER_ID"))
TOPICS = os.environ.get("TOPICS")




bot_version = "ODH bot version 1.0.18"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="Echo ", intents=intents)
openai.api_key = OPENAI_API_KEY

def get_git_commit_hash():
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Error getting git commit hash: {e}")
        return None

bot_active = True

def decode_escapes(s):
    return s.encode('utf-8').decode('unicode_escape')

PERSONALITY = decode_escapes(os.environ.get("PERSONALITY"))
RULES = decode_escapes(os.environ.get("RULES"))

@bot.command(name="toggle")
@commands.has_permissions(administrator=True)
async def toggle(ctx):
    global bot_active
    bot_active = not bot_active
    status = "active" if bot_active else "inactive"
    await ctx.send(f"Bot is now {status}.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot_active:
        # Your bot's normal message handling logic here
        pass

    await bot.process_commands(message)

def should_reply(message):
    if message.author == bot.user:
        return False

    if message.content.startswith('!'):
        return False

    if message.content.startswith('@'):
        return False

    # Assuming TOPICS is a list of topics, you can check if any topic is present in the message content
    for topic in TOPICS:
        if topic.lower() in message.content.lower():
            return True

    return BOT_NAME.lower() in message.content.lower()


@bot.command()
async def V(ctx):
    prompt = "Generate a random Russian phrase about updating the bot."
    random_russian_phrase = await get_chatgpt_response(prompt)
    await ctx.send(f"Bot version: {bot_version} - {random_russian_phrase}")


@bot.command(name="You_have_an_update")
async def update_bot(ctx):
    if ctx.message.author.id == DISCORD_USER_ID:
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("As you wish, my lord. Updating the bot, please wait...")

            try:
                subprocess.run(["git", "fetch", "--all"], check=True)
                subprocess.run(["git", "reset", "--hard", "origin/master"], check=True)

                await ctx.send("The bot has been updated, and the Jedi have been defeated. Restarting...")
            except subprocess.CalledProcessError as e:
                await ctx.send(f"An unexpected disturbance in the Force: {e}")

            await bot.close()
            sys.exit(1)
        else:
            await ctx.send("This command can only be used in a DM with the bot, my lord.")
    else:
        await ctx.send("I'm sorry, but you don't have the authority to execute Order 66.")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(682742469766807606)  # Replace YOUR_WELCOME_CHANNEL_ID with the actual channel ID
    welcome_message = f"Welcome {member.mention}! We're happy to have you here!"
    await channel.send(welcome_message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for slurs in the message content
    #if any(slur.lower() in message.content.lower() for slur in SLURS):
        # Delete the message
    #    await message.delete()
    #else:
        # Process the message as usual
     #   pass


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if should_reply(message):
        prompt = f"User: {message.content}"
        response = await get_chatgpt_response(prompt)
        response = response.replace("Echo:", "", 1).strip()
        await message.channel.send(response)


    await bot.process_commands(message)

async def get_chatgpt_response(prompt, conversation_history=None):
    model_engine = "gpt-3.5-turbo-0301"
    personality = (PERSONALITY)

    if conversation_history:
        prompt = f"{personality}\n\n{conversation_history}\n\n{prompt}"
    else:
        prompt = f"{personality}\n\n{prompt}"

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    return message

commit_hash = get_git_commit_hash()
if commit_hash:
    print(f"Bot is running on commit: {commit_hash}")


bot.run(TOKEN)
