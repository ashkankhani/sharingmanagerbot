import sqlite3
import jdatetime
from pytz import timezone
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from telegram.ext import Updater,MessageHandler,ConversationHandler,CallbackContext,CommandHandler
from telegram import Update
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup




TOKEN = '1939997594:AAHesGv-8IIZpQaHaivY1QewnE36V8Eo0ag'
BOT_MAKER = 800882871
updater = Updater(TOKEN)
iran = timezone('Asia/Tehran')

after_date_jalali = str(jdatetime.datetime.now(iran) + jdatetime.timedelta(days = 7))
print(after_date_jalali.year)