import sqlite3
import jdatetime
from pytz import timezone
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from telegram.ext import Updater,MessageHandler,ConversationHandler,CallbackContext, dispatcher
from telegram import Update
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.filters import Filters



TOKEN = '1924233905:AAGMhEiPXvJQYMpr71A6GVmf6wWseERYQD4'
BOT_MAKER = 800882871
updater = Updater(TOKEN)
iran = timezone('Asia/Tehran')

SABT = range(1)


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.start()

def test():
    print('test')

def tamdid(update:Update , context:CallbackContext):
    update.message.reply_text(text = 'سلاممممم')



    return SABT







#he = scheduler.add_job(test , trigger='date' ,run_date='2021-8-23 11:42:05',timezone = iran , misfire_grace_time = 30 * 24 * 3600)





def main():

    dispatcher = updater.dispatcher

    forward_from_vip_user_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.forwarded , tamdid)],
        states= {

            SABT : [CallbackQueryHandler]

        }
    )


    dispatcher.add_handler(forward_from_vip_user_handler)









    updater.start_polling()
    updater.idle()

    


if(__name__ == '__main__'):
    main()


#connection = sqlite3.connect('jobs.sqlite')
#cursor = connection.cursor()
#cursor.execute(f'''update apscheduler_jobs
#set next_run_time = next_run_time + {hey}''')
#connection.commit()








