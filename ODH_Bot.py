import os
import discord
import openai
import subprocess
import re
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks

global bot_active


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

bot_version = "ODH bot version 1.0.9"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="Echo", intents=intents)
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

    if bot_active:
        if should_reply(message):
            prompt = f"User: {message.content}"
            response = await get_chatgpt_response(prompt)
            await message.channel.send(response)

    await bot.process_commands(message)

#@bot.command(name="ODH")
#async def ask(ctx, *, question):
#    response = await on_message(question)
#    await ctx.send(response)

@bot.command(name="ask")
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

@bot.command(name="update_bot")
async def update_bot(ctx):
    if ctx.message.author.id == 472828401619697664:
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Updating the bot, please wait...")
            git_pull = subprocess.Popen("git pull", cwd=os.getcwd(), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = git_pull.communicate()
            os._exit(1)
            await ctx.send(f"Update result:\n{stdout.decode('utf-8')}\n{stderr.decode('utf-8')}")
            await ctx.send("Restarting the bot...")
            await bot.close()
        else:
            await ctx.send("This command can only be used in a DM with the bot.")
    else:
        await ctx.send("You don't have permission to use this command.")



# Rest of your bot code

bot.run(TOKEN)
