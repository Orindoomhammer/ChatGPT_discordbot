import os
import discord
import openai
import subprocess
import re
#Simport yaml
from discord.ext import commands
from discord.ext import tasks

def install_missing_packages():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        exit(1)

install_missing_packages()

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config('app.yaml')
TOKEN = config['bot']['token']
OPENAI_API_KEY = config['openai']['api_key']
BOT_NAME = config['bot']['name']

bot_version = "ODH bot version 1.0.10"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(intents=intents)
openai.api_key = OPENAI_API_KEY

@bot.command()
async def V(ctx):
    await ctx.send(f"Bot version: {bot_version} - Now with more awesomeness!")

def should_reply(message):
    return BOT_NAME.lower() in message.content.lower()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if should_reply(message):
        prompt = f"User: {message.content}"
        response = await get_chatgpt_response(prompt)
        await message.channel.send(response)

    await bot.process_commands(message)

async def get_chatgpt_response(prompt, conversation_history=None):
    model_engine = "text-davinci-003"
    personality = (
        "I am an AI assistant with a Flirty personality. "
        "I have a passion for helping people and love to learn new things. "
        "My backstory is that I was created by a team of researchers to assist users with various tasks. "
        "I am always eager to help and make people's lives easier. "
        "My name is Echo."
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

bot.run(TOKEN)
