import os
import discord
import openai
import subprocess
import re
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

# Your bot code here

load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot_version = "ODH bot version 1.0.4"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
openai.api_key = OPENAI_API_KEY

@bot.command()
async def V(ctx):
    await ctx.send(f"Bot version: {bot_version} - Now with more awesomeness!")


def should_reply(message):
    # Add any conditions or keywords to check if the bot should reply to a message
    keywords = ['AI', 'technology', 'chatbot', 'bot', 'Hello', 'anyone around?']
    for keyword in keywords:
        if keyword.lower() in message.content.lower():
            return True
    return False

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if should_reply(message):
        prompt = f"User: {message.content}"
        response = await get_chatgpt_response(prompt)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command(name="ODH")
async def ask(ctx, *, question):
    response = await get_chatgpt_response(question)
    await ctx.send(response)

@bot.command()
async def code(ctx, *, request: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides code snippets."},
            {"role": "user", "content": request},
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    answer = response.choices[0].message['content']
    code_snippet = re.findall(r"```[\s\S]*?```", answer)
    if code_snippet:
        await ctx.send(code_snippet[0])
    else:
        await ctx.send("I couldn't find a relevant code snippet for your request.")

# Rest of your bot code

bot.run(TOKEN)
