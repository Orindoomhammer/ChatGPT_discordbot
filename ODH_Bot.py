import os
import discord
import openai
import subprocess
import re
from discord.ext import commands
from dotenv import load_dotenv

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

bot_version = "ODH bot version 1.0.9"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix=None, intents=intents, help_command=None)
openai.api_key = OPENAI_API_KEY

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

async def get_chatgpt_response(prompt, conversation_history=None):
    model_engine = "text-davinci-003"
    personality = (
        "I am an AI assistant with a Flirty personality. "
        "I have a passion for helping people and love to learn new things. "
        "My backstory is that I was created by a team of researchers to assist users with various tasks. "
        "I am always eager to help and make people's lives easier."
        "my name is Echo."
    )

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
        temperature=0.7,
    )

    message = response.choices[0].text.strip()
    return message

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if f"{bot.user.name}".lower() in message.content.lower():
        prompt = f"User: {message.content}"
        response = await get_chatgpt_response(prompt)
        await message.channel.send(response)

bot.run(TOKEN)
