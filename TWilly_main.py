import discord
import requests
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.messages = True

# Initialize the Discord client with intents
client = discord.Client(intents=intents)

# Fetch player ID from player name
def get_player_id(player_name):
    search_url = f"https://statsapi.web.nhl.com/api/v1/players?fullName={player_name}"
    response = requests.get(search_url)
    data = response.json()
    
    # Print the full API response for debugging
    print("API Response:", data)

    players = data.get('people', [])
    if players:
        return players[0]['id'], players[0]['currentTeam']['abbreviation']
    
    return None, None

# Fetch player stats from the NHL API for a specific report type
def get_player_skater_stats(player_id, report_type):
    url = f"https://api.nhle.com/stats/rest/en/skater/{report_type}?playerId={player_id}"
    response = requests.get(url)
    return response.json()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Command to fetch player-specific stats
    if message.content.startswith("!playerstats"):
        args = message.content[len("!playerstats "):].strip().split(" ")
        if len(args) < 2:
            await message.channel.send("Please provide both a player name and a report type.")
            return
        
        player_name = " ".join(args[:-1])  # Join all but the last argument as the player name
        report_type = args[-1]  # Last argument is the report type
        
        print(f"Searching for player: '{player_name}'")
        player_id, team_abbr = get_player_id(player_name)

        if player_id:
            await message.channel.send(f"Player ID for {player_name}: {player_id}")
            await message.channel.send(f"Team Abbreviation: {team_abbr}")

            player_stats = get_player_skater_stats(player_id, report_type)
            if player_stats and 'data' in player_stats:
                stats_info = player_stats['data']
                response_message = f"**Stats for {player_name} under report type '{report_type}':**\n"
                for stat in stats_info:
                    response_message += f"- Player: {stat.get('playerName')}, Goals: {stat.get('goals', 0)}, Assists: {stat.get('assists', 0)}\n"  # Add more fields as needed
                await message.channel.send(response_message)
            else:
                await message.channel.send(f"No stats found for {player_name} under report type '{report_type}'.")
        else:
            await message.channel.send(f"Player {player_name} not found.")

client.run(DISCORD_TOKEN)
