import json
import asyncpraw
import db


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
        print(vars(i))
        return []
        if i.id in posted_rising:
            continue
        else:
            posted_rising.append(i.id)
            temp_list.append((i.id,i.author.name))
            fu=None
            if not i.link_flair_text:
                  fu = i.author_flair_richtext[0]['u']
            return_list.append({
                "username": i.author.name,
                "postid": i.id,
                "score": i.score,
                "title": i.title,
                "selftext": i.selftext,
                "url": i.url,
                "is_self": i.is_self,
                "flair_url": fu
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
            posted_rising.append(i.id)
            temp_list.append((i.id,i.author.name))
            fu=None
            if not i.link_flair_text:
                  fu = i.author_flair_richtext[0]['u']
            return_list.append({
                "username": i.author.name,
                "postid": i.id,
                "score": i.score,
                "title": i.title,
                "selftext": i.selftext,
                "url": i.url,
                "is_self": i.is_self,
                "flair_url": fu
            })
    await db.insert_hot_posts(temp_list)
    pass



async def approve(pid):
    try:
        await reddit.submission(id=pid).approve()
        return True
    except Exception as e:
        return e

async def shadowban(username):
    try:
        await subreddit.flair.set(
            redditor=username,
            flair_template_id="63da9b16-80b7-11ea-99ef-0e10a6a106e1"
        )
        return True
    except Exception as e:
        return e

async def remove(pid):
    try:
        await reddit.submission(id=pid).remove()
        return True
    except Exception as e:
        return e

async def sevendayban(username,modname):
    try:
        (await reddit.subreddit(settings.get("subreddit"))).banned.add(username,ban_reason(f"Ban from discord by {modname}"))
        return True
    except Exception as e:
        return e


