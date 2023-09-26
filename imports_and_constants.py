# the chain starts here
import nextcord
import asyncio
import threading
import time
import os
import sys
import random
import json
import requests
import datetime
import multiprocessing
import shutil
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(intents=intents)

owner_id = 315851790967111680

