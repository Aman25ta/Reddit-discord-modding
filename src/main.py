import discord
from discord.ext import commands,tasks
from discord_slash import SlashCommand 
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import json
import reddit
import asyncio
import db

f= open("config.json","r")
settings = json.load(f)
f.close()

bot = commands.Bot(command_prefix=">")

slash = SlashCommand(bot,sync_commands=True)



@bot.event
async def on_ready():
    if not settings.get("refresh_token",None):
        await reddit.get_link()
    else:
        check1.start()
        if int(settings['shadow_channel']) != 0:
            check2.start()
        if int(settings['reports_channel']) != 0:
            check3.start()
        if int(settings['modlog_channel']) != 0:
            check4.start()
    print("bot has started")


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
            label = "Reject",
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
                url=f"https://reddit.com/{i['id']}",
                color=0x00FF00
            ).add_field(
                name="Rising post",
                value=f"[Post link](https://reddit.com/{i['id']})"
            ).add_field(
                name="User",
                value=f"[u/{i['username']}](https://reddit.com/u/{i['username']})"
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
                url=f"https://reddit.com/{i['id']}",
                color=0x00FF00
            ).add_field(
                name="Hot post",
                value=f"[Post link](https://reddit.com/{i['id']})"
            ).add_field(
                name="User",
                value=f"[u/{i['username']}](https://reddit.com/u/{i['username']})"
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
            label = "Reject",
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
            label = "Reject",
            custom_id="creject",
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
    async for post in reddit.unmoderated_stream():
        if post[1] == "p":
            await channel.send(embed=post[0],components=[actRow])
        elif post[1] == "c":
            await channel.send(embed=post[0],components=[actRow2])


@tasks.loop()
async def check3():
    channel = bot.get_channel(int(settings['reports_channel']))
    actRow = create_actionrow(
        create_button(
            style=ButtonStyle.blurple,
            label = "Approve",
            custom_id="approve",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Reject",
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
    actRow2 = create_actionrow(
        create_button(
            style=ButtonStyle.blurple,
            label = "Approve",
            custom_id="capprove",
        ),
        create_button(
            style=ButtonStyle.blurple,
            label = "Reject",
            custom_id="creject",
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
    async for post in reddit.report_stream():
        if post[1] == "p":
            await channel.send(embed=post[0],components=[actRow])
        elif post[1] == "c":
            await channel.send(embed=post[0],components=[actRow2])




@tasks.loop()
async def check4():
    channel = bot.get_channel(int(settings['modlog_channel']))
    async for post in reddit.modlog_stream():
        await channel.send(embed=post)






@bot.event
async def on_component(ctx):
    if ctx.origin_message.author.id != bot.user.id:
        return
    username = ctx.origin_message.embeds[0].title.split("u/")[-1].split(" ")[0]
    postid = ctx.origin_message.embeds[0].url.strip("/").split("/")[-1]
    if ctx.channel_id == settings['rising_channel']:
        await db.mod_rising_post(ctx.author_id,ctx.component['label'],postid)
    elif ctx.channel.id == settings['hot_channel']:
        await db.mod_hot_post(ctx.author_id,ctx.component['label'],postid)
    if ctx.custom_id == "approve":
        result = await reddit.approve(postid)
    elif ctx.custom_id == "reject":
        result = await reddit.remove(postid)
    if ctx.custom_id == "capprove":
        result = await reddit.capprove(postid)
    elif ctx.custom_id == "creject":
        result = await reddit.cremove(postid)
    elif ctx.custom_id == "shadowban":
        result = await reddit.shadowban(username)
    elif ctx.custom_id == "7day":
        result = await reddit.sevendayban(username,f"{ctx.author.name}#{ctx.author.discriminator}")
    elif ctx.custom_id == "rshadowban":
        result = await reddit.unshadowban(username)
    if result == True:
        if int(settings['mod_action_logs_channel']) !=0:
            msgd={
                'approve': 'Post approval',
                'reject': 'Post removal',
                'capprove': 'Comment approval',
                'creject': 'Comment removal',
                'shadowban': 'Shadowban',
                '7day': '7 day ban',
                'rshadowban': 'Shadowban removal'
            }
            logs = bot.get_channel(int(settings['mod_action_logs_channel']))
            await logs.send(embed=discord.Embed(
                title=f"Action by {ctx.author.name}#{ctx.author.discriminator}",
                url=ctx.origin_message.jump_url,
                description=f"{msgd.get(ctx.custom_id)} for u/{username} in [this post](https://reddit.com/{postid})"
            ))
        await ctx.edit_origin(embed=ctx.origin_message.embeds[0].set_footer(text=f"Attended by {ctx.author.name}#{ctx.author.discriminator}"),components=[create_actionrow(
        create_button(
            style=ButtonStyle.green,
            label = ctx.component['label'],
            custom_id=ctx.custom_id,
            disabled=True
        ))])

    else:
        await ctx.send(f"Action failed. Error: {result}",hidden=True)


bot.run(settings.get("token"))
