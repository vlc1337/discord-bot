import disnake
from disnake.ext import commands
import sqlite3
from random import randint
import random
import math

bot = commands.InteractionBot(intents=disnake.Intents.all())
con = sqlite3.connect("discord.db")
cursor = con.cursor()
items = ['Lucky coin'] #add items here

token = 'token' #your bot token
logs_channel_id = 123
bot_id = 1337
transfering_balance_log = True #logging balance operations
transfering_items_log = True #logging inventory changing
lucky_coin_boost = True #lucky coin boosts reward per message
message_rewards = True #add balance for messages
min_reward = 1
max_reward = 5
minimal_message_length = 0 #minimal message length to add balance for messagew
coin_boost = 1 #coins per message
chat_bot = True #turn on chat bot

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
async def account(inter, user: disnake.User = None):
    if not user:
        user = inter.author
    for info in cursor.execute(f"SELECT id, balance, messages, inventory FROM users where id={user.id}"):
        ninv = " " if info[3].count('\n') == 0 else '\n'
        for i in info[3].split(';'):
            ninv += f'```{i}```\n'
        await inter.send(f'Viewing `{user.name}`\nID: `{info[0]}`\nbalance: `{info[1]}`\nmessages: `{info[2]}`\ninventory:{ninv}')

@bot.event
async def on_message(message):
    for messages in cursor.execute(f"SELECT messages FROM users where id={message.author.id}"):
        newm = messages[0] + 1
        cursor.execute(f'UPDATE users SET messages={newm} where id={message.author.id}')
        con.commit()
    if len(message.content) > minimal_message_length:
        for money in cursor.execute(f"SELECT balance FROM users where id={message.author.id}"):
            newb = money[0] + randint(min_reward, max_reward)
            inv = invlist(message.author.id)
            if 'Lucky coin' in inv and lucky_coin_boost:
                newb+=coin_boost*inv.count('Lucky coin')
            cursor.execute(f'UPDATE users SET balance={newb} where id={message.author.id}')
            con.commit()
    if (f'<@{bot_id}>') in message.content and chat_bot: # your bot ID
        msg = await word()
        if msg:
            await message.channel.send(content=msg)
    if message.author.bot:
        return
    if '@' in message.content or 'http' in message.content:
        return
    if chat_bot:
        await add_word(message.content)
    if randint(0, 100) <= 10 and chat_bot:
        msg = await word()
        if msg:
            await message.channel.send(content=msg)

@bot.slash_command(description='shows money leaberboard')
async def lbmoney(inter, page: int=1):
    await inter.response.defer()
    cursor.execute('SELECT id, balance FROM users ORDER BY balance DESC')
    rows = cursor.fetchall()

    max_pages = math.ceil(len(rows)/10)
    if page > max_pages or page < 1:
        await inter.send(f"Invalid page number. Valid pages are 1-{max_pages}")
        return

    start_index = (page - 1) * 10
    end_index = start_index + 10

    leaderboard = 'Balance leaderboard (Page {}/{}):\n\n'.format(page, max_pages)
    for i, row in enumerate(rows[start_index:end_index]):
        user = await bot.fetch_user(row[0])
        leaderboard += f'{i+1+page*10-10}) `{user.name}` - {row[1]}\n'
    await inter.send(leaderboard)

@bot.slash_command(description='shows messages leaderboard')
async def lbmessages(inter, page: int=1):
    await inter.response.defer()
    cursor.execute('SELECT id, messages FROM users ORDER BY messages DESC')
    rows = cursor.fetchall()

    max_pages = math.ceil(len(rows)/10)
    if page > max_pages or page < 1:
        await inter.send(f"Invalid page number. Valid pages are 1-{max_pages}")
        return

    start_index = (page - 1) * 10
    end_index = start_index + 10

    leaderboard = 'Messages leaderboard (Page {}/{}):\n\n'.format(page, max_pages)
    for i, row in enumerate(rows[start_index:end_index]):
        user = await bot.fetch_user(row[0])
        leaderboard += f'{i+1+page*10-10}) `{user.name}` - {row[1]}\n'
    await inter.send(leaderboard)

async def word():
    with open("words.txt", "r", encoding='utf-8') as tempwords:
        words = tempwords.readlines()
        res = random.choice(words)
        if not res:
            return
        return res

async def add_word(msg):
    with open("words.txt", "a", encoding='utf-8') as s:
        msgnormal = msg.replace('@', '')
        if not msgnormal:
            return
        s.write(f"{msgnormal}\n")

def invlist(id):
    for w in cursor.execute(f"SELECT inventory FROM users where id={id}"):
        if 'empty' in w[0]:
            inv = 'empty'  
        else:
            inv = w[0].split('\n')
        return inv


@bot.slash_command(description='add balance to user(admin command)')
@commands.has_role("[ROOT]")
async def addbalance(inter, user: disnake.User, amount: int):
    await inter.response.defer()
    for row in cursor.execute(f"SELECT balance FROM users where id={user.id}"):
        money = row[0]
    res = money + amount
    cursor.execute(f'UPDATE users SET balance={res} where id={user.id}')
    con.commit()
    if transfering_balance_log:
        channel = bot.get_channel(logs_channel_id)
        await channel.send(f"<@{inter.author.id}> added {amount} coins to <@{user.id}>'s(now {res} coins) balance")
    await inter.send(f"<@{inter.author.id}> added {amount} coins to <@{user.id}>'s balance")

@bot.slash_command(description='send money to user')
async def sendbalance(inter, user:disnake.User, amount: int):
    await inter.response.defer()
    for row in cursor.execute(f"SELECT balance FROM users where id={inter.author.id}"):
        if row[0] < amount:
            await inter.send(f"you can't send {amount} coins because you have only {row[0]} coins")
            if transfering_balance_log:
                channel = bot.get_channel(logs_channel_id)
                await channel.send(f'<@{inter.author.id}> tried to send {amount} coins to <@{user.id}> but he had only {row[0]} coins')
        elif amount <= 0:
            await inter.send(f"you can't send {amount} coins :p")
            if transfering_balance_log:
                channel = bot.get_channel(logs_channel_id)
                await channel.send(f'<@{inter.author.id}> tried to send {amount} coins to <@{user.id}>')
        elif inter.author.id == user.id:
            await inter.send(f"you can't send money to yourself")
        if row[0] >= amount and amount > 0 and inter.author.id != user.id:
            newb = row[0] - amount
            cursor.execute(f'UPDATE users SET balance={newb} where id={inter.author.id}')
            con.commit()
            for r in cursor.execute(f"SELECT balance FROM users where id={user.id}"):
                addb = r[0] + amount
                cursor.execute(f'UPDATE users SET balance={addb} where id={user.id}')
                con.commit()
            if transfering_balance_log:
                channel = bot.get_channel(logs_channel_id)
                await channel.send(f"<@{inter.author.id}>(now {newb} coins) sent <@{user.id}>(now {addb} coins) {amount} coins")
            await inter.send(f"<@{inter.author.id}> sent <@{user.id}> {amount} coins")


@bot.slash_command(description='add an item to user(admin command)')
@commands.has_role("[ROOT]")
async def additem(inter, user: disnake.User, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    resinvv = invlist(user.id)
    resinv = '\n'.join(resinvv)
    if resinvv != 'empty':
        resinv+=f'\n{item}'
    if resinvv == 'empty':
        resinv=f'{item}'
    cursor.execute(f"UPDATE users SET inventory='{str(resinv)}' where id={user.id}")
    con.commit()
    await inter.send(f"<@{inter.author.id}> gave <@{user.id}> an item: {item}") 
    if transfering_items_log:
        channel = bot.get_channel(logs_channel_id)
        await channel.send(f"<@{inter.author.id}> gave <@{user.id}> an item: {item}\ncurrent <@{user.id}> inventory:\n{str(resinv)}")

@bot.slash_command(description='remove an item(admin command)')
@commands.has_role("[ROOT]")
async def removeitem(inter, user: disnake.User, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    resinvv = invlist(user.id)
    if item in resinvv:
        resinvv.remove(item)
        resinv = '\n'.join(resinvv)
        cursor.execute(f"UPDATE users SET inventory='{str(resinv)}' where id={user.id}")
        con.commit()
        await inter.send(f"<@{inter.author.id}> removed {item} from <@{user.id}>'s inventory") 
        if transfering_items_log:
            channel = bot.get_channel(logs_channel_id)
            await channel.send(f"<@{inter.author.id}> removed {item} from <@{user.id}>'s inventory\ncurrent <@{user.id}> inventory:\n{str(resinv)}")
    else:
        await inter.send(f"<@{user.id}> doesn't have {item}")

@bot.slash_command(description='send an item to another user')
async def senditem(inter, user: disnake.User, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    resinvv = invlist(user.id)
    resinv = '\n'.join(resinvv)
    senderinv = invlist(inter.author.id)
    if item in senderinv and user.id != inter.author.id:
        if resinv != 'empty':
            resinv+=f'\n{item}'
        if resinv == 'empty':
            resinv=f'{item}'
        cursor.execute(f"UPDATE users SET inventory='{str(resinv)}' where id={user.id}")
        con.commit()
        senderinv.remove(item)
        if senderinv == []:
            senderinv.append('empty')
        sendinv = '\n'.join(senderinv) if len(senderinv) > 1 else senderinv[0]
        cursor.execute(f"UPDATE users SET inventory='{str(sendinv)}' where id={inter.author.id}")
        con.commit()
        await inter.send(f"<@{inter.author.id}> sent <@{user.id}> an item: {item}") 
        if transfering_items_log:
            channel = bot.get_channel(logs_channel_id)
            await channel.send(f"<@{inter.author.id}> gave <@{user.id}> an item: {item}\n<@{inter.author.id}>:\n{sendinv}\n<@{user.id}>:\n{resinv}")
    elif item not in senderinv:
        await inter.send(f"you don't have {item} so you can't send it")
    elif user.id == inter.author.id:
        await inter.send(f"you can't send it to yourself")

bot.run(token)
