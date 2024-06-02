import disnake
from disnake.ext import commands
import sqlite3
from random import randint
import random

bot = commands.InteractionBot(intents=disnake.Intents.all())
con = sqlite3.connect("discord.db")
cursor = con.cursor()

@bot.event
async def on_ready():
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                cursor.execute(f"SELECT id FROM users where id={member.id}")
                if cursor.fetchone()==None:
                    cursor.execute(f"INSERT INTO users VALUES ({member.id}, 0, 0, 'empty')")
                else:
                    pass
        con.commit()

@bot.event
async def on_member_join(member):
    if not member.bot:
        cursor.execute(f"SELECT id FROM users where id={member.id}")
        if cursor.fetchone()==None:
            cursor.execute(f"INSERT INTO users VALUES ({member.id}, 0, 0, 'empty')")
        else:
            pass
    con.commit()

@bot.slash_command(description='shows account info')
async def account(ctx, user: disnake.User):
    for info in cursor.execute(f"SELECT id, balance, messages, inventory FROM users where id={user.id}"):
        await ctx.send(f'ID: `{info[0]}`\nbalance: `{info[1]}`\nmessages: `{info[2]}`\ninventory: `{info[3]}`')

@bot.event
async def on_message(message):
    for messages in cursor.execute(f"SELECT messages FROM users where id={message.author.id}"):
        newm = messages[0] + 1
        cursor.execute(f'UPDATE users SET messages={newm} where id={message.author.id}')
    if len(message.content) > 10:
        for money in cursor.execute(f"SELECT balance FROM users where id={message.author.id}"):
            newb = money[0] + randint(1,5)
            cursor.execute(f'UPDATE users SET balance={newb} where id={message.author.id}')
    if ('<@1245744833612746762>') in message.content: # your bot ID
        msg = await word()
        if msg:
            await message.channel.send(content=msg)
    if message.author.bot:
        return
    if '@' in message.content or 'http' in message.content:
        return
    await add_word(message.content)
    if randint(0, 100) <= 10:
        msg = await word()
        if msg:
            await message.channel.send(content=msg)
con.commit()

@bot.slash_command(description='shows money leaberboard')
async def lbmoney(inter):
    await inter.response.defer()
    cursor.execute('SELECT id, balance FROM users ORDER BY balance DESC LIMIT 10')
    rows = cursor.fetchall()
    leaderboard = 'Top 10 users balance:\n\n'
    for i, row in enumerate(rows):
        user = await bot.fetch_user(row[0])
        leaderboard += f'{i+1}) {user.name} - {row[1]}\n'
    await inter.send(leaderboard)

@bot.slash_command(description='shows messages leaderboard')
async def lbmessages(inter):
    await inter.response.defer()
    cursor.execute('SELECT id, messages FROM users ORDER BY balance DESC LIMIT 10')
    rows = cursor.fetchall()
    leaderboard = 'Top 10 users messages:\n\n'
    for i, row in enumerate(rows):
        user = await bot.fetch_user(row[0])
        leaderboard += f'{i+1}) {user.name} - {row[1]}\n'
    await inter.send(leaderboard)

async def word():
    words = open("words.txt", "r", encoding='utf-8').readlines()
    res = random.choice(words)
    if not res:
        return
    return res

async def add_word(msg):
    s = open("words.txt", "a+", encoding='utf-8')
    msgnormal = msg.replace('@', '')
    if not msgnormal:
        return
    s.write(f"{msgnormal}\n")

@bot.slash_command(description='add balance to user(admin command)')
@commands.has_role("[ROOT]")
async def addbalance(ctx, user: disnake.User, amount: int):
    for row in cursor.execute(f"SELECT balance FROM users where id={user.id}"):
        money = row[0]
    res = money + amount
    cursor.execute(f'UPDATE users SET balance={res} where id={user.id}')
    con.commit()
    await ctx.send(f"<@{ctx.author.id}> added {res} coins to <@{user.id}>'s balance")

bot.run('token')


