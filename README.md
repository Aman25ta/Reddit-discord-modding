# Reddit-discord-modding

Bot to send rising and Hot posts to discord channels to perform mod actions on.

# Setup
Install packages in requirements.txt
Fill config.json

# Refresh token in config.json

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


