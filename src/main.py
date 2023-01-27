import discord
from discord.ext import commands,tasks
from discord_slash import SlashCommand 
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import json
import reddit
import asyncio
import db
import os,sys,aiohttp
from datetime import datetime
import logging



f= open("/config/config.json","r")
settings = json.load(f)
f.close()

bot = commands.Bot(command_prefix=">")

slash = SlashCommand(bot,sync_commands=True)



logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('reddit_disc')
handler = logging.FileHandler(filename='reddit_disc.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def handler(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))

sys.excepthook = handler

@bot.event
async def on_ready():
    if not settings.get("refresh_token",None):
        await reddit.get_link()
    else:
        await db.date_check()
        check1.start()
        if int(settings['shadow_channel']) != 0:
            check2.start()
        if int(settings['reports_channel']) != 0:
            check3.start()
        if int(settings['modlog_channel']) != 0:
            check4.start()
        check5.start()
    print("bot has started")
    logger = logging.getLogger('reddit_disc')
    logger.setLevel(logging.INFO)
    logger.info("Started bot")
    logger.setLevel(logging.WARNING)
    

@tasks.loop()
async def check5():
    await reddit.last1k()


@tasks.loop(seconds=25*10)
async def check1():
    actRow = create_actionrow(
        create_button(
            style=ButtonStyle.blurple,
            label = "Approve",
            custom_id="approve",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Remove",
            custom_id="reject",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Shadowban",
            custom_id="shadowban",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "7 day ban",
            custom_id="7day",
        )
    )
    if int(settings['rising_channel']) == 0:
        pass
    else:
        rising = await reddit.latest_rising_posts()
        channel1 = bot.get_channel(int(settings['rising_channel']))
        for i in rising:
            embed = discord.Embed(
                title=f"Post by u/{i['username']} has reached rising",
                url=f"https://www.reddit.com/r/{settings['subreddit']}/comments/{i['id']}",
                color=0x00FF00
            ).add_field(
                name="Rising post",
                value=f"[Post link](https://www.reddit.com/r/{settings['subreddit']}/comments/{i['id']})"
            ).add_field(
                name="User",
                value=f"[u/{i['username']}](https://www.reddit.com/u/{i['username']})"
            ).add_field(
                name="Score",
                value=f"Post score = {i['score']}"
            ).add_field(
                name="Post Title",
                value=i['title']
            )
            if i['flair_url']:
                embed.set_thumbnail(url=i['flair_url'])
            if i['url'].endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
                embed.set_image(url=i['url'])
            elif i['is_self']:
                embed.add_field(name="selftext",value=i['selftext'])

            await channel1.send(embed=embed,components=[actRow])

            await asyncio.sleep(5)
    if int(settings['hot_channel']) == 0:
        pass 
    else:
        hot = await reddit.latest_hot_posts()
        channel2 = bot.get_channel(int(settings['hot_channel']))
        for i in hot:
            embed = discord.Embed(
                title=f"Post by u/{i['username']} has reached hot",
                url=f"https://www.reddit.com/r/{settings['subreddit']}/comments/{i['id']}",
                color=0x00FF00
            ).add_field(
                name="Hot post",
                value=f"[Post link](https://www.reddit.com/r/{settings['subreddit']}/comments/{i['id']})"
            ).add_field(
                name="User",
                value=f"[u/{i['username']}](https://www.reddit.com/u/{i['username']})"
            ).add_field(
                name="Score",
                value=f"Post score = {i['score']}"
            ).add_field(
                name="Post Title",
                value=i['title']
            )
            if i['flair_url']:
                embed.set_thumbnail(url=i['flair_url'])
            if i['url'].endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
                embed.set_image(url=i['url'])
            elif i['is_self']:
                embed.add_field(name="selftext",value=i['selftext'])

            await channel2.send(embed=embed,components=[actRow])
            await asyncio.sleep(5)

@bot.command()
async def lb(ctx,date = None):

    allowed = [602569683543130113,365906052677500928,250567840417972225,718631090574721064]

    if ctx.author.id not in allowed:
        return

    h = await db.get_all_hot_posted()
    r = await db.get_all_rising_posted()
    d=dict()
    if not date:
        for i in h+r:
            if len(i) == 5 and i[2]:
                if not d.get(i[2]):
                    d[i[2]] = 0
                d[i[2]] += 1
    else:
        try:
            date = date.replace("-","/")
            if len(date.split("/")[-1]) == 2:
                date = date.split("/")[0] + "/" + date.split("/")[1] + "/20" + date.split("/")[-1]
            t = datetime.timestamp(datetime.strptime(date,"%d/%m/%Y"))
        except Exception as e:
            return await ctx.send("Invalid date!")
        if not t:
            return await ctx.send("Invalid date!")

        for i in h+r:
            if len(i) == 5 and i[2] and i[4] and (float(i[4]) > t):
                if not d.get(i[2]):
                    d[i[2]] = 0
                d[i[2]] += 1
    d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1])}
    d2=""
    for i in reversed(list(d.keys())):
        d2 = d2 + f"<@{i}>" + ": " + str(d[i]) + "\n"
    embed = discord.Embed(
        title = "Top actions leaderboard",
        description = d2
    )
    await ctx.send(embed=embed)

@tasks.loop()
async def check2():
    channel = bot.get_channel(int(settings['shadow_channel']))
    actRow = create_actionrow(
        create_button(
            style=ButtonStyle.blurple,
            label = "Approve",
            custom_id="approve",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Remove",
            custom_id="reject",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Remove shadowban",
            custom_id="rshadowban",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "7 day ban",
            custom_id="7day",
        )
    )
    actRow2 = create_actionrow(
        create_button(
            style=ButtonStyle.blurple,
            label = "Approve",
            custom_id="capprove",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Remove",
            custom_id="creject",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Remove shadowban",
            custom_id="crshadowban",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "7 day ban",
            custom_id="c7day",
        )
    )
    async for post in reddit.unmoderated_stream():
        if post[1] == "p":
            await channel.send(embed=post[0],components=[actRow])
        elif post[1] == "c":
            await channel.send(embed=post[0],components=[actRow2])


@tasks.loop()
async def check3():
    channel = bot.get_channel(int(settings['reports_channel']))
    actRow2 = create_actionrow(
        create_button(
            style=ButtonStyle.blurple,
            label = "Approve",
            custom_id="capprove",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Remove",
            custom_id="creject",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Shadowban",
            custom_id="cshadowban",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "7 day ban",
            custom_id="c7day",
        )
    )
    async for post in reddit.report_stream():
        if post[1] == "c":
            await channel.send(embed=post[0],components=[actRow2])


@bot.command(aliases=['r'])
async def restart(ctx):
    
    u = bot.get_user(602569683543130113)
    if not u:
        u = await bot.fetch_user(602569683543130113)
    if u:
        await u.send(file=discord.File("reddit_disc.log"))
    await ctx.reply("Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)



@tasks.loop()
async def check4():
    channel = bot.get_channel(int(settings['modlog_channel']))
    async for post in reddit.modlog_stream():
        await channel.send(embed=post)


@bot.command(aliases=['log'])
async def logs(ctx):
    if ctx.author.id in [365906052677500928,602569683543130113,718631090574721064,694914425412649021,357918459058978816]:
        await ctx.send(file=discord.File("reddit_disc.log"))



@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
         await ctx.send('Please input all required arguments.', delete_after=25)
    elif isinstance(error, commands.CommandNotFound):
        return 
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f'You are missing permissions to run this command. `{error}`', delete_after=25)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Invalid user!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You\'re on {str(error.cooldown.type).split(".")[-1]} cooldown for this command. Try again in {round(error.retry_after)} seconds.')
    elif isinstance(error, aiohttp.client_exceptions.ClientOSError):
        u = bot.get_user(602569683543130113)
        if not u:
            u = await bot.fetch_user(602569683543130113)
        if u:
            await u.send(file=discord.File("reddit_disc.log"))
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        logger = logging.getLogger('reddit_disc')
        logger.error(error,exc_info=True)



@bot.event
async def on_component(ctx):
    if ctx.origin_message.author.id != bot.user.id:
        return
    await ctx.defer(ignore=True)
    username = ctx.origin_message.embeds[0].title.split("u/")[-1].split(" ")[0]
    postid = ctx.origin_message.embeds[0].url.strip("/").split("/")[-1]
    if str(ctx.channel_id) == str(settings['rising_channel']):
        await db.mod_rising_post(ctx.author_id,ctx.component['label'],postid)
    elif str(ctx.channel_id) == str(settings['hot_channel']):
        await db.mod_hot_post(ctx.author_id,ctx.component['label'],postid)
    if ctx.custom_id == "approve":
        result = await reddit.approve(postid)
    elif ctx.custom_id == "reject":
        result = await reddit.remove(postid)
    if ctx.custom_id == "capprove":
        result = await reddit.capprove(postid)
    elif ctx.custom_id == "creject":
        result = await reddit.cremove(postid)
    elif ctx.custom_id == "cshadowban":
        result = await reddit.shadowban(username)
        if result == True:
            result = await reddit.cremove(postid)
    elif ctx.custom_id == "c7day":
        result = await reddit.sevendayban(username,f"{ctx.author.name}#{ctx.author.discriminator}")
        if result == True:
            result = await reddit.cremove(postid)
    elif ctx.custom_id == "shadowban":
        result = await reddit.shadowban(username)
        if result == True:
            result = await reddit.remove(postid)
    elif ctx.custom_id == "7day":
        result = await reddit.sevendayban(username,f"{ctx.author.name}#{ctx.author.discriminator}")
        if result == True:
            result = await reddit.remove(postid)
    elif ctx.custom_id == "rshadowban":
        result = await reddit.unshadowban(username)
        if result == True:
            result = await reddit.approve(postid)
    elif ctx.custom_id == "crshadowban":
        result = await reddit.unshadowban(username)
        if result == True:
            result = await reddit.capprove(postid)
    if result == True:
        if int(settings['mod_action_logs_channel']) !=0:
            msgd={
                'approve': ['Post approval',0x00FF00],
                'reject': ['Post removal',0xFF0000],
                'capprove': ['Comment approval',0x00FF00],
                'creject': ['Comment removal',0xFF0000],
                'shadowban': ['Shadowban',0x808080],
                '7day': ['7 day ban',0xcb4154],
                'cshadowban': ['Shadowban',0x808080],
                'c7day': ['7 day ban',0xcb4154],
                'crshadowban': ['Shadowban removal',0x00FF00],
                'rshadowban': ['Shadowban removal',0x00FF00]
            }
            logs = bot.get_channel(int(settings['mod_action_logs_channel']))
            await logs.send(embed=discord.Embed(
                title=f"Action by {ctx.author.name}#{ctx.author.discriminator}",
                url=ctx.origin_message.jump_url,
                description=f"{msgd.get(ctx.custom_id)[0]} for u/{username} in [this post]({ctx.origin_message.embeds[0].url})",
                color = msgd.get(ctx.custom_id)[1]
            ))
        await ctx.origin_message.delete()
    else:
        await ctx.send(f"Action failed. Error: {result}",hidden=True)


bot.run(settings.get("token"))
