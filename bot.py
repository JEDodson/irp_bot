import os
from re import search
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import logging
import praw
import requests

logging.basicConfig(format="%(asctime)s"+" "*20+"%(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()
D_TOKEN = os.getenv("DISCORD_TOKEN")
R_ID = os.getenv("R_ID")
R_SECRET = os.getenv("R_SECRET")
r = praw.Reddit(
    client_id=R_ID,
    client_secret=R_SECRET,
    user_agent="I-RP Bot's random meme grabber"
)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord.\n")


@bot.event
async def on_member_join(member):
    strings = (
        f"Hi, {member.name}, welcome to IRP!"
        "Introductory sample message here"
    )

    logger.info(f"User connected: {member.name}, sending a DM..")
    await member.create_dm()
    await member.dm_channel.send(strings)


@bot.event
async def on_message(msg):
    await bot.process_commands(msg)

    if msg.author == bot.user:
        return


class FunCommands(commands.Cog):
    # rolls a random nmumber between two specified integers
    @commands.command(name="roll", help=("Rolls a random number between "
                                         "two given numbers. Must be "
                                         "integers."))
    async def roll(self, ctx, start, end):
        author = ctx.author
        logger.info(f"Running roll command, triggered by {author}")
        try:
            n = random.randint(int(start), int(end))
        except ValueError:
            await ctx.send("Please enter two numbers (integers), e.g. 1-6!")
        else:
            await ctx.send(f"Between {start}-{end}, {author} rolled: {n}!")

    @commands.command(name="meme", help="Grabs a meme from /r/memes")
    async def meme(self, ctx):

        author = ctx.author
        logger.info(f"Running meme command, triggered by {author}")

        subreddit = r.subreddit("memes")
        memes = [m for m in subreddit.hot(limit=35)]

        r_num = random.randint(0, 20)
        r_meme = memes[r_num]

        meme_json = f"https://www.reddit.com/r/memes/{r_meme}/.json"
        resp = requests.get(
            url=meme_json,
            headers={"User-agent": "Random Meme Grabber for I-RP"}).json()

        img = resp[0]['data']['children'][0]['data']['url_overridden_by_dest']
        await ctx.send(img)


bot.add_cog(FunCommands())
bot.run(D_TOKEN, bot=True)
