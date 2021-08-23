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



TAMDID = range(1)




jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///vip_manager.sqlite')
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

def get_user_info_db(user_id):
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'''select first_name , last_name , user_name
    from users_info
    where user_id = {user_id}
    ''')
    res = cursor.fetchone()
    return res

def reminder(user_id):
    try:
        updater.bot.send_message(chat_id = user_id,text = '''با سلام
    تنها یک روز به پایان اعتبار حساب vip شما باقی مانده است...
    برای تمدید میتوانید به این آیدی پیام داده و پیگیری های لازم را انجام دهید:
    @Lesson_perfect
    ''')
    except:
        updater.bot.send_message(chat_id = BOT_MAKER,text = 'در ارسال پیام به یک عضو وی آی پی خطا رخ داد!')

    first_name , last_name , user_name = get_user_info_db(user_id)
    updater.bot.send_message(chat_id = BOT_MAKER,text = f'''ادمین عزیز سلام
اشتراک فردی با این مشخصات تا 24 ساعت آینده ابطال میگردد:
نام : {first_name}
نام خانوادگی : {last_name}
یوزرنیم : {user_name}
فرد مورد نظر نیز توسط پیامی آگاه سازی شد
''')
    






def have_charge(user_id):
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'''select id
    from apscheduler_jobs
    where user_id = {user_id}
    ''')
    res = cursor.fetchone()
    if(res):
        return True
    return False

def get_database_date(user_id):
    connection =  sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'''select year , month , day , hour , minute , second
    from apscheduler_jobs
    where user_id = {user_id}
    ''')
    res =  cursor.fetchone()
    return res


def recharge(user_id,days):
    delta_time = datetime.timedelta(days = days - 1)
    seconds = delta_time.total_seconds()
    before_date_jalali = get_database_date(user_id)
    year , month , day , hour , minute , second = before_date_jalali
    after_date_jalali = jdatetime.datetime(year , month , day , hour , minute) + jdatetime.timedelta(days=days)
    year , month , day , hour , minute , second = after_date_jalali.year , after_date_jalali.month , after_date_jalali.day , after_date_jalali.hour , after_date_jalali.minute , after_date_jalali.second
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'''update apscheduler_jobs
    set next_run_time = next_run_time + {seconds} , year = {year}, month = {month} , day = {day} , hour = {hour} , minute = {minute} , second = {second}
    where user_id = {user_id}
    ''')
    connection.commit()
    connection.close()


def submit_charge_user_id_date(job_code,user_id,after_date_jalali_tup):
    year , month , day , hour , minute , second = after_date_jalali_tup
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute((f'''update apscheduler_jobs
    set user_id = {user_id} , year = {year}, month = {month} , day = {day} , hour = {hour} , minute = {minute} , second = {second}
    where id = '{job_code}'
    '''))
    connection.commit()
    connection.close()




def charge (user_id,days):
    now_date = datetime.datetime.now(iran)
    after_date = now_date + datetime.timedelta(days=days - 1) 
    after_date_jalali = jdatetime.datetime.now(iran) + jdatetime.timedelta(days = days)
    after_date_jalali_tup = (after_date_jalali.year , after_date_jalali.month , after_date_jalali.day , after_date_jalali.hour , after_date_jalali.minute , after_date_jalali.second)
    remind = scheduler.add_job(reminder, 'date', run_date=after_date, args=[user_id])
    job_code = remind.id
    submit_charge_user_id_date(job_code,user_id,after_date_jalali_tup)

    

    

def tamdid_manager(update : Update , context : CallbackContext):
    query = update.callback_query
    data_list = (query.data.split(','))[1:]
    user_id = data_list[0]
    days = int(data_list[1])
    if(have_charge(user_id)):
        recharge(user_id,days)
    else:
        charge(user_id , days)


def user_in_db(user_id):
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'''select id
    from users_info
    where user_id = {user_id}
    ''')
    res = cursor.fetchone()
    connection.close()
    if(res):
        return True
    return False





def submit_user_info(user_id , first_name , last_name , user_name):
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    id = 0
    cursor.execute('''select max(id)
    from users_info
    ''')
    max_res = (cursor.fetchone())[0]
    if(max_res):
        id = max_res
    cursor.execute(f'''insert into users_info
    (id , first_name , last_name , user_id , user_name)
    values
    ({id + 1} , '{first_name}' , '{last_name}' , {user_id} , '{user_name}')
    ''')
    connection.commit()
    connection.close()
    


def tayid(update:Update , context:CallbackContext):
    message = update.message.forward_from
    user_id = message.id
    first_name = message.first_name
    last_name = 'ندارد'
    user_name = 'ندارد'
    if(message.last_name):
        last_name = message.last_name
    if(message.username):
        user_name = message.username
    if(not user_in_db(user_id)):
        submit_user_info(user_id , first_name , last_name , user_name)
    

    
    inline_keyboard_button = [
        [InlineKeyboardButton(text = 'یک هفته',callback_data=f't,{user_id},7') , InlineKeyboardButton(text = 'یک ماه',callback_data=f't,{user_id},30')]
    ]
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_button)
    if(message):
        update.message.reply_text(text = f'''لطفا زمان تمدید را برای فرد مورد نظر تعیین کنید:
نام : {first_name}
نام خانوادگی : {last_name}
یوزرنیم : {user_name}
آیدی عددی : {user_id}
همچنین با دستور /cancel میتوانید این پروسه را لغو کنید''' , reply_markup=inline_keyboard_markup)
    else:
        update.message.reply_text('''احتمالا فوروارد شخص مورد نظر قفل هستش...
بنابراین از عضو vip جدید بخواین که فورواردشو وا کنه...
        ''')



    return TAMDID





def cancel (update : Update , context : CallbackContext):
    update.message.reply_text('شما با موفقیت از محیط تمدید vip خارج شدید!')
    return ConversationHandler.END





#he = scheduler.add_job(test , trigger='date' ,run_date='2021-8-23 11:42:05',timezone = iran , misfire_grace_time = 30 * 24 * 3600)





def main():

    dispatcher = updater.dispatcher

    tamdid_manager_handler = CallbackQueryHandler(tamdid_manager ,pattern='^t,\d*,\d+$')

    forward_from_vip_user_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.forwarded , tayid)],
        states= {

            #TAMDID : [CallbackQueryHandler(tamdid_manager , pattern='^t,\d*,\d+$')]

        },
        fallbacks=[CommandHandler('cancel' , cancel)]
    )


    dispatcher.add_handler(forward_from_vip_user_handler)
    dispatcher.add_handler(tamdid_manager_handler)









    updater.start_polling()
    updater.idle()

    


if(__name__ == '__main__'):
    main()


#connection = sqlite3.connect('jobs.sqlite')
#cursor = connection.cursor()
#cursor.execute(f'''update apscheduler_jobs
#set next_run_time = next_run_time + {hey}''')
#connection.commit()








