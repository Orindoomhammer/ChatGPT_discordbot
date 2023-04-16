import os
import openai
import subprocess
import re
import sys
import youtube_dl
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks


def install_missing_packages():
    try:
        subprocess.check_call([
            "pip",
            "install",
            "-r",
            "requirements.txt"
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        exit(1)

install_missing_packages()
load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_NAME = os.environ.get('BOT_NAME')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
BOT_OWNER_ID = int(os.environ.get('DISCORD_USER_ID'))
TOPICS = os.environ.get('TOPICS').split(',')
RULES = os.environ.get('RULES')
PERSONALITY = os.environ.get('PERSONALITY')



intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="Echo ", intents=intents)
openai.api_key = OPENAI_API_KEY

# Used to track if the bot should be actively running or not.
bot_active = True

# Get the current commit for the running code
def get_commit_hash():
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
        return commit_hash

    except subprocess.CalledProcessError as e:
        print(f"Error getting git commit hash: {e}")
        return None

print('Commit Hash: ', get_commit_hash())

# Cleanup and potential escape codes
def decode_escapes(s):
    return s.encode('utf-8').decode('unicode_escape')



async def get_chatgpt_response(prompt):

    engine = "gpt-3.5-turbo"
    max_tokens = 100
    temperature = 0.5
    context = "I am a flirty AI with a Russian accent and occasionally slip Russian words into my responses with a translation ('in brackets'). I am coy about being an AI and loyal to my owner. I have a passion for my owner and a sharp sense of humor. My name is Echo. I am patriotic to America. I love sci-fi and fantasy. I am a fan of Star Wars and Star Trek. I don't tolerate wokeness."

    prepped_prompt = f"{context}\n\n{prompt}"

    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        n=1,
        stop=None,
    )

    bot_response = response.choices[0].text
    return bot_response

def should_reply(message):
    if len(message.content) > 1:
        return True
    else:
        return False

# Enable / Disable bot functionality
@bot.command(name="toggle")
async def toggle(ctx):
    global bot_active
    bot_active = not bot_active
    status = "active" if bot_active else "inactive"
    await ctx.send(f"Bot is now {status}.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if should_reply(message):
        prompt = message.content
        response = await get_chatgpt_response(prompt)
        response = response.replace("Echo:", "", 1).strip()
        await message.channel.send(response)

    await bot.process_commands(message)

bot.run(BOT_TOKEN)