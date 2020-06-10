import os
from dotenv import load_dotenv

def getFirebaseToken():
    load_dotenv()
    return os.getenv('FIREBASE_TOKEN')

def getDiscordToken():
    load_dotenv()
    return os.getenv('DISCORD_TOKEN')