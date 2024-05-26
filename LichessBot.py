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

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
puzzleTime = datetime.time(hour=12, minute = 0, second = 0)

r = requests.get("https://lichess.org/api/puzzle/daily").json()
y = json.dumps(r)

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

@tasks.loop(time=puzzleTime)
async def PostPuzzle():
    channel = client.get_channel(os.getenv("TNCORD-CHESS-CHANNEL"))
    
#-----------------TESTING------------------------
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'ping':
        
        await message.channel.send(fenURL)
        
#-----------------TESTING------------------------
@client.event
async def on_ready():
    if not PostPuzzle.is_running():
        PostPuzzle.start()
        print("Post puzzle task started")

client.run(os.getenv("TOKEN"))
