from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

def steps():
	steps_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	button1 = KeyboardButton("⬅️Вернуться на прошлый шаг")
	return steps_keyboard

def menu():
	menu_keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
	button1 = KeyboardButton("👤Профиль")
	button2 = KeyboardButton("📝Записаться на консультацию")
	button3 = KeyboardButton("☎️Контакты")
	button5 = KeyboardButton("❓Частые вопросы")
	menu_keyboard.add(button1)
	menu_keyboard.add(button2, button3)
	menu_keyboard.add(button5)
	return menu_keyboard

def social():
    social_keyboard = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton(text="🌐 Сайт", url="https://cmab.edu.kz/")
    button2 = InlineKeyboardButton(text="🗺️ 2GIS", url="https://go.2gis.com/YHuP3")
    button3 = InlineKeyboardButton(text="📷 Instagram", url="https://www.instagram.com/college_mab/")
    button4 = InlineKeyboardButton(text="🎵 TikTok", url="https://www.tiktok.com/@college_mab")
    social_keyboard.add(button1, button2, button3, button4)
    return social_keyboard

def profile():
	profile = InlineKeyboardMarkup(row_width=1)
	button1 = InlineKeyboardButton(text="🧑🏻‍🎓 Какая спецальность мне подходит?", callback_data="getProf")
	button2 = InlineKeyboardButton(text="📝 Заполнить профиль заново", callback_data="restart")
	profile.add(button1)
	profile.add(button2)
	return profile