# Reddit-discord-modding

Bot to send rising and Hot posts to discord channels to perform mod actions on.

# Setup

Install packages in `requirements.txt` using `pip install -r requirements.txt`

Fill `config.example.json` as `config.json`

`modlog_channel` in `config.json` is for mod award logs and distinguish logs

`mod_action_logs_channel` is logs for actions performed through the bot

Run using `python3 main.py` 

# Refresh token in config.json

How to get the refresh_token for `config.json` (bot will not work otherwise)

Run bot

Authorize given link in console while logged into bot account

Copy the url from the redirect (will be an invalid page), and paste it into the prompt in console.

Bot should work as intended.