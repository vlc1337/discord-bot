# **Installation**

**Download these things first:**

- [Python](https://www.python.org/downloads/)(also while installing add python to path by clicking the check mark)
  
- [PIP](https://bootstrap.pypa.io/get-pip.py)(download it as a python file and run it)
  

Open cmd and enter ```cd <path to the bot folder>``` Example: ```cd C:\Users\admin\Downloads\bot```

Enter this command in cmd: ```pip install -r requirements.txt```

It will install all libraries you need.

If you want to change the bot's database(discord.db) by yourself - download [DB browser for SQLite](https://sqlitebrowser.org/dl/) and open database using this app.

Go to [discord developer portal](https://discord.com/developers/applications) and create an application. Go to bot and set up an avatar and username; turn on all privileged gateway intents. Save your bot's token.

To add your bot to your server - go to OAuth2, pick bot in OAuth2 URL Generator and go to the generated link.


# **Setup**

Open main.py via text redactor or python IDLE. Change logs_channel_id, bot_id and token(you can copy IDs by turning on dev mode in discord). 

items - contains all in-game items(used for /additem, /removeitem, /senditem)

shopitems - contains items which are availible in the shop, format ID|item|price

coin_boosts - how much coins to add per message if user has this coin, format coin: amount

cooldowns and marketlist - just don't change them

helptext - string - text displayed using /help command(change it as you want)

admin_role - string - a name of admin role for admin commands

transfering_balance_log - bool - bot will send a message to logs channel when someone buys something/transfers balance/claim coins

transfering_items_log - bool - bot will send a message to logs channel when someone buys something/transfers item/burns item

coins_boost - bool - to activate coins boost(additional coins per message)

message_rewards - bool - to add balance to users for messages

min_reward and max_reward - integer - how much to add

min_message_length - integer - minimal message length to pay a reward

chat_bot - bool - turning on chat bot(sometimes sends random previous messages, you can add your words by changing words.txt)

maxitems_limit - bool - set a limit on inventory items

maxslots - integer - primary limit of slots per user

slot_cost - integer - additional inventory slot price

slot_cost_increase - integer - increase price per each level

claim_coins - integer - how much to award for claim

claim_interval - integer - claiming interval(in seconds)

How to change max slots limit if I already have a filled database? Use this SQL command:

UPDATE users
SET space = 5;

where 5 - your number

Also change help command if you change items or something

# **Admin commands**

/addbalance <user> <amount> - adding balance to users(to reduce the balance just use the number below zero)

/additem <user> and /removeitem <user> - adding and removing items from users

/dump - saving discord.db into logs channel

# **User commands**

/account <user> - checking an account and inventory

/market - opens shop and market

/buyslot - buy an additional slot in inventory(if enabled); send 'yes' as a confirmation in chat

/sell <price> <item> - selling items

to get your item back just buy it from market, you will be charged 0 coins

/buy <id> - buying items

/burnitem - throwing away items; send 'yes' as a confirmation in chat 

/sendbalance <user> <amount> - transfering balance

/senditem <user> - transfering items

/claim - claim coins(you have to buy a pickaxe first)

/lbmoney <page> and /lbmessages <page> - checking leaderboard

/help - help command

# **Donate**

TON wallet
```UQByi9LkO8E9-_tTtXoERu638unhbVzHXet5BBcKNuFRlHs9```

# **Change log**

v0.1

- made a chat bot sending random previous messages(or you can fill messages database by changing words.txt)
  
- added sql users database
  
- added profile including id, balance, messages, inventory
  
- added leaderboard for balance and messages
  
- adeed an admin command to change balance(use -int to decrease balance)
  
v0.1.1

- fixed problem with chat bot
  
- fixed messages leaderboard
  
v0.2

- added first item: lucky coin(gives balance farm boost)
  
- added config
  
- added balance transfers
  
- added inventory transfers
  
- fixed some bugs
  
v0.2.1

- upgraded leaderboard
  
- minor bug fixes
  
v0.3

- improved profile
  
- added inventory limit
  
- added shop
  
- added an ability to burn items

- added more test items
  
v0.4

- added marketplace(buy&sell items)
  
- added burning confirmation
  
- added coins mining

v0.5

- added inventory slots in shop

- changed config

v0.5.1

- added items stack in inventory

- changed items buying progress
