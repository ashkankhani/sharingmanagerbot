from pytz import timezone
from datetime import datetime  
from datetime import timedelta  


iran = timezone('Asia/Tehran')

test = datetime.now(iran) + timedelta(days = 7)
print(test)




from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from telegram.ext import Updater




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

def test():
    print('test')
    
updater = Updater('1924233905:AAGMhEiPXvJQYMpr71A6GVmf6wWseERYQD4')


scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.add_job(test , trigger='date' ,run_date='2021-08-21 12:53:05',timezone = iran , misfire_grace_time = 30 * 24 * 3600)
scheduler.add_job(test , trigger='date' ,run_date='2021-08-20 12:53:05',timezone = iran , misfire_grace_time = 30 * 24 * 3600)
scheduler.add_job(test , trigger='date' ,run_date='2021-08-19 12:53:05',timezone = iran , misfire_grace_time = 30 * 24 * 3600)
scheduler.add_job(test , trigger='date' ,run_date='2021-08-18 12:53:05',timezone = iran , misfire_grace_time = 30 * 24 * 3600)




scheduler.start()
updater.start_polling()
updater.idle()
