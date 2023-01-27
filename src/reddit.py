import json,os,sys
import asyncpraw
import db
import discord

f= open("config.json","r")
settings = json.load(f)
f.close()

f = open("botlist.txt","r")
botlist = f.read().split("\n")
f.close()

token = settings.get("refresh_token",None)
reddit = asyncpraw.Reddit(
    client_id=settings.get("client_id"),
    client_secret=settings.get("client_secret"),
    user_agent="Mod bot test by u/Aman25ta",
    refresh_token=token,
    redirect_uri="https://localhost/"
)



async def get_link():
    """
    Check README.md

    """
    if not settings.get("refresh_token",None):
        print(reddit.auth.url(["*"], "...", "permanent"))
        url = input("Enter url after authorization: ")

        ref_token=await reddit.auth.authorize(url.split("...&code=")[-1].strip("#_"))

        with open('config.json','r') as cfg:
            data=json.load(cfg)
        data['refresh_token']=ref_token
        with open('config.json','w') as cfg:
            data=json.dump(data,cfg,indent=2)
        os.execv(sys.executable,['python']+sys.argv)



async def latest_rising_posts():
    sub = await reddit.subreddit(settings.get("subreddit"))
    posted_rising = await db.get_rising_posted()
    temp_list = []
    return_list = []
    async for i in sub.rising(limit=50):
        if i.id in posted_rising:
            continue
        elif i.score >= 400:
            await db.insert_rising_post((i.id,i.author.name))
            fu=None
            if i.author_flair_richtext and len(i.author_flair_richtext)!=0:
                  fu = i.author_flair_richtext[0].get('u',None)
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
    return return_list


async def latest_hot_posts():
    sub = await reddit.subreddit(settings.get("subreddit"))
    posted_hot = await db.get_hot_posted()
    temp_list = []
    return_list = []
    async for i in sub.hot(limit=25):
        if i.id in posted_hot:
            continue
        else:
            await db.insert_hot_post((i.id,i.author.name))
            fu=None
            if i.author_flair_richtext and len(i.author_flair_richtext)!=0:
                  fu = i.author_flair_richtext[0].get('u',None)
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
    return return_list


async def unmoderated_stream():
    subreddit = await reddit.subreddit(settings.get("subreddit"))
    async for post in subreddit.mod.stream.spam(skip_existing=True):
        if post.author_flair_css_class == "f":
            if type(post) == asyncpraw.models.Submission:
                url = post.url
                if url.endswith(('.jpg', '.png', '.gif', '.jpeg', '.gifv', '.svg')):   
                    embed = discord.Embed(
                        description=post.title,
                        title= f"New post by u/{post.author.name}",
                        url=f"https://www.reddit.com/r/{settings.get('subreddit')}/comments/{post.id}"
                    ).set_image(url=url)
                elif post.is_self:
                    embed = discord.Embed(
                        description=post.title,
                        url=f"https://www.reddit.com/r/{settings.get('subreddit')}/comments/{post.id}",
                        title= f"New post by u/{post.author.name}\n\n{post.selftext}"
                    )
                else:
                    embed = discord.Embed(
                        description=post.title,
                        title= f"New post by u/{post.author.name}",
                        url=f"https://www.reddit.com/r/{settings.get('subreddit')}/comments/{post.id}"
                    )
                yield [embed,'p']
            if type(post) == asyncpraw.models.Comment:
                embed = discord.Embed(title=f"New comment by u/{post.author.name}",url=f"https://www.reddit.com/r/{settings.get('subreddit')}/comments/{post.id}",description=post.body)
                yield [embed,'c']






async def last1k():
    #new posts stream
    #check for flair, then check post history
    subreddit = await reddit.subreddit(settings.get("subreddit"))
    async for i in subreddit.stream.submissions(skip_existing=True):
        if i.author_flair_richtext and len(i.author_flair_richtext)!=0:
            fu = i.author_flair_richtext
            userhas=False
            ok=False
            flairs = ''
            if fu:
                for j in fu:
                    flairs = flairs + j.get('a','')
                    if ":gooduser:" in j.get('a',None):
                        userhas=True
                        break
            if userhas:
                continue
            else:
                await i.author.load()
                listupv=[]
                async for k in i.author.submissions.top(limit=1000):
                    if len(listupv) == 5:
                        break
                    if 1000 - sum(listupv) > i.score and len(listupv) == 4:
                        break

                    if str(k.subreddit).lower() == settings.get("subreddit").lower():
                        listupv.append(k.score)
                if sum(listupv) >= 1000:
                    ok = True
                    counter=0
                    async for k in i.author.comments.new(limit=1000):
                        if str(k.subreddit).lower() == settings.get("subreddit").lower():
                            counter+=1
                        if counter==50:
                            break
                    if counter < 50:
                        ok = False
                if ok:
                    await subreddit.flair.set(
                        redditor=i.author.name,
                        text=f"{flairs} :gooduser:"
                    )


async def modlog_stream():
    subreddit = await reddit.subreddit(settings.get("subreddit"))
    async for modlog in subreddit.mod.stream.log(skip_existing=True):
        if modlog.action.lower() == "distinguish":
            if modlog.mod not in botlist:
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
        if type(post) == asyncpraw.models.Comment:
            embed = discord.Embed(title=f"New comment by u/{post.author.name}",url=f"https://www.reddit.com/r/{settings.get('subreddit')}/comments/{post.id}",description=post.body)
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
            css_class="f"
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

