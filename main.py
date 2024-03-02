import discord
import requests
from bs4 import BeautifulSoup
import re
import os
from discord.ext import commands
import logging
logging.basicConfig(level=logging.DEBUG)
from command_cog import CommandsCog
from music_cog import MusicCog
import aiohttp
import asyncio

# Define the intents you need for your bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True 

# Initialize Discord bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)
#cogs
bot.load_extension('ServerStatusCog')
bot.load_extension('music_cog')
bot.load_extension('command_cog')
# Discord bot token

my_secret = os.environ['TOKEN']
token = my_secret

# URLs
ONLINE_URL = "https://eodash.com/online"
SERVER_STATUS_URL = "https://game.endless-online.com/server.html"
LEADERBOARD_URL = "https://eodash.com/leaderboard"
ITEM_LIST_URL = "https://docs.google.com/spreadsheets/d/1Itfl1YBw2R_mussBFg0F0XqOaOPtWpxQTpG10GG2fS4/edit#gid=1737236281"
GUILDS_URL = "https://eodash.com/guilds"






# Function to scrape guild data
def scrape_guild_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # Skip the header row

        guild_data = []
        for row in rows:
            columns = row.find_all("td")
            rank = columns[0].text.strip()
            guild_name = columns[1].text.strip()
            guild_data.append(f"{rank}\t{guild_name}")

        return guild_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# Function to scrape item data
def scrape_item_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[1:]  # Skip the header row

        item_data = {}
        for row in rows:
            columns = row.find_all("td")
            item_name = columns[1].text.strip().lower()  # Convert to lowercase
            sell_price = columns[-1].text.strip()
            item_data[item_name] = sell_price

        return item_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
      
# Initialize Discord client
bot = commands.Bot(command_prefix='!', intents=intents)


#command list cog
# Load the command cog
bot.load_extension('command_cog')

# Function to check if the name is online
def is_name_online(name):
    try:
        response = requests.get(ONLINE_URL)
        response.raise_for_status()  # Check for successful response

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')

        for row in rows[1:]:  # Skip the first row as it contains the table headers
            columns = row.find_all('td')
            if len(columns) >= 3:  # Check if there are at least three columns
                player_name = columns[0].text.strip()
                player_level = columns[1].text.strip()
                player_exp = columns[2].text.strip()

                if name.lower() == player_name.lower():
                    return f"{player_name} (Level {player_level}) - Current Experience: {player_exp}"

        return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Function to check server status
def get_server_status():
    try:
        response = requests.get(SERVER_STATUS_URL)
        response.raise_for_status()  # Check for successful response

        soup = BeautifulSoup(response.text, 'html.parser')
        status = soup.find('p').text.strip()

        return status

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

#
# Function to fetch top players and their information
def get_top_players():
    try:
        response = requests.get(LEADERBOARD_URL)
        response.raise_for_status()  # Check for successful response

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the rows in the table containing player data
        rows = soup.find_all('tr')

        top_players_data = []
        for row in rows[1:]:  # Skip the first row as it contains the table headers
            columns = row.find_all('td')
            if len(columns) >= 3:  # Check if there are at least three columns
                player_name = columns[0].text.strip()
                player_level = columns[1].text.strip()
                player_exp = columns[2].text.strip()

                # Format the columns to be uniform
                player_name = player_name.ljust(10)  # Adjust the width as needed
                player_level = player_level.ljust(16)  # Adjust the width as needed
                player_exp = player_exp.ljust(10)  # Adjust the width as needed

                top_players_data.append(f"{player_name}{player_level}{player_exp}")

                if len(top_players_data) >= 10:
                    break

        return top_players_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None




# Discord bot event: on ready
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
# Discord bot event: on message received
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()  # Convert message content to lowercase
# Discord bot event: on message received
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!player'):
        name_to_check = message.content.replace('!player', '').strip()
        if name_to_check:
            is_online = is_name_online(name_to_check)
            if is_online:
                await message.channel.send("Player is online!")
            else:
                await message.channel.send(" Player is not online.")
        else:
            await message.channel.send("Please provide a player name to check.")

    elif message.content.startswith('!status'):
        server_status = get_server_status()
        if server_status:
            await message.channel.send(server_status)
        else:
            await message.channel.send("Failed to fetch server status.")

    elif message.content.startswith('!top'):
        top_players = get_top_players()
        if top_players:
            response = "Top Players:\n```Rank\t\tName\t\tLevel\n"
            response += "\n".join(top_players)
            response += "```"
            await message.channel.send(response)
        else:
            await message.channel.send("Failed to fetch top players data.")
                #ITEM SEARCH
    
    elif message.content.lower().startswith('!price'):
        item_name = message.content.lower().replace('!price', '').strip()
        if not item_name:
            await message.channel.send("Please provide an item name after the command, like `!price Eon`.")
        else:
            item_data = scrape_item_data(ITEM_LIST_URL)
            if item_data:
                sell_price = item_data.get(item_name)
                if sell_price:
                    await message.channel.send(f"The sell price of {item_name.capitalize()} is {sell_price} EON.")
                else:
                    await message.channel.send(f"Item not found in the item list.")
            else:
                await message.channel.send("Failed to fetch item data.")

    elif message.content.lower().startswith('!guilds'):
        guild_data = scrape_guild_data(GUILDS_URL)
        if guild_data:
            response = "Top Guilds:\n```Rank\tGuild Name\n"
            response += "\n".join(guild_data)
            response += "```"
            await message.channel.send(response)
        else:
            await message.channel.send("Failed to fetch guild data.")
  
          #GENERAL LINK COMMANDS
    elif message.content.startswith('!noob guide'):
        embed = discord.Embed(title="Video Guide", description="Check out this YouTube video guide by Kami: https://www.youtube.com/watch?v=QHGFkog0eAU&ab_channel=KamiYamaoni", url="https://www.youtube.com/watch?v=QHGFkog0eAU&ab_channel=KamiYamaoni")
        await message.channel.send(embed=embed)

    elif message.content.startswith('!items'):
        await message.channel.send("Here is the item list: https://docs.google.com/spreadsheets/d/1Itfl1YBw2R_mussBFg0F0XqOaOPtWpxQTpG10GG2fS4/edit#gid=1737236281")
      
    elif message.content.startswith('!kodyisgay'):
        await message.channel.send("Exploit took two loads in the eye. He thanked chad after the experience. He never saw the world the same.")
    
    elif message.content.startswith('!guide'):
        await message.channel.send("Best guide on the interwebz for the newbs https://www.youtube.com/watch?v=QHGFkog0eAU&ab")
      
    elif message.content.startswith('!epicguide'):
        await message.channel.send("Here is the Epic Guide: https://docs.google.com/document/d/1iNCCYTVInLJvgEY-uYcYHOt1FX4ogVjZs999NfJWRAE/edit")

    elif message.content.startswith('!download'):
        await message.channel.send("You can download the game here: https://www.endless-online.com/downloads.html")

    elif message.content.startswith('!cheats'):
        await message.channel.send("Join the cheats Discord server here:  not for public")
      

bot.run(token)
