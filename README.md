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
admin_role - string - a name of admin role for admin commands
items - contains all in-game items
shopitems - contains items which are availible in the shop, format ID|item|price
cooldowns and marketlist - just don't change them
transfering_balance_log - True/False - bot will send a message to logs channel when someone buys something/transfers balance/claim coins
transfering_items_log - True/False - bot will send a message to logs channel when someone buys something/transfers item/burns item
lucky_coin_boost - True/False - lucky coin's boosting perk(adding additional coins per each message)
lucky_coin_boosti - integer - how much to add per each message
golden_coin_boost and golden_coin_boosti are the same
message_rewards - True/False - to add balance to users for messages
min_reward and max_reward - integer - how much to add
min_message_length - integer - minimal message length to pay a reward
chat_bot - True/False - turning on chat bot(sometimes sends random previous messages, you can add your words by changing words.txt)
maxitems_limit - True/False - set a limit on inventory items
maxitems - integer - max items per person
claim_coins - integer - how much to award for claim
claim_interval - integer - claiming interval(in seconds)
tester_coin_boost - integer - multiply claimed coins(tester coin's boost)

# **Admin commands**

/addbalance <user> <amount> - adding balance to users(to reduce the balance just use the number below zero)
/additem <user> and /removeitem <user> - adding and removing items from users
/dump - saving discord.db into logs channel

# **User commands**

/account <user> - checking an account and inventory
/market - opens shop and market
/sell <price> <item> - selling items
to get your item back just buy it from market, you will be charged 0 coins
/buy - buying items
send an ID of an item you want to buy in chat and then send a confirmation
/burnitem - throwing away items
send a confirmation in chat 
/sendbalance <user> <amount> - transfering balance
/senditem <user> - transfering items
/claim - claim coins(you have to buy a pickaxe first)
/lbmoney <page> and /lbmessages <page> - checking leaderboard

# **Donate**

TON wallet
```UQByi9LkO8E9-_tTtXoERu638unhbVzHXet5BBcKNuFRlHs9```
