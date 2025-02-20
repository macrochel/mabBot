import telebot, logging, db, json, requests
from telebot.types import ReplyKeyboardRemove
from keyboard import menu, social, profile, steps
from os import path as pather
from sys import stdout
from decouple import config
from validator import phone

bot = telebot.TeleBot(config("API_KEY"))
API_URL = "https://n8n.bitscompany.kz/webhook/google-sheets" #API google sheets
API_OpenAI = "https://n8n.bitscompany.kz/webhook/llm"

filterList = ["/start", "⬅️Вернуться на прошлый шаг"]

#Logging into console
logger = logging.getLogger("logger")
logger.setLevel(level=logging.DEBUG)
logStreamFormatter = logging.Formatter(
  fmt=f"%(levelname)s %(asctime)s - %(message)s", 
  datefmt="%H:%M:%S"
)
consoleHandler = logging.StreamHandler(stream=stdout)
consoleHandler.setFormatter(logStreamFormatter)
consoleHandler.setLevel(level=logging.DEBUG)
logger.addHandler(consoleHandler)

#Logging into .log file
logFileFormatter = logging.Formatter(
    fmt=f"%(levelname)s %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
fileHandler = logging.FileHandler(filename="storage/loggs/.log")
fileHandler.setFormatter(logFileFormatter)
fileHandler.setLevel(level=logging.INFO)
logger.addHandler(fileHandler)

try:
    dbc, coll = db.init()
    logger.info("✅ Успешное подключение к базе данных")
except Exception as e:
    logger.error(f"❌ Ошибка подключения к базе данных: {e}")
    exit(1) 

#Commands handler
@bot.message_handler(commands=["start"])
def command_message(message):
    if message.text == "/start":
        user = db.findUser(coll, message)  
        logger.info(f"🔍 Пользователь: {user}")  
        if user is None:  
            msg = "👋🏻 Привет, абитуриент!)\nЯ помогу тебе сделать первый шаг в увлекательный мир профессионального развития и карьерного продвижения"
            sendCaptionPhoto(message.chat.id, 1, msg, ReplyKeyboardRemove())
            msg = "Давай знакомиться!\n\n👤 Напиши свое ФИО\n\nЖелательно напиши свое ФИО так как в написано у тебя в государственных документах (удостоверение личности)"
            bot.send_message(message.chat.id, msg)
            bot.register_next_step_handler(message, getName)
        else:
            msg = "👋🏻 Привет снова!\nРад тебя видеть 😊"
            sendCaptionPhoto(message.chat.id, 1, msg, menu())

#Text handler
@bot.message_handler(content_types=["text"])
def text_message(message):
    if message.text == "👤Профиль":
        user = db.findUser(coll, message)
        msg = f"👤ФИО: {user['name']}\n📱Номер телефона: {user['phone']}\n📟id: {message.chat.id}\n🎓Образование: {user['education']}\n🔧Hard skills: {user['hardSkills']}\n🗣Soft skills: {user['softSkills']}\n🗂Дополнительная информация: {user['addInfo']}"
        bot.send_message(message.chat.id, msg, reply_markup=profile())
    elif message.text == "☎️Контакты":
        msg = "📍Улица Мустафы Озтюрка, 5а\n\n📞Приемная:\n+7-707-846-44-27\n+7-727-302-23-03"
        bot.send_message(message.chat.id, msg, reply_markup=social())
    elif message.text == "📝Записаться на консультацию":
        user = db.findUser(coll, message)  
        logger.info(f"🔍 Пользователь: {user}")
        if user["consultation"]:
            try:
                response = requests.post(API_URL, json=user, headers={"Content-Type": "application/json"})
                logger.info(f"📤 Ответ API: {response.status_code}, {response.text}")
            except Exception as e:
                logger.error(f"❌ Ошибка при отправке API: {e}")
        msg = "Спасибо за запись! С тобой обязательно свяжутся 🤗"
        bot.send_message(message.chat.id, msg)
        db.addColumn(coll, "consultation", message)
    elif message.text == "❓Частые вопросы":
        msg = "https://teletype.in/@microchel.txt/QOlWJn9ape"
        bot.send_message(message.chat.id, msg)

#Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "getProf":
        msg = "👀 Анализирую твой профиль"
        bot.send_message(call.message.chat.id, msg)
        user = db.findUser(coll, call.message)  
        logger.info(f"🔍 Пользователь: {user}")
        try:
            response = requests.post(API_OpenAI, json=user, headers={"Content-Type": "application/json"})
            logger.info(f"📤 Ответ API: {response.status_code}, {response.text}")
            msg = response.text
            bot.send_message(call.message.chat.id, msg)
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке API: {e}")
            msg = "❌ Ошибка при анализе"
            bot.send_message(call.message.chat.id, msg)
    elif call.data == "restart":
        msg = "Давай знакомиться!\n\n👤 Напиши свое ФИО\n\nЖелательно напиши свое ФИО так как в написано у тебя в государственных документах (удостоверение личности)"
        bot.send_message(call.message.chat.id, msg, reply_markup=steps())
        bot.register_next_step_handler(call.message, getName)

#Functions
def goHome(message):
        msg = "Добро пожаловать в меню!"
        bot.send_message(message.chat.id, msg, reply_markup=menu())

def sendCaptionPhoto(chatid, number, msg, keyboard):
    path = "storage/pictures/" + str(number) + ".png"
    if not pather.exists(path):
        bot.send_message(chatid, f"Фото не найдено  {path}")
        return
    with open(path, "rb") as photo:
        bot.send_photo(chatid, photo, msg, reply_markup=keyboard)

#Step handlers
def getName(message):
    if message.text not in filterList:
        msg = "📞 Напиши свой номер телефона в формате «+77001234567»\n\nУкажи актуальный номер телефона, на который ты 100% ответишь в рабочее время"
        bot.send_message(message.chat.id, msg, reply_markup=steps())
        x = db.initUser(coll, message)
        logger.info(f"✅ Новый пользователь создан: {x}")  
        bot.register_next_step_handler(message, getPhone)
        db.addColumn(coll, "name", message)

def getPhone(message):
    if message.text not in filterList and phone(message.text):
        msg = "🏫 Укажи сколько классов ты окончил\n\nМожешь указать дополнительное образования курсы, которые проходили и т.п"
        bot.send_message(message.chat.id, msg)
        db.addColumn(coll, "phone", message)
        bot.register_next_step_handler(message, getEducation)        
    elif phone(message.text) != True:
        msg = "❌ Некорректный формат ввода телефона, вводите номер в формате «+77001234567»"
        bot.send_message(message.chat.id, msg, reply_markup=nextstep())
        bot.register_next_step_handler(message, getPhone)
    elif message.text == "⬅️Вернуться на прошлый шаг":
        msg = "Давай знакомиться!\n\n👤 Напиши свое ФИО\n\nЖелательно напиши свое ФИО так как в написано у тебя в государственных документах (удостоверение личности)"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, getName)

def getEducation(message):
    if message.text not in filterList:
        msg = "Укажи свои практические навыки. Например, владение конкретными языками программирования, знание основ разных видов учета"
        bot.send_message(message.chat.id, msg)
        db.addColumn(coll, "education", message)
        bot.register_next_step_handler(message, getHard)
    elif message.text == "⬅️Вернуться на прошлый шаг":
        msg = "📞 Напиши свой номер телефона в формате «+77001234567»\n\nУкажи актуальный номер телефона, на который ты 100% ответишь в рабочее время"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, getPhone)

def getHard(message):
    if message.text not in filterList:
        msg = "Навыки Soft skills\n\nКоммуникабельность, ответственность, уверенный пользователь ПК…\n\nЛучше указывайте soft skills. Например:\n- Навык ведения тренингов.\n- Навык управления несколькими проектами.\n- Высокий эмоциональный интеллект.\n- Знание иностранного языка и т.п.\n\nА если вам хочется рассказать о своих личных качествах, то упомяните их в разделе «Дополнительные сведения»"
        bot.send_message(message.chat.id, msg)
        db.addColumn(coll, "hardSkills", message)
        bot.register_next_step_handler(message, getSoft)
    elif message.text == "⬅️Вернуться на прошлый шаг":
        msg = "Укажи свои практические навыки. Например, владение конкретными языками программирования, знание основ разных видов учета"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, getHard)

def getSoft(message):
    if message.text not in filterList:
        msg = "Дополнительные сведения.\n\nПример, как правильно заполнять этот раздел:\n\nВерно:\nВыстраиваю отношения с окружающими, основанные на взаимоуважение и доверии.\n\nНеверно:\nКоммуникабельность."
        bot.send_message(message.chat.id, msg)
        db.addColumn(coll, "softSkills", message)
        bot.register_next_step_handler(message, getInfo)
    elif message.text == "⬅️Вернуться на прошлый шаг":
        msg = "Навыки Soft skills\n\nКоммуникабельность, ответственность, уверенный пользователь ПК…\n\nЛучше указывайте soft skills. Например:\n- Навык ведения тренингов.\n- Навык управления несколькими проектами.\n- Высокий эмоциональный интеллект.\n- Знание иностранного языка и т.п.\n\nА если вам хочется рассказать о своих личных качествах, то упомяните их в разделе «Дополнительные сведения»"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, getSoft)

def getInfo(message):
    if message.text not in filterList:
        msg = "😊 Рад знакомству!"
        bot.send_message(message.chat.id, msg, reply_markup=menu())
        db.addColumn(coll, "addInfo", message)
    elif message.text == "⬅️Вернуться на прошлый шаг":
        msg = "Дополнительные сведения.\n\nПример, как правильно заполнять этот раздел:\n\nВерно:\nВыстраиваю отношения с окружающими, основанные на взаимоуважение и доверии.\n\nНеверно:\nКоммуникабельность."
        bot.send_message(message.chat.id, msg)
        db.addColumn(coll, "softSkills", message)
        bot.register_next_step_handler(message, getSoft)

#Polling
bot.polling(none_stop = True)