import telebot
import requests
from enum import Enum
from face_rec import find_faces, public_bd_add, bd_init


class Status(Enum):
	FREE = 0
	ADD_PHOTO = 1
	ADD_NAME = 2

TOKEN = '1089518853:AAEEs1i735_N89TCtkMRwinA_kz3yKd8Ykg'
#not an actual token


bot = telebot.TeleBot(TOKEN)

user_stat = {}
bd_init()

def check_usr(message):
	if not user_stat.get(message.from_user.id):
		user_stat[message.from_user.id] = [Status.FREE,0,0]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	check_usr(message)
	user_stat[message.from_user.id] = [Status.FREE,0,0]
	bot.reply_to(message, "Welcome to open fasedetection bot. You can add new fases in the libruary by entering /add command and detect faces by just sending photo with some faces. You can also type /annalize to do so")

@bot.message_handler(commands=['analize'])
def handle_analize(message):
	check_usr(message)
	user_stat[message.from_user.id] = [Status.FREE,0,0]
	bot.reply_to(message, "Send photo to analize or add new")
	
@bot.message_handler(commands=['add'])
def handle_add(message):
	check_usr(message)
	bot.send_message(message.chat.id, "Send us a photo of the person you wanna add")
	user_stat[message.from_user.id][0] = Status.ADD_PHOTO

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
	check_usr(message)
	if user_stat[message.from_user.id][0] == Status.ADD_PHOTO:
		photo_path = bot.get_file(message.photo[1].file_id).file_path
		request = requests.get('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, photo_path))
		user_stat[message.from_user.id][1] = request.content
		bot.reply_to(message, "Enter this person's name")
		user_stat[message.from_user.id][0] = Status.ADD_NAME
	elif user_stat[message.from_user.id][0] == Status.FREE:
		photo_path = bot.get_file(message.photo[1].file_id).file_path
		request = requests.get('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, photo_path))
		adding_photo = open("tmp.jpg", "wb")
		adding_photo.write(request.content)

		bot.send_message(message.chat.id, "Processing")
		name_list = find_faces("tmp.jpg")
		out_str = ""
		for name in name_list:
			out_str = out_str + name + '\n'
		if out_str == "":
			out_str = "Could not find known faces"
		else :
			out_str = "Found persons:\n" + out_str
		bot.reply_to(message, out_str)
	else:
		bot.reply_to(message, "You'r doing something wrong")


@bot.message_handler(content_types=['text'])
def handle_text(message):
	check_usr(message)
	if user_stat[message.from_user.id][0] == Status.ADD_NAME:
		user_stat[message.from_user.id][2] = message.text
		print(user_stat[message.from_user.id][2])
		#debugging photos
		adding_photo = open("tmp.jpg", "wb")
		adding_photo.write(user_stat[message.from_user.id][1])
		
		if public_bd_add("tmp.jpg", user_stat[message.from_user.id][2]):
			bot.reply_to(message, "Person successfully added")
		else:
			bot.reply_to(message, "Something went wrong. No faces found")
		user_stat[message.from_user.id][0] = Status.FREE
	else:
		bot.reply_to(message, "You'r doing something wrong")

bot.polling()
