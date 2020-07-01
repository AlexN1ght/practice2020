import requests
from pydub import AudioSegment
import telebot
from telebot import apihelper
import numpy as np
import aubio
import re 
import math as m




BASE_NOTE = 440 / ((2**(1/12))**48)

def note_to_n(n, octave):
    if n == 'A':
        in_oc = 12
    elif n == 'A#' or n == 'Bb':
        in_oc = 13
    elif n == 'B':
        in_oc = 14
    elif n == 'C':
        in_oc = 3
    elif n == 'C#' or n == 'Db':
        in_oc = 4
    elif n == 'D':
        in_oc = 5
    elif n == 'D#' or n == 'Eb':
        in_oc = 6
    elif n == 'E':
        in_oc = 7
    elif n == 'F':
        in_oc = 8
    elif n == 'F#' or n == 'Gb':
        in_oc = 9
    elif n == 'G':
        in_oc = 10
    elif n == 'G#' or n == 'Ab':
        in_oc = 11
    else:
        return 0
    return BASE_NOTE * ((2**(1/12))**(in_oc + 12 * (octave)))


def oct_note(n):
    if n == 0:
        return 'A'
    elif n == 1:
        return 'A#'
    elif n == 2:
        return 'B'
    elif n == 3:
        return 'C'
    elif n == 4:
        return 'C#'
    elif n == 5:
        return 'D'
    elif n == 6:
        return 'D#'
    elif n == 7:
        return 'E'
    elif n == 8:
        return 'F'
    elif n == 9:
        return 'F#'
    elif n == 10:
        return 'G'
    elif n == 11:
        return 'G#'

def n_of_note(freq):
    return m.ceil(12 * m.log2(freq / BASE_NOTE) - 0.5)
def n_to_note(n):
    return oct_note(n % 12) + str((n + 9) // 12 - 1)

def median(lst): 
    quotient, remainder = divmod(len(lst), 2) 
    if remainder: 
        return sorted(lst)[quotient]
    return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.

def offset(freq, note):
    ideale_freq = BASE_NOTE * ((2**(1/12))**note)
    if abs(freq - ideale_freq) < ((ideale_freq * (2**(1/12))) - ideale_freq) * 0.1:
        return 'OK'
    elif freq - ideale_freq < 0 :
        return '-' + str(abs(m.floor(freq - ideale_freq)))
    else:
        return '+' + str(abs(m.floor(freq - ideale_freq)))


def help():
    res = "\t-I can tune your instument, just play me via voice message\n"
    res += "\t-Tell of a different tunes, simply type your instrument\n"
    res += "\t-Convert frequency to note and vice versa, just type some!\n"
    return res




ip = 'grsst.s5.opennetwork.cc'
port = '999'
usrP = '214931371'
passP = 'mnPO7xTd'

proxy = {'https': 'socks5h://{}:{}@{}:{}'.format(usrP, passP, ip,port)}
apihelper.proxy = proxy

TOKEN = '857334744:AAEVh3Rvfbvdfbdfxb3pZH54n81cI'
#not an actual token

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    res = "Hello and welcome. If you are a musician your on the right way!\n"
    res += help()
    bot.send_message(message.chat.id, res)
@bot.message_handler(commands=['help'])
def send_help(message):
    res = help()
    bot.send_message(message.chat.id, res)

@bot.message_handler(content_types=['voice'])
def analyse_audio(message):
    audio_path = bot.get_file(message.voice.file_id).file_path
    request = requests.get('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, audio_path), proxies=proxy)
    
    my_file = open("UsersAudio/test.ogg", "wb")
    my_file.write(request.content)

    ogg_version = AudioSegment.from_ogg("UsersAudio/test.ogg")
    ogg_version.export("UsersAudio/test.wav", format="wav")

    src = aubio.source('UsersAudio/test.wav', hop_size=2048)

    pDetection = aubio.pitch("yin", 2048, 2048, src.samplerate)
    pDetection.set_unit("Hz")
    pDetection.set_silence(-60)

    buf_count = 0
    buf_freak = [ 0 for i in range(5)]
    all_sl = []
    res = ''

    while True:
        samples, read = src()
        buf_freak[buf_count] = (pDetection(samples)[0])

        if buf_count == 4:
            all_sl.append(median(buf_freak))
            buf_count = 0
        else:
            buf_count += 1

        if read < src.hop_size:
            break


    curr_count = 0
    curr_f = 0
    for slise in all_sl:
        print(slise)
        if abs(curr_f - slise) < (curr_f * (2**(1/12)) - curr_f):
            if curr_count == 0:
                curr_f = slise
            else:
                curr_f = (curr_f + slise) / 2
            curr_count += 1
        elif curr_count > 4:
            n = n_of_note(curr_f)
            note = n_to_note(n)
            res += note + ': ' + offset(curr_f, n) + '\n'

            curr_count = 0
            curr_f = slise
        else:
            curr_count = 0
            curr_f = slise

    if curr_count > 4:
        n = n_of_note(curr_f)
        note = n_to_note(n)
        res += note + ': ' + offset(curr_f, n) + '\n'

    if res == '':
        answer = "I can't quite hear you."
    else:
        answer = "You playd:\n" + res

    #print(total_read)
    bot.reply_to(message, answer)

@bot.message_handler(regexp=r'^Guitar$')
def guitar_tune(message):
    res = "Here's the standart tune for a guitar:\n"
    res += "1-E3 2-B2 3-G2\n4-D2 5-A1 6-E1\n"
    bot.reply_to(message, res)

@bot.message_handler(regexp=r'^Piano$')
def piano_tune(message):
    res = "There's no other tune for piano.\nBut here's the tip: you can start your tuning from A3:\n"
    bot.reply_to(message, res)

@bot.message_handler(regexp=r'^\d+(\.)?\d* ?(Hz|HZ|hz)?$')
def freq_to_note(message):
    freq = float(re.search(r'^\d+(\.)?\d*', message.text)[0])
    n = n_of_note(freq)
    note = n_to_note(n)
    off = offset(freq, n)
    if off == 'OK':
        off = ''
    else:
        off += " Hz"
    res = note + ' ' + off + '\n'
    bot.reply_to(message, res)

@bot.message_handler(regexp=r'^[ABCDEFG][#b]?\d$')
def note_to_freq(message):
    note = re.search(r'[ABCDEFG][#b]?', message.text)
    octave = re.search(r'\d$', message.text)
    if (not note) or (not octave):
        bot.reply_to(message, "Write in capitale!")
        return
    n = note_to_n(note[0], int(octave[0]))
    answer = str(m.floor(n)) + " Hz"
    bot.reply_to(message, answer)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, "I can't undestend you... Мяу:3")

bot.polling()
