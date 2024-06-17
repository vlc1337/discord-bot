import disnake
from disnake.ext import commands
import sqlite3
from random import randint
import random
import math
import asyncio
import os

bot = commands.InteractionBot(intents=disnake.Intents.all())
con = sqlite3.connect("discord.db")
cursor = con.cursor()
items = ['Lucky coin', 'Copper ingot', 'Tester coin', 'Golden coin', 'Pickaxe']
shopitems  = ['1|Lucky coin|500', '2|Golden coin|1000', '3|Pickaxe|1000'] #ID|item|price
cooldowns = {}
marketlist = []

logs_channel_id = 848444705414840350
bot_id = 996707458082951248
token = 'token' #your bot token
transfering_balance_log = True #logging balance operations
transfering_items_log = True #logging inventory changing
lucky_coin_boost = True #lucky coin boosts reward per message
lucky_coin_boosti = 1 #coins boost per message
golden_coin_boost = True #golden coin boosts reward per message
golden_coin_boosti = 2 #coins boost per message
message_rewards = True #add balance for messages
min_reward = 1
max_reward = 5
min_message_length = 5 #minimal message length for a reward
chat_bot = True #turn on chat bot
maxitems_limit = True #set a limit on inventory
maxitems = 5 #max items in inventory
claim_coins = 150 #how much coins to claim
claim_interval = 3600 #in seconds
tester_coin_boost = 2 #multiply claimed coins

@bot.event
async def on_ready():
    global marketlist
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                cursor.execute(f"SELECT id FROM users where id={member.id}")
                if cursor.fetchone()==None:
                    cursor.execute(f"INSERT INTO users VALUES ({member.id}, 0, 0, 'empty')")
                else:
                    pass
        con.commit()
    channel = bot.get_channel(logs_channel_id)
    await channel.send(f"bot is working")
    with open('market.txt', 'r') as m:
        marketlist = m.readlines()

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
    global ninv, profil
    await inter.response.defer()
    if not user:
        user = inter.author
    for info in cursor.execute(f"SELECT id, balance, messages, inventory FROM users where id={user.id}"):
        ninv = "\nempty" if 'empty' in info[3] else '\n'
        coun = 0
        if 'empty' not in info[3]:
            for i in info[3].split('\n'):
                ninv += f'`{i}`\n'
            coun = len(info[3].split('\n'))
        if maxitems_limit:
            ninv = f'`{user.name}` inventory ({coun}/{maxitems} items):\n' + ninv
        else:
            ninv = f'`{user.name}` inventory:\n' + ninv
        profil = f'viewing `{user.name}`\nID: `{info[0]}`\nbalance: `{info[1]}`\nmessages: `{info[2]}`'
        await inter.send(profil, components=[
        disnake.ui.Button(label="open inventory", style=disnake.ButtonStyle.primary, custom_id="inventory")
    ])
    if user.bot:
        await inter.send("Bots don't have profile")

@bot.event
async def on_button_click(inter):
    await inter.response.defer()
    if inter.component.custom_id == "inventory":
            await inter.message.edit(content=ninv, components=[
        disnake.ui.Button(label="open profile", style=disnake.ButtonStyle.primary, custom_id="profile")
    ])
    if inter.component.custom_id == 'profile':
            await inter.message.edit(content=profil, components=[
                disnake.ui.Button(label="open inventory", style=disnake.ButtonStyle.primary, custom_id="inventory")
            ])
    if inter.component.custom_id == 'market':
        await inter.message.edit(content=marketl, components=[
                disnake.ui.Button(label="open shop", style=disnake.ButtonStyle.primary, custom_id="shop")
            ])
    if inter.component.custom_id == 'shop':
        await inter.message.edit(content=shoplist, components=[
                disnake.ui.Button(label="open market", style=disnake.ButtonStyle.primary, custom_id="market")
            ])


@bot.event
async def on_message(message):
    for messages in cursor.execute(f"SELECT messages FROM users where id={message.author.id}"):
        newm = messages[0] + 1
        cursor.execute(f'UPDATE users SET messages={newm} where id={message.author.id}')
        con.commit()
    if len(message.content) > min_message_length:
        for money in cursor.execute(f"SELECT balance FROM users where id={message.author.id}"):
            newb = money[0] + randint(min_reward, max_reward)
            inv = invlist(message.author.id)
            if 'Lucky coin' in inv and lucky_coin_boost:
                newb+=lucky_coin_boosti*inv.count('Lucky coin')
            if 'Golden coin' in inv and golden_coin_boost:
                newb+=golden_coin_boosti*inv.count('Golden coin')
            cursor.execute(f'UPDATE users SET balance={newb} where id={message.author.id}')
            con.commit()
    if (f'<@{bot_id}>') in message.content and chat_bot:
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

    leaderboard = f'Balance leaderboard (Page {page}/{max_pages}):\n\n'
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

    leaderboard = f'Messages leaderboard (Page {page}/{max_pages}):\n\n'
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
        await channel.send(f"`{inter.author.name}` added {amount} coins to `{user.name}`'s(now {res} coins) balance")
    await inter.send(f"<@{inter.author.id}> added {amount} coins to <@{user.id}>'s balance")

@bot.slash_command(description='send money to user')
async def sendbalance(inter, user:disnake.User, amount: int):
    await inter.response.defer()
    for row in cursor.execute(f"SELECT balance FROM users where id={inter.author.id}"):
        if row[0] < amount:
            await inter.send(f"you can't send {amount} coins because you have only {row[0]} coins")
            if transfering_balance_log:
                channel = bot.get_channel(logs_channel_id)
                await channel.send(f'`{inter.author.name}` tried to send {amount} coins to `{user.name}` but he had only {row[0]} coins')
        elif amount <= 0:
            await inter.send(f"you can't send {amount} coins :p")
            if transfering_balance_log:
                channel = bot.get_channel(logs_channel_id)
                await channel.send(f'`{inter.author.name}` tried to send {amount} coins to `{user.name}`')
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
                await channel.send(f"`{inter.author.name}`(now {newb} coins) sent `{user.name}`(now {addb} coins) {amount} coins")
            await inter.send(f"<@{inter.author.id}> sent <@{user.id}> {amount} coins")
    if user.bot:
        await inter.send("You can't send money to bot")


@bot.slash_command(description='add an item to user(admin command)')
@commands.has_role("[ROOT]")
async def additem(inter, user: disnake.User, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    resinvv = invlist(user.id)
    if maxitems_limit and maxitems <= len(resinvv) and resinvv != 'empty':
        await inter.send(f"you can't add {item} because <@{user.id}> already has {len(resinvv)}/{maxitems} items")
    elif user.bot:
        await inter.send(f"you can't send it to a bot")
    else:
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
            await channel.send(f"`{inter.author.name}` gave `{user.name}` an item: {item}\ncurrent `{user.name}` inventory:\n{str(resinv)}")

@bot.slash_command(description='remove an item(admin command)')
@commands.has_role("[ROOT]")
async def removeitem(inter, user: disnake.User, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    resinvv = invlist(user.id)
    if item in resinvv:
        resinvv.remove(item)
        resinv = '\n'.join(resinvv)
        if resinv == '':
            resinv = 'empty'
        cursor.execute(f"UPDATE users SET inventory='{str(resinv)}' where id={user.id}")
        con.commit()
        await inter.send(f"<@{inter.author.id}> removed {item} from <@{user.id}>'s inventory") 
        if transfering_items_log:
            channel = bot.get_channel(logs_channel_id)
            await channel.send(f"`{inter.author.name}` removed {item} from `{user.name}`'s inventory\ncurrent `{user.name}` inventory:\n{str(resinv)}")
    else:
        await inter.send(f"<@{user.id}> doesn't have {item}")

@bot.slash_command(description='send an item to another user')
async def senditem(inter, user: disnake.User, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    resinvv = invlist(user.id)
    resinv = '\n'.join(resinvv)
    senderinv = invlist(inter.author.id)
    if maxitems_limit and maxitems == len(resinvv) and resinvv != 'empty':
        await inter.send(f"you can't send {item} because <@{user.id}> already has {len(resinvv)}/{maxitems} items")
    elif (len(resinvv) < maxitems and maxitems_limit) or (maxitems_limit == False):
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
                await channel.send(f"`{inter.author.name}` gave `{user.name}` an item: {item}\n`{inter.author.name}`:\n{sendinv}\n`{user.name}`:\n{resinv}")
    elif item not in senderinv:
        await inter.send(f"you don't have {item} so you can't send it")
    elif user.id == inter.author.id:
        await inter.send(f"you can't send it to yourself")

@bot.slash_command(description='burn an item(get rid of it)')
async def burnitem(inter, item: str = commands.Param(choices=items)):
    await inter.response.defer()
    inv = invlist(inter.author.id)
    def check(m):
        return m.author == inter.author and m.channel == inter.channel and (m.content == 'yes' or m.content == '`yes`')
    if item in inv:
        try:
            await inter.send(f"are you sure you want to burn(throw away) {item}? send `yes` to confirm(or wait 15 seconds to cancel)")
            msg = await bot.wait_for("message", check=check, timeout=15.0)
            inv.remove(item)
            if inv == []:
                inv.append('empty')
            res = '\n'.join(inv) if len(inv) > 1 else inv[0]
            cursor.execute(f"UPDATE users SET inventory='{str(res)}' where id={inter.author.id}")
            con.commit()
            await inter.send(f"successfully burnt {item}")
            if transfering_items_log:
                channel = bot.get_channel(logs_channel_id)
                await channel.send(f"`{inter.author.name}` burnt {item}")
        except asyncio.TimeoutError:
            await inter.send("timeout, try again")
    else:
        await inter.send(f"you don't have {item}")

def checkid(id,marketlist):
    if marketlist != [] and marketlist != ['\n']:
        for i in marketlist:
            try:
                i = i.split('|')
                if int(i[0]) == id:
                    id = randint(1000000, 9999999)
                    return checkid(id,marketlist)
            except: pass
        
    return

@bot.slash_command(description='sell an item using marketplace')
async def sell(inter, price: int, item: str = commands.Param(choices=items)):
    global marketlist
    await inter.response.defer()
    inv = invlist(inter.author.id)
    if price < 0:
        await inter.send(f"price should be >= 0")
        return
    if item in inv:
        inv.remove(item)
        inv.append(f'{item}(on sale)')
        res = '\n'.join(inv) if len(inv) > 1 else inv[0]
        id = randint(1000000, 9999999)
        with open('market.txt', 'r+') as m:
            if m != []:
                marke = m.readlines()
                checkid(id, marke)
            m.write(f"{id}|{inter.author.id}|{item}|{price}\n")
        marketlist.append(f"{id}|{inter.author.id}|{item}|{price}")
        cursor.execute(f"UPDATE users SET inventory='{str(res)}' where id={inter.author.id}")
        con.commit()
        await inter.send(f"you are selling {item} for {price} coins; ID - {id}")
        if transfering_items_log:
            channel = bot.get_channel(logs_channel_id)
            await channel.send(f"`{inter.author.name}` is selling {item} for {price} coins; ID - {id}")
    else:
        await inter.send(f"you don't have {item}")

@bot.slash_command(description='shows market list')
async def market(inter):
    global marketl, shoplist
    await inter.response.defer()
    marketl = 'market items:\n\n'
    if marketlist != [] and marketlist != ['\n']:
        for i in marketlist:
            try:
                i = i.split('|')
                seller = await bot.fetch_user(int(i[1]))
                marketl+=f'ID: `{i[0]}` seller: `{seller.name}` item: `{i[2]}` price: `{int(i[3])}`\n'
            except: pass
        marketl+= 'use `/buy` to buy an item'
    shoplist = 'shop items:\n\n'
    for i in shopitems:
        i = i.split('|')
        shoplist+=f'ID: `{i[0]}` item: `{i[1]}` price: `{int(i[2])}`\n'
    shoplist += 'use `/buy` to buy an item'
    await inter.send(shoplist, components=[
        disnake.ui.Button(label="open market", style=disnake.ButtonStyle.primary, custom_id="market")
    ])

@bot.slash_command(description='buy an item using marketplace')
async def buy(ctx):
    await ctx.response.defer()
    await ctx.send("enter an ID of item to buy(use `/market` to check)")
    def check1(m):
        ids = []
        for i in marketlist:
            i = i.split('|')
            ids.append(i[0])
        for i in shopitems:
            i = i.split('|')
            ids.append(i[0])
        return m.author == ctx.author and m.channel == ctx.channel and m.content in ids
    def check2(m):
        return m.author == ctx.author and m.channel == ctx.channel and (m.content == 'yes' or m.content == '`yes`')
    try:
        msg = await bot.wait_for("message", check=check1, timeout=30.0)
        id = msg.content
        item = []
        for i in marketlist:
            i = i.split('|')
            if i[0] == id:
                item = i
        for i in shopitems:
            i = i.split('|')
            if i[0] == id:
                item = i
        if len(item) == 3:
            await ctx.send(f"are you sure you want to buy {item[1]} for {int(item[2])} coins? send `yes` to confirm(or wait 15 seconds to cancel)")
            try:
                conf = await bot.wait_for("message", check=check2, timeout=15.0)
                inv = invlist(ctx.author.id)
                for row in cursor.execute(f"SELECT balance FROM users where id={ctx.author.id}"):
                    if int(item[2]) > row[0]:
                        await ctx.send(f"insufficient balance")
                        return
                    if len(inv) == maxitems and inv != 'empty' and maxitems_limit:
                        await ctx.send(f"you have {maxitems}/{maxitems} items now so you can't do it")
                        return
                    else:
                        newb = row[0] - int(item[2])
                        cursor.execute(f"UPDATE users SET balance={newb} where id={ctx.author.id}")
                        con.commit()
                        if inv != 'empty':
                            inv.append(item[1])
                            inv = '\n'.join(inv)
                        else:
                            inv = item[1]
                        cursor.execute(f"UPDATE users SET inventory='{str(inv)}' where id={ctx.author.id}")
                        con.commit()
                        await ctx.send(f"successfully bought {item[1]} for {item[2]} coins")
                        if transfering_balance_log or transfering_items_log:
                            channel = bot.get_channel(logs_channel_id)
                            await channel.send(f"`{ctx.author.name}` bought {item} from store, {newb} coins now")
            except asyncio.TimeoutError:
                await ctx.send("timeout, try again")
        if len(item) == 4:
            if ctx.author.id == int(item[1]):
                inv = invlist(ctx.author.id)
                inv.remove(f'{item[2]}(on sale)')
                if inv != 'empty':
                    inv.append(item[2])
                    inv = '\n'.join(inv)
                else:
                    inv = item[2]
                cursor.execute(f"UPDATE users SET inventory='{str(inv)}' where id={ctx.author.id}")
                con.commit()
                await ctx.send(f'you got your {item[2]} back')
                this = '|'.join(item)
                marketlist.remove(this)
                with open('market.txt', "w") as f:
                    f.write("")
                with open('market.txt', 'r+') as m:
                    if marketlist != []:
                        for i in marketlist:
                            m.write(f"{i}")
                if transfering_items_log:
                    channel = bot.get_channel(logs_channel_id)
                    await channel.send(f"`{ctx.author.name}` removed {item[2]} from sale; ID - {item[0]}")
                return
            await ctx.send(f"are you sure you want to buy {item[2]} for {int(item[3])} coins? send `yes` to confirm(or wait 15 seconds to cancel)")
            try:
                conf = await bot.wait_for("message", check=check2, timeout=15.0)
                inv = invlist(ctx.author.id)
                if len(inv) == maxitems and inv != 'empty' and maxitems_limit:
                    await ctx.send(f"you have {maxitems}/{maxitems} items now so you can't do it")
                    return
                for row in cursor.execute(f"SELECT balance FROM users where id={ctx.author.id}"):
                    if int(item[3]) > row[0]:
                        await ctx.send(f"insufficient balance")
                        return
                    else:
                        newb = row[0] - int(item[3])
                        cursor.execute(f"UPDATE users SET balance={newb} where id={ctx.author.id}")
                        con.commit()
                        if inv != 'empty':
                            inv.append(item[2])
                            inv = '\n'.join(inv)
                        else:
                            inv = item[2]
                        cursor.execute(f"UPDATE users SET inventory='{str(inv)}' where id={ctx.author.id}")
                        con.commit()
                        await ctx.send(f"successfully bought {item[2]} for {int(item[3])} coins")
                        seller = await bot.fetch_user(int(item[1]))
                        for row in cursor.execute(f"SELECT balance FROM users where id={seller.id}"):
                            newsell = row[0] + int(item[3])
                        sellinv = invlist(seller.id)
                        sellinv.remove(f'{item[2]}(on sale)')
                        sellinv = '\n'.join(sellinv)
                        if sellinv == '\n' or sellinv == '':
                            sellinv = 'empty'
                        cursor.execute(f"UPDATE users SET inventory='{str(sellinv)}' where id={seller.id}")
                        cursor.execute(f"UPDATE users SET balance={newsell} where id={seller.id}")
                        con.commit()
                        try:
                            await seller.send(f"`{ctx.author.name}` bought your {item[2]} for {item[3]} coins", timeout=1.0)
                        except: pass
                        if transfering_balance_log or transfering_items_log:
                            channel = bot.get_channel(logs_channel_id)
                            await channel.send(f"`{ctx.author.name}` bought {item} from market from {seller.name}, {newb} coins now")
                        this = '|'.join(item)
                        marketlist.remove(this)
                        with open('market.txt', "w") as f:
                            f.write("")
                        with open('market.txt', 'r+') as m:
                            if marketlist != []:
                                for i in marketlist:
                                    m.write(f"{i}")
            except asyncio.TimeoutError:
                await ctx.send("timeout, try again")
    except asyncio.TimeoutError:
        await ctx.send("timeout, try again")

@bot.slash_command(description='claim free coins')
async def claim(ctx):
    user_id = ctx.author.id
    if user_id in cooldowns and cooldowns[user_id] > asyncio.get_event_loop().time():
        time_left = cooldowns[user_id] - asyncio.get_event_loop().time()
        await ctx.send(f"please wait {int(time_left//60)} more minutes to claim coins")
        return
    add = claim_coins
    for r in cursor.execute(f"SELECT balance FROM users where id={ctx.author.id}"):
        inv = invlist(ctx.author.id)
        if 'Tester coin' in inv:
            add *= tester_coin_boost
        if 'Pickaxe' not in inv:
            await ctx.send(f"buy pickaxe to claim coins")
            return
    cooldowns[user_id] = asyncio.get_event_loop().time() + claim_interval
    bal = add + r[0]
    cursor.execute(f"UPDATE users SET balance={bal} where id={ctx.author.id}")
    con.commit()
    await ctx.send(f"successfully claimed {add} coins")
    if transfering_balance_log:
        channel = bot.get_channel(logs_channel_id)
        await channel.send(f'`{ctx.author.name}` claimed {add} coins, {bal} coins now')

@bot.slash_command(description='save db')
@commands.has_role("[ROOT]")
async def dump(ctx):
    file_path = "discord.db"
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            channel = bot.get_channel(logs_channel_id)
            await channel.send(file=disnake.File(f, "discord.db"))
            await ctx.send("success")
    else:
        await ctx.send("file does not exist")

bot.run(token)
