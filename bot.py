import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import requests
import owncloud

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ['BOT_TOKEN']
ADDRESS = os.environ['BOT_ADDRESS']
ALLOWED_USER = os.environ['ALLOWED_USER']
NEXTCLOUD_URL = os.environ['NEXTCLOUD_URL']
NEXTCLOUD_USERNAME = os.environ['NEXTCLOUD_USERNAME']
NEXTCLOUD_PASSWORD = os.environ['NEXTCLOUD_PASSWORD']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def rose(update, context):
    """Send a message when the command /rose is issued."""

    url = 'https://api.github.com/repos/rose-compiler/rose/git/refs/heads/release'
    roseReleaseCommit = requests.get(url).json()['object']['sha']

    update.message.reply_text(roseReleaseCommit)

def nclink(update, context):
    """Send a message when the command /nclink is issued."""
    oc = owncloud.Client(NEXTCLOUD_URL)
    oc.login(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)

    if oc.is_shared('Documents'):
        link_info = oc.get_shares('Documents')
        sharingLink = link_info[0].get_link()
    else:
        link_info = oc.share_file_with_link('Documents')
        sharingLink = link_info.get_link()

    update.message.reply_text(sharingLink)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, Filters.user(username=ALLOWED_USER)))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("rose", rose))
    dp.add_handler(CommandHandler("nclink", nclink))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(ADDRESS + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
