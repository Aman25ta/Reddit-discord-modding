import json
import asyncpraw
import db
import discord

f= open("config.json","r")
settings = json.load(f)
f.close()




reddit = asyncpraw.Reddit(
    client_id=settings.get("client_id"),
    client_secret=settings.get("client_secret"),
    user_agent="pewdiepie subreddit bot test by u/Aman25ta",
    refresh_token=settings.get("refresh_token"),
    redirect_uri="https://localhost/"
)




async def get_link():
    """
    
    How to get the refresh_token for config.json (bot will not work otherwise)

    Uncomment first line (with reddit auth url), and run
    Link will be printed to console (ignore the errors if any)

    Use link in browser *while* Logged in as the bot account, and give access
    It will redirect you to an invalid page, Copy the link on the page

    It should look something like: ' https://localhost/?state=...&code=<code>#_ ' 

    Copy down the <code> without #_

    Re-comment the first line (yes this is important, the token gets invalidated otherwise), and uncomment the second, with your code in <code>

    Place the printed token in the config.json with refresh_token as the key.

    Re-run the app, and comment out the second line too.

    The app should now be working as intended


    """
    # print(reddit.auth.url(["*"], "...", "permanent"))
    # print(await reddit.auth.authorize('<code>'))
    pass

global posted_hot,posted_rising
posted_hot,posted_rising = [],[]


async def latest_rising_posts():
    sub = await reddit.subreddit(settings.get("subreddit"))
    global posted_rising
    if len(posted_rising)==0:
        posted_rising = await db.get_rising_posted()
    temp_list = []
    return_list = []
    async for i in sub.rising(limit=100):
        if i.id in posted_rising:
            continue
        else:
            posted_rising.append(i.id)
            temp_list.append((i.id,i.author.name))
            fu=None
            if not i.link_flair_text and len(i.author_flair_richtext)!=0:
                  fu = i.author_flair_richtext[0]['u']
            return_list.append({
                "username": i.author.name,
                "id": i.id,
                "score": i.score,
                "title": "None" if not i.title else i.title,
                "selftext": "None" if not i.selftext else i.selftext,
                "url": i.url,
                "is_self": i.is_self,
                "flair_url": None if not fu else fu
            })
    await db.insert_rising_posts(temp_list)
    return return_list


async def latest_hot_posts():
    sub = await reddit.subreddit(settings.get("subreddit"))
    global posted_hot
    if len(posted_hot)==0:
        posted_hot = await db.get_hot_posted()
    temp_list = []
    return_list = []
    async for i in sub.hot(limit=100):
        if i.id in posted_hot:
            continue
        else:
            posted_hot.append(i.id)
            temp_list.append((i.id,i.author.name))
            fu=None
            if not i.link_flair_text and len(i.author_flair_richtext)!=0:
                  fu = i.author_flair_richtext[0]['u']
            return_list.append({
                "username": i.author.name,
                "id": i.id,
                "score": i.score,
                "title": "None" if not i.title else i.title,
                "selftext": "None" if not i.selftext else i.selftext,
                "url": i.url,
                "is_self": i.is_self,
                "flair_url": None if not fu else fu
            })
    await db.insert_hot_posts(temp_list)
    return return_list


async def unmoderated_stream():
    subreddit = await reddit.subreddit(settings.get("subreddit"))
    # checks for removed comments+posts and yields embed to send.
    async for post in subreddit.mod.stream.spam(skip_existing=True):
        if post.author_flair_template_id:
            if post.author_flair_template_id == settings['shadow_flair_template_id']:
                if type(post) == asyncpraw.models.Submission:
                    url = post.url
                    if url.endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
                        embed = discord.Embed(
                            title=post.title,
                            description= f"New post by u/{post.author.name}",
                            url=f"https://reddit.com/{post.id}/"
                        ).set_image(url=url)
                    elif post.is_self:
                        embed = discord.Embed(
                            title=post.title,
                            url=f"https://reddit.com/{post.id}/",
                            description= f"New post by u/{post.author.name}\n\n{post.selftext}"
                        )
                    else:
                        embed = discord.Embed(
                            title=post.title,
                            description= f"New post by u/{post.author.name}",
                            url=f"https://reddit.com/{post.id}/"
                        )
                    yield [embed,'p']
                elif type(post) == asyncpraw.models.Comment:
                    embed = discord.Embed(title=f"New comment by u/{post.author.name}",url=f"https://reddit.com/{post.id}/",description=post.body)
                    yield [embed,'c']




async def modlog_stream():
    subreddit = await reddit.subreddit(settings.get("subreddit"))
    async for modlog in subreddit.mod.stream.log(skip_existing=True):
        if modlog.action.lower() == "distinguish":
            embed = discord.Embed(
                title=f"u/{modlog.mod} {'un-distinguished' if modlog.details == 'remove' else 'distinguished'} u/{modlog.target_author}\'s {'comment' if not modlog.target_title else 'post'}",
                url="https://reddit.com"+modlog.target_permalink,
                description=modlog.target_body if modlog.target_body else 'No body'
            )
            yield embed
        elif modlog.action.replace("_","").replace(" ","").lower() == "modawardgiven":
            embed = discord.Embed(
                title=f"u/{modlog.mod} Gave a mod award to u/{modlog.target_author}\'s {'comment' if not modlog.target_title else 'post'}",
                url="https://reddit.com"+modlog.target_permalink,
                description=modlog.target_body if modlog.target_body else 'No body'
            )
            yield embed

async def report_stream():
    subreddit = await reddit.subreddit(settings.get("subreddit"))
    # checks for removed comments+posts and yields embed to send.
    async for post in subreddit.mod.stream.reports(skip_existing=True):
        report = ""
        for i in post.user_reports:
            report = report + str(i[1]) + " - " + i[0] + "\n"
        if len(report) > 3500:
            report = report[0:3500] + "..."
        if type(post) == asyncpraw.models.Submission:
            url = post.url
            if url.endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
                embed = discord.Embed(
                    title=post.title,
                    description= f"New post by u/{post.author.name}",
                    url=f"https://reddit.com/{post.id}/"
                ).set_image(url=url)
            elif post.is_self:
                embed = discord.Embed(
                    title=post.title,
                    url=f"https://reddit.com/{post.id}/",
                    description= f"New post by u/{post.author.name}\n\n{post.selftext}"
                )
            else:
                embed = discord.Embed(
                    title=post.title,
                    description= f"New post by u/{post.author.name}",
                    url=f"https://reddit.com/{post.id}/"
                )
            yield [embed.add_field(name="Reports",value=report),'p']
        elif type(post) == asyncpraw.models.Comment:
            embed = discord.Embed(title=f"New comment by u/{post.author.name}",url=f"https://reddit.com/{post.id}/",description=post.body)
            yield [embed.add_field(name="Reports",value=report),'c']




async def approve(pid):
    try:
        await (await reddit.submission(id=pid)).mod.approve()
        return True
    except Exception as e:
        return e

async def shadowban(username):
    try:
        subreddit = await reddit.subreddit(settings.get("subreddit"))
        await subreddit.flair.set(
            redditor=username,
            flair_template_id=settings['shadow_flair_template_id']
        )
        return True
    except Exception as e:
        return e


async def unshadowban(username):
    try:
        subreddit = await reddit.subreddit(settings.get("subreddit"))
        await subreddit.flair.delete(
            redditor=username
        )
        return True
    except Exception as e:
        return e



async def remove(pid):
    try:
        await (await reddit.submission(id=pid)).mod.remove()
        return True
    except Exception as e:
        return e

async def sevendayban(username,modname):
    try:
        await (await reddit.subreddit(settings.get("subreddit"))).banned.add(username,ban_reason=f"Ban from discord by {modname}",duration=7)
        return True
    except Exception as e:
        return e

async def capprove(pid):
    try:
        await (await reddit.comment(id=pid)).mod.approve()
        return True
    except Exception as e:
        return e

async def cremove(pid):
    try:
        await (await reddit.comment(id=pid)).mod.remove()
        return True
    except Exception as e:
        return e

