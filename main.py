import discord
from discord.ext import commands,tasks
from discord_slash import SlashCommand 
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
import json
import reddit
import asyncio

f= open("config.json","r")
settings = json.load(f)
f.close()

bot = commands.Bot(command_prefix=">")

slash = SlashCommand(bot,sync_commands=True)



@bot.event
async def on_ready():
    await reddit.get_link()
    check1.start()
    print("bot has started")


@tasks.loop(seconds=25*1)
async def check1():
    rising = await reddit.latest_rising_posts()
    hot = await reddit.latest_hot_posts()
    channel1 = bot.get_channel(int(settings['rising_channel']))
    channel2 = bot.get_channel(int(settings['hot_channel']))
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
        if i['url'].endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
            embed.set_image(url=i['url'])
        elif i['is_self']:
            embed.add_field(name="selftext",value=i['selftext'])

        await channel1.send(embed=embed,components=[actRow])
        await asyncio.sleep(5)

    for i in hot:
        embed = discord.Embed(
            title=f"Post by u/{i['username']} has reached hot",
            url=f"https://reddit.com/{i['id']}",
            color=0xFFFF00
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
        if i['url'].endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
            embed.set_image(url=i['url'])
        elif i['is_self']:
            embed.add_field(name="selftext",value=i['selftext'])

        await channel2.send(embed=embed,components=[actRow])
        await asyncio.sleep(5)

    print("---------")






@bot.event
async def on_component(ctx):
    if ctx.origin_message.author.id != bot.user.id:
        return
    username = ctx.origin_message.embeds[0].title.split("u/")[-1].split(" ")[0]
    postid = ctx.origin_message.embeds[0].url.split("/")[-1]
    if ctx.custom_id == "approve":
        result = await reddit.approve(postid)
    elif ctx.custom_id == "reject":
        result = await reddit.remove(postid)
    elif ctx.custom_id == "shadowban":
        result = await reddit.shadowban(username)
    elif ctx.custom_id == "7day":
        result = await reddit.sevendayban(username,f"{ctx.author.name}#{ctx.author.discriminator}")
    if result == True:
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
