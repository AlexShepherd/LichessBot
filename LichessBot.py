import discord
from discord.ext import tasks
import datetime
import requests
import json
import chess
import chess.pgn
import pgntofen
import os
from dotenv import load_dotenv
import schedule
import time

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
puzzleTime = datetime.time(hour=12, minute = 00, second = 30)

r = requests.get("https://lichess.org/api/puzzle/daily").json()
y = json.dumps(r)

solutionStartLoc = y.find("solution")
themeStartLoc = y.find("theme")
solution = y[solutionStartLoc:themeStartLoc]
cleanSolution = solution[13:-5]
cleanerSolution = cleanSolution.replace('"', "")
finalSolution = cleanerSolution.replace(',', '')
maskedSolution = "||" + finalSolution + "||"
accepted_solutions = {finalSolution, maskedSolution}

input = str(finalSolution)

pgnstartloc = y.find("pgn")
clockstartloc = y.find("clock")
pgn = y[pgnstartloc:clockstartloc]
cleanpgn = pgn[7:-4]

pgnConverter = pgntofen.PgnToFen()
pgnConverter.pgnToFen(cleanpgn.split(' '))
fen = pgnConverter.getFullFen()
cleanFen = fen[:-6]
URL = "https://fen2image.chessvision.ai/"
fenURL = URL + cleanFen

numSpaces = cleanpgn.count(" ")
if(numSpaces % 2 == 0):
    blackTrailer = '?turn=black&pov=black'
    fenURL += blackTrailer
else:
    whiteTrailer = '?turn=white&pov=white'
    fenURL += whiteTrailer

def job():
    schedule.every(4).hours.do(r = requests.get("https://lichess.org/api/puzzle/daily").json())
    while True:
        schedule.run_pending()
        time.sleep(1)

@tasks.loop(time=puzzleTime)
async def PostPuzzle():
    channel = client.get_channel(os.getenv("TNCORD-CHESS-CHANNEL"))
    await channel.send(fenURL)
    
@client.event
async def on_message(message):
    reply_author = None if message.reference is None or client.get_channel(message.reference.channel_id) is None  \
    else (await client.get_channel(message.reference.channel_id).fetch_message(message.reference.message_id)).author
    if client.user in message.mentions and reply_author == client.user:
        if message.content.lower() in accepted_solutions:
            await message.add_reaction("✅")
        else: await message.add_reaction("❌")

@client.event
async def on_ready():
    if not PostPuzzle.is_running():
        PostPuzzle.start()
        print("Post puzzle task started")

client.run(os.getenv("TOKEN"))
