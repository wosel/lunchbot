import discord
import datetime
import time
from pubs import *
import json



config = json.load(open('config.json'))
TOKEN = config['token']


client = discord.Client()
last_mess = datetime.datetime.now() - datetime.timedelta(seconds=10)
cache = {}

def all_upper(inp_string):
    return all(x.isupper() for x in inp_string.replace(',', '').replace('.', '').replace(' ', '').replace(':', '').replace(';', ''))

def translate_string(inp_string):
    r = requests.post('https://lindat.mff.cuni.cz/services/translation/api/v2/models/cs-en', {'input_text': inp_string} )
    dec = r.content.decode()
    ev = eval(dec)
    tx = ev[0].strip()
    return tx

def translate_msg(msg_cz):
    msg_split = msg_cz.split('\n')
    msg_en_split = [msg_split[0]]
    for mline in msg_split[1:]:
        l_split = mline.split(' ')
        new_line = []
        first = True
        for word in l_split:
            new_word = word
            if len(word) > 0 and  all_upper(word):
                lowerword = word.lower()
                if first:
                    first = False
                    new_word = lowerword[0].upper() + lowerword[1:]
                else:
                    new_word = lowerword

            new_line.append(new_word)

        fixed_line = ' '.join(new_line)
        translated_line = ''
        if len(fixed_line.strip()) > 0:
            translated_line = translate_string(fixed_line)
        msg_en_split.append(translated_line)

    msg_en = '\n'.join(msg_en_split)
    return msg_en

def write_pub(pub, cache, cur_day, fp, lang='cz'):
    if pub in cache and cache[pub]['day'] == cur_day:
        if lang == 'cz':
            msg_cz = cache[pub]['msg_cz']
            return msg_cz
        if lang == 'en':
            if 'msg_en' in cache[pub]:
                msg_en = cache[pub]['msg_en']
                return msg_en
            else:
                msg_cz = cache[pub]['msg_cz']
                msg_en = translate_msg(msg_cz)
                cache[pub]['msg_en'] = msg_en
                return msg_en
    else:
        msg_cz = fp[pub]()
        cache[pub] = {}
        if lang == 'cz':
            cache[pub]['msg_cz'] = msg_cz
            cache[pub]['day'] = cur_day
            return msg_cz
        if lang == 'en':
            msg_en = translate_msg(msg_cz)
            cache[pub]['msg_cz'] = msg_cz
            cache[pub]['msg_en'] = msg_en
            cache[pub]['day'] = cur_day
            return msg_en

@client.event
async def on_message(message):
    global cache
    global last_mess
    fp = {'klid': klid, 'upecku': upecku, 'peprasul': peprasul, 'naradnici': naradnici}
    cur_day = datetime.datetime.now().day

    # we do not want the bot to reply to itself
    delta = datetime.timedelta(seconds=10)
    if message.author == client.user:
        return
    mt = message.timestamp
    mtm, mts = mt.minute, mt.second
    lim = last_mess + delta
    lm, ls = lim.minute, lim.second

    if (mtm == lm and mts < ls) or mtm < lm:
        print('too soon')
        return
    else:
        print('working on {}'.format(message.content))
    for pub in fp.keys():
        if message.content.startswith('!'+pub):
            msg = write_pub(pub, cache, cur_day, fp, 'cz')
            await client.send_message(message.channel, msg)
            last_mess = datetime.datetime.now()

        elif message.content.startswith('!en_'+pub):
            msg = write_pub(pub, cache, cur_day, fp, 'en')
            await client.send_message(message.channel, msg)
            last_mess = datetime.datetime.now()

    if message.content.startswith('!all'):
        for pub in fp.keys():
            msg = write_pub(pub, cache, cur_day, fp, 'cz')
            await client.send_message(message.channel, msg)
        last_mess = datetime.datetime.now()

    if message.content.startswith('!en_all'):
        for pub in fp.keys():
            msg = write_pub(pub, cache, cur_day, fp, 'en')
            await client.send_message(message.channel, msg)
        last_mess = datetime.datetime.now()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
