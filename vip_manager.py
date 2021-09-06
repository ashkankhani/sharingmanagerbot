from logging import Filter
import sqlite3
import jdatetime
from pytz import timezone
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from telegram.ext import Updater,MessageHandler,CallbackContext
from telegram import Update
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup




TOKEN = '1939997594:AAHesGv-8IIZpQaHaivY1QewnE36V8Eo0ag'
BOT_MAKER = 800882871
#ADMIN_ID = 800882871
ADMIN_ID = 1148289066
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
    cursor.execute(f'''select first_name , last_name , user_name , user_id
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
        updater.bot.send_message(chat_id = ADMIN_ID,text = 'در ارسال پیام به یک عضو وی آی پی خطا رخ داد!')

    first_name , last_name , user_name , user_id = get_user_info_db(user_id)
    try:
        updater.bot.send_message(chat_id = ADMIN_ID,text = f'''ادمین عزیز سلام
اشتراک فردی با این مشخصات تا 24 ساعت آینده ابطال میگردد:
نام : {first_name}
نام خانوادگی : {last_name}
یوزرنیم : @{user_name}
آیدی عددی : {user_id}
فرد مورد نظر نیز توسط پیامی آگاه سازی شد
''')
    except:
        print('cant send message to admin!')
    




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
    delta_time = datetime.timedelta(days = days)
    seconds = delta_time.total_seconds()
    before_date_jalali = get_database_date(user_id)
    year , month , day , hour , minute , second = before_date_jalali
    after_date_jalali = jdatetime.datetime(year , month , day , hour , minute , second) + jdatetime.timedelta(days=days)
    year , month , day , hour , minute , second = after_date_jalali.year , after_date_jalali.month , after_date_jalali.day , after_date_jalali.hour , after_date_jalali.minute , after_date_jalali.second
    connection = sqlite3.connect('vip_manager.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'''update apscheduler_jobs
    set next_run_time = next_run_time + {seconds} , year = {year}, month = {month} , day = {day} , hour = {hour} , minute = {minute} , second = {second}
    where user_id = {user_id}
    ''')
    connection.commit()
    connection.close()
    return after_date_jalali


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

def after_jalali_date(days):
    after_date_jalali = jdatetime.datetime.now(iran) + jdatetime.timedelta(days = days)
    return after_date_jalali




def charge (user_id,days):
    now_date = datetime.datetime.now(iran)
    after_date = now_date + datetime.timedelta(days = days - 1) 
    after_date_jalali = after_jalali_date(days)
    after_date_jalali_tup = (after_date_jalali.year , after_date_jalali.month , after_date_jalali.day , after_date_jalali.hour , after_date_jalali.minute , after_date_jalali.second)
    remind = scheduler.add_job(reminder, 'date', run_date=after_date, args=[user_id] , misfire_grace_time=365 * 24 * 60 * 60,timezone = iran)
    job_code = remind.id
    submit_charge_user_id_date(job_code,user_id,after_date_jalali_tup)
    return after_date_jalali

    

    

def tamdid_manager(update : Update , context : CallbackContext):
    query = update.callback_query
    data_list = (query.data.split(','))[1:]
    user_id = data_list[0]
    days = int(data_list[1])
    if(have_charge(user_id)):
        date = recharge(user_id,days)
    else:
        date = charge(user_id , days)

    str_date = date.strftime("14%y/%m/%d %H:%M:%S")
    context.bot.send_message(text = f'''حق اشراک فرد مورد نظر با آیدی : {user_id}
تا تاریخ:
{str_date}
با موفقیت تمدید شد!
''',chat_id = ADMIN_ID)
    try:
        context.bot.send_message(text = f'''حق اشراک شما با آیدی : {user_id}
    تا تاریخ:
    {str_date}
    با موفقیت تمدید شد!
    ''',chat_id = user_id)
    except:
        context.bot.send_message(text = f'''در ارسال پیام تمدید به فردی با ایدی زیر,خطا روی داده است
این خطا ممکن است ناشی از بلاک کردن و یا استارت نکردن ربات از فرد مورد نظر باشد...
آیدی:
{user_id}
''',chat_id = ADMIN_ID)
    else:
        context.bot.send_message(text = 'پیام تمدید با موفقیت به عضو vip ارسال شد!' , chat_id = ADMIN_ID)





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
یوزرنیم : @{user_name}
آیدی عددی : {user_id}
''' , reply_markup=inline_keyboard_markup)
    else:
        update.message.reply_text('''احتمالا فوروارد شخص مورد نظر قفل هستش...
بنابراین از عضو vip جدید بخواین که فورواردشو وا کنه...
        ''')








def help (update : Update , context : CallbackContext):
    update.message.reply_text('''ادمین عزیز سلام
به ربات خودتون خوش اومدین...
برای کار کردن با این ربات لازمه دو نکته رو رعایت کنین:
1.در جهت اد کردن فردی به لیست لازمه که ازش بخواین قفل فورواردشو باز کنه
2.از کاربر مورد نظر بخواین که ربات رو استارت کنه که رسید به ایشون هم ارسال بشه
3.با فوروارد کردن پيامي از کاربر مورد نظر به ربات و مشخص کردن دوره آن,ميتوايند اشتراک فرد مورد نظر را تمديد کنيد!
''')




def start(update : Update , context : CallbackContext):
    update.message.reply_text('''دو نوع تعرفه برای تبلیغ در گروه داریم:

✅ هفتگی 👈🏻 ۳۰ هزار تومان

✅ ماهانه 👈🏻 ۷۵ هزار تومان

▫️محدودیت برداشته میشه براتون
▫️با خرید حق اشتراک امکان تبلیغ و درج آگهی توانمندی بدون محدودیت براتون ایجاد میشه. 
▫️از سایر پیام‌های تبلیغاتی جلوگیری میشه تا کسانی که حق اشتراک میخرن بهتر دیده بشن
▫️فقط خواهشا به صورت رگباری و مزاحم گونه تبلیغ نکنید. مثلا هر ۱۵ دقیقه یک پیام برای تبلیغ کارتون بزارید🌹

برای اقدام به خرید اشتراک مورد نظر,با آیدی زیر در ارتباط باشید:
@Lesson_perfect
''')





def main():

    dispatcher = updater.dispatcher

    tamdid_manager_handler = CallbackQueryHandler(tamdid_manager ,pattern='^t,\d*,\d+$')

    help_handler = MessageHandler(Filters.chat(ADMIN_ID) | Filters.chat(BOT_MAKER), help)
    start_handler = MessageHandler(Filters.all, start)


    forward_from_vip_user_handler = MessageHandler((Filters.chat(ADMIN_ID) | Filters.chat(BOT_MAKER)) & Filters.forwarded , tayid)


    dispatcher.add_handler(forward_from_vip_user_handler)
    dispatcher.add_handler(tamdid_manager_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(start_handler)









    updater.start_polling()
    updater.idle()

    


if(__name__ == '__main__'):
    main()











