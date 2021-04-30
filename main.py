# bot.py
import os
import requests
import json
import discord
from dotenv import load_dotenv
from discord.ext import commands
from keep_online import keep_online
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import numpy as np


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents(messages=True, members=True, guilds=True)
client = commands.Bot(command_prefix='$', help_command=None, intents=intents)

quotes_channel = 812474792103903283
tasks_channel = 812474792103903282

def mask_circle_transparent(data, size):
    profile_picture = Image.open(data).convert("RGB")
    profile_picture = profile_picture.resize(size)
    npImage = np.array(profile_picture)

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.pieslice([0, 0, size], 0, 360, fill=255)

    npAlpha=np.array(mask)
    npImage = np.dstack((npImage, npAlpha))
    Image.fromarray(npImage).save('pfp.png')
    return;

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
@commands.has_role('chicken')
async def classprofile(ctx, role: discord.Role = None):
    if role is None:
        role = 'bme25'
    template = Image.open("bme25.png")
    row = 0
    column = 0
    x_coordinate = 350
    y_coordinate = 1200
    size = (450, 450)

    # Going through server members to add the profile pictures of BME students into list
    for guild in client.guilds:
        for member in guild.members:
            if role in member.roles: #role.id:
                asset = member.avatar_url_as(format="png", size=256)
                data = BytesIO(await asset.read())
                mask_circle_transparent(data, size)
                edited_asset = Image.open("pfp.png")

                font = ImageFont.truetype("simplifica.ttf", 100)
                name = member.display_name
                name_pixel_length = len(name)

                #pasting photos into template
                drawn_template = ImageDraw.Draw(template)
                drawn_template.text((x_coordinate + (225-name_pixel_length*13), y_coordinate + 500), str(name), font=font)
                template.paste(edited_asset, (x_coordinate, y_coordinate), edited_asset)
                if column == 9:
                    row += 1
                    column = 0
                    y_coordinate += 800
                    x_coordinate = 350
                else:
                    column += 1
                    x_coordinate += 800

    template = template.resize((4350, 5630), Image.ANTIALIAS)
    template.save("BME25ClassProfile.png", optimize=True)
    channel = client.get_channel(709904167912865873)
    await ctx.send(file=discord.File("BME25ClassProfile.png"))

@client.event
async def on_message(message):
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
