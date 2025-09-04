import os
from datetime import datetime, timedelta
import telebot
from threading import Thread
import time
import flask
from colorama import Fore


bot = telebot.TeleBot(os.getenv("bot"))

if os.path.exists("remind.txt"):
    print(f"{Fore.LIGHTGREEN_EX}[INFO] remind.txt found, loading user IDs...{Fore.RESET}")
    with open("remind.txt", "r") as file:
        remind = [int(line.strip()) for line in file if line.strip().isdigit()]
        print(f"{Fore.LIGHTGREEN_EX}[INFO] Current remind list is {remind}")

else:
    print(f"{Fore.LIGHTYELLOW_EX}[INFO] remind.txt not found, creating a new one...{Fore.RESET}")
    with open("remind.txt", "w") as file:
        file.write("")

    remind = []


days = {"Monday": {"8:00":"1. Фізичне виховання, частина 1\n8:00-9:20\n<b>Практична</b>",
                   "10:05":None,
                   "11:40":"3. Вища математика, частина 1\n11:40-13:00\n<b>Кучма М.І., 322 I н.к., Лекція</b>",
                   "13:15":"4. Українська мова за професійним спрямуванням\n13:15-14:35\n<b>Шмілик І.Д., 405 I н.к. Практична</b>",
                   "14:50":"5. Іноземна мова за професійним спрямуванням, частина 1\n14:50-16:10\n<b>Миклаш Л.Т.(1 підгрупа)\\Вислободська І.М.(2 підгрупа), ??? ? н.к. Практична</b>",
                   "16:25":None},

        "Tuesday": {"8:30":None,
                   "10:05":"2. Фізика\n10:05-11:25\n<b>ел.2лаб Гол. н.к., мол.2лаб Гол. н.к., опт.2лаб Гол. н.к., Лабораторна</b>",
                   "11:40":"3. Фізика\n11:40-13:00\n<b>Рудка М.М., 124 Гол. н.к., Лекція</b>",
                   "13:15":"4. Фізика\n13:15-14:35\n<b>Рудка М.М., 134 Гол. н.к., Практична</b>\n<b>ЗНАМЕННИК</b>",
                   "14:50":None,
                   "16:25":None},

        "Wednesday": {"8:30":"1. Вища математика, частина 1\n8:30-9:50\n<b>Страп Н.І., 405 I н.к., Практична</b>\n<b>ЧИСЕЛЬНИК</b>\n\n\n1. Вища математика, частина 1\n8.30-9.50\n<b>Кучма М.І., 322 I н.к., Лекція</b>\n<b>ЗНАМЕННИК</b>",
                   "10:05":"2. Вища математика, частина 1\n10:05-11:25\n<b>Страп Н.І., 405 I н.к., Практична</b>",
                   "11:40":"3. Фізика\n11:40-13:00\n<b>Рудка М.М., 134 Гол. н.к., Практична</b>\n<b>ЗНАМЕННИК</b>",
                   "13:15":"4. Основи інформаційної та кібернетичної безпеки\n14:50-16:10\n<b>Швед М.Є., 212 XIX н.к., Практична</b>\n<b>ЧИСЕЛЬНИК</b>",
                   "14:50":None,
                   "16:25":None},

        "Thursday":{"8:30":"1. Основи інформаційної та кібернетичної безпеки\n8:00-9:20\n<b>Дудикевич В.Б., 208 XIX н.к., Лекція</b>",
                   "10:05":"2. Технології програмування, частина 1\n10:05-11:25\n<b>Совин Я.Р., 208 XIX н.к., Лекція</b>",
                   "11:40":None,
                   "13:15":None,
                   "14:50":None,
                   "16:25":None},

        "Friday": {"8:30":"1. Технології програмування, частина 1\n8:00-9:20\n<b>Побережник В.О., 232 XX н.к., Лабораторна</b>\n\n\n<b>1 ГРУПА</b>",
                   "10:05":"2. Технології програмування, частина 1\n10:05-11:25\n<b>Побережник В.О., 221 XIX н.к., Лабораторна</b>\n\n\n<b>2 ГРУПА</b>",
                   "11:40":"3. Технології програмування, частина 1\n11:40-13:00\n<b>Колбасинський І.В., 211 XIX н.к., Практична</b>",
                   "13:15":None,
                   "14:50":None,
                   "16:25":None}}

@bot.message_handler(commands=["start"])
def start(message):
    menu = telebot.types.InlineKeyboardMarkup()
    if message.chat.id not in remind: menu.add(telebot.types.InlineKeyboardButton("✅Увімкнути авто-нагадування✅", callback_data="enable_reminder"))
    else: menu.add(telebot.types.InlineKeyboardButton("❌Вимкнути авто-нагадування❌", callback_data="disable_reminder"))
    menu.add(telebot.types.InlineKeyboardButton("🔔Розклад на сьогодні🔔", callback_data="today"))
    bot.send_message(message.chat.id, "Ласкаво просимо! Я допоможу тобі з розкладом занять. Обери що тобі потрібно знизу!", reply_markup=menu)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data == "refresh":
        call.data = "today"
        bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text="Оновлення повідомлення відносно реального часу...", parse_mode="HTML")

    elif call.data == "back":
        menu = telebot.types.InlineKeyboardMarkup()
        if call.message.chat.id not in remind: menu.add(telebot.types.InlineKeyboardButton("✅Увімкнути авто-нагадування✅", callback_data="enable_reminder"))
        else: menu.add(telebot.types.InlineKeyboardButton("❌Вимкнути авто-нагадування❌", callback_data="disable_reminder"))
        menu.add(telebot.types.InlineKeyboardButton("🔔Розклад на сьогодні🔔", callback_data="today"))
        bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text="Ласкаво просимо! Я допоможу тобі з розкладом занять. Обери що тобі потрібно знизу!", parse_mode="HTML", reply_markup=menu)

    elif call.data == "enable_reminder":
        if call.from_user.id in remind:
            kb = telebot.types.InlineKeyboardMarkup()
            kb.add(telebot.types.InlineKeyboardButton("Назад 🔙", callback_data="back"))
            bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text="Авто-нагадування вже увімкнено! Ви будете отримувати нагадування за 15 хвилин до початку кожного заняття.", parse_mode="HTML", reply_markup=kb)
            return

        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("Назад 🔙", callback_data="back"))
        remind.append(call.message.chat.id)
        bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text="Авто-нагадування увімкнено! Ви будете отримувати нагадування за 15 хвилин до початку кожного заняття.", parse_mode="HTML", reply_markup=kb)

    elif call.data == "disable_reminder":
        if call.from_user.id not in remind:
            kb = telebot.types.InlineKeyboardMarkup()
            kb.add(telebot.types.InlineKeyboardButton("Назад 🔙", callback_data="back"))
            bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text="Авто-нагадування вже вимкнено! Ви не будете отримувати нагадування про заняття.", parse_mode="HTML", reply_markup=kb)
            return

        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("Назад 🔙", callback_data="back"))
        remind.remove(call.message.chat.id)
        bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text="Авто-нагадування вимкнено! Ви не будете отримувати нагадування про заняття.", parse_mode="HTML", reply_markup=kb)


    if call.data == "today":
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("Оновити 🏫", callback_data="refresh"))
        kb.add(telebot.types.InlineKeyboardButton("Назад 🔙", callback_data="back"))
        now = datetime.now()
        weekday = now.strftime("%A")
        if weekday in days:
            schedule = days[weekday]
            response = f"📅 Розклад на сьогодні:\n\n"
            for time_slot, details in schedule.items():
                if details:
                    response += f"🕒 {time_slot}\n{details}\n\n"
            bot.edit_message_text(message_id=call.message.id ,chat_id=call.message.chat.id, text=response, parse_mode="HTML", reply_markup=kb)
        else:
            bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text="Сьогодні вихідний! Насолоджуйся відпочинком 😊", parse_mode="HTML", reply_markup=kb)


def auto_backup():
    print(f"{Fore.LIGHTYELLOW_EX}[INFO] Auto-backup function started!{Fore.RESET}")
    while True:

        try:
            with open("remind.txt", "w") as file:
                for user_id in remind:
                    file.write(f"{user_id}\n")

        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[ERROR] An error occurred during auto-backup: {e}{Fore.RESET}")

        time.sleep(5)

def reminder(bot):
    print(f"{Fore.LIGHTYELLOW_EX}[INFO] Reminder function started!{Fore.RESET}")

    try:
        while True:
            now = datetime.now()
            weekday = now.strftime("%A")
            current_time = now.strftime("%H:%M")

            if weekday in days:
                for lesson_time, details in days[weekday].items():
                    lesson_dt = datetime.strptime(lesson_time, "%H:%M")
                    reminder_time = (lesson_dt - timedelta(minutes=15)).strftime("%H:%M")

                    if current_time == reminder_time and details:
                        for user_id in remind:
                            try:
                                bot.send_message(
                                    user_id,
                                    f"🔔 Нагадування про заняття:\n\n🕒 {lesson_time} (через 15 хвилин)\n{details}",
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                print(f"{Fore.LIGHTRED_EX}[ERROR] Could not send reminder to user {user_id}: {e}{Fore.RESET}")

                                if "bot was blocked by the user" in str(e):
                                    remind.remove(user_id)
                                    print(f"{Fore.LIGHTYELLOW_EX}[INFO] Removed user {user_id} from reminder list due to block.{Fore.RESET}")

                        time.sleep(60)

    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR] An error occurred in the reminder function: {e}{Fore.RESET}")

def alive():
    app = flask.Flask(__name__)

    @app.route('/')
    def index():
        return "Bot is running!"

    app.run(host='0.0.0.0', port=8080)

print(f"{Fore.LIGHTYELLOW_EX}[INFO] Alive func started!{Fore.RESET}")
Thread(target=alive).start()
print(f"{Fore.LIGHTYELLOW_EX}[INFO] Bot started!{Fore.RESET}")
Thread(target=reminder, args=[bot]).start()
Thread(target=auto_backup).start()
while True:
    try:
        bot.polling(none_stop=True)
    except:
        pass


