import os
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from random import choice
from instabot import Bot as InstaBot

# Load environment variables from the system environment
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')  # e.g., '@examplechannel'
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')  # To send errors to your admin account
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Initialize Telegram client
client = TelegramClient('session_name', API_ID, API_HASH)
client.start()

# Initialize Telegram bot
telegram_bot = Bot(token=BOT_TOKEN)

# Initialize Instagram bot
insta_bot = InstaBot()
insta_bot.login(username=INSTAGRAM_USERNAME, password=INSTAGRAM_PASSWORD)

def fetch_random_post():
    try:
        # Get history
        posts = client(GetHistoryRequest(
            peer=CHANNEL_USERNAME,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=100,  # You can adjust the limit
            max_id=0,
            min_id=0,
            hash=0
        )).messages

        if posts:
            # Choose a random post
            post = choice(posts)
            return post.message or post.media
        else:
            return None
    except Exception as e:
        telegram_bot.send_message(chat_id=ADMIN_USER_ID, text=f"Error fetching post: {e}")
        return None

def post_on_instagram(post):
    try:
        if post:
            insta_bot.upload_photo(post, caption=post)
        else:
            telegram_bot.send_message(chat_id=ADMIN_USER_ID, text="No posts found to repost.")
    except Exception as e:
        telegram_bot.send_message(chat_id=ADMIN_USER_ID, text=f"Error posting on Instagram: {e}")

def main():
    scheduler = BlockingScheduler()
    # Schedule the job every 2 hours
    scheduler.add_job(lambda: post_on_instagram(fetch_random_post()), 'interval', hours=2)
    scheduler.start()

if __name__ == '__main__':
    main()
