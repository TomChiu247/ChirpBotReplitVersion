# bot.py
import os
import requests
import json
import discord
from dotenv import load_dotenv
from discord.ext import tasks, commands
from keep_online import keep_online
from PIL import Image
from io import BytesIO

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents(messages=True, members=True, guilds=True)
client = commands.Bot(command_prefix='$', help_command=None, intents=intents)

quotes_channel = 812474792103903283
tasks_channel = 812474792103903282
quotes_channel2 = 837419156805648404

def get_quote():
    response = requests.get\
    ("https://zenquotes.io/api/random")
    json_represenation = json.loads(response.text)
    quote = json_represenation[0]['q'] + " -" + json_represenation[0]['a']
    return quote

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def classprofile(ctx, role: discord.Role = None):
    if role is None:
        role = 'bme25'
    template = Image.open("bme25.png")
    row = 0
    column = 0
    x_coordinate = 392
    y_coordinate = 900

    # Going through server members to add the profile pictures of BME students into list
    for guild in client.guilds:
        for member in guild.members:
            if role in member.roles: #role.id:
                asset = member.avatar_url_as(format="png", size=256)
                data = BytesIO(await asset.read())
                profile_picture = Image.open(data)
                profile_picture = profile_picture.resize((400, 400))

                #pasting photos into template
                template.paste(profile_picture, (x_coordinate, y_coordinate))
                if column == 9:
                    row += 1
                    column = 0
                    y_coordinate += 792
                    x_coordinate = 392
                else:
                    column += 1
                    x_coordinate += 792

        template.save("BME25ClassProfile.png")
        await ctx.send(file=discord.File("BME25ClassProfile.png"))

@client.event
async def on_message(message):
  if message.guild.id != 812474791670972416:
    return
  else:
    if message.author == client.user and message.channel==client.get_channel(tasks_channel):
        await message.add_reaction('✅')
        return
    if message.content.startswith('T:'):
        await client.get_channel(tasks_channel).send('%s' % message.content)
    elif message.content.startswith('*inspire'):
        quote = get_quote()
        await client.get_channel(quotes_channel).send(quote)
  await client.process_commands(message)

@client.event
async def on_reaction_add(reaction, user):
  if reaction.message.guild.id != 812474791670972416:
    return
  else:
    if user == client.user:
        return
    channel = reaction.message.channel
    msg_id = reaction.message.id

    if reaction.emoji == '✅':
        msg = await channel.fetch_message(msg_id)
        await msg.edit(content="~~%s~~" % msg.content)

@client.event
async def on_reaction_remove(reaction, user):
  if reaction.message.guild.id != 812474791670972416:
    return
  else:
    if user == client.user:
        return
    channel = reaction.message.channel
    msg_id = reaction.message.id

    if reaction.emoji == '✅':
        msg = await channel.fetch_message(msg_id)
        await msg.edit(content="%s" % msg.content.replace('~~', '' ))

client.load_extension('cogs.DailyQuotesCog')
keep_online()
client.run(TOKEN)
