import discord
import datetime
import time, sys
from pubs import *
import json

try:
    config_fname = sys.argv[1]
    config = json.load(open(config_fname))
    print('config loaded from {}'.format(config_fname))
except:
    config = json.load(open('config.json'))
    print('default "config.json" loaded')
TOKEN = config['token']


client = discord.Client()
last_mess = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
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

    try:

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
    except:
        return 'error in {}'.format(pub)

warned = False

@client.event
async def on_message(message):
    global cache
    global last_mess
    global warned
    fp = {'klid': klid, 'upecku': upecku, 'peprasul': peprasul, 'naradnici': naradnici}
    cur_day = datetime.datetime.now().day

    # we do not want the bot to reply to itself
    delta = datetime.timedelta(seconds=10)
    if message.author == client.user:
        return
    if not message.content.startswith('!'):
        return

    mt = message.timestamp
    


    if (mt < last_mess + delta) and message.content.startswith('!'):
        if not warned:
            await client.send_message(message.channel, "You're doing that too often. Try again in 10 seconds")
            await client.send_message(message.channel, "To list all available menus, use !all (or !en_all for English)")
            warned = True
        print('too soon')
        return
    else:
        warned = False
        print('working on {}'.format(message.content))
    for pub in fp.keys():
        if message.content.startswith('!'+pub):
            msg = write_pub(pub, cache, cur_day, fp, 'cz')
            await client.send_message(message.channel, msg)
            last_mess = datetime.datetime.utcnow()

        elif message.content.startswith('!en_'+pub):
            msg = write_pub(pub, cache, cur_day, fp, 'en')
            await client.send_message(message.channel, msg)
            last_mess = datetime.datetime.utcnow()

    if message.content.startswith('!all'):
        for pub in fp.keys():
            msg = write_pub(pub, cache, cur_day, fp, 'cz')
            await client.send_message(message.channel, msg)
        await client.send_message(message.channel, ':peace: :chestnut: <:peprasul:580322318526709780> :house: <:phoenix:578278816435273728> :man_with_turban::skin-tone-4:')
        last_mess = datetime.datetime.utcnow()
    

    if message.content.startswith('!en_all'):
        for pub in fp.keys():
            msg = write_pub(pub, cache, cur_day, fp, 'en')
            await client.send_message(message.channel, msg)
        await client.send_message(message.channel, ':peace: :chestnut: <:peprasul:580322318526709780> :house: <:phoenix:578278816435273728> :man_with_turban::skin-tone-4:')
        last_mess = datetime.datetime.utcnow()
    
    if message.content.startswith('!both_all'):
        for pub in fp.keys():
            msg_both  = ''
            msg_cz = write_pub(pub, cache, cur_day, fp, 'cz')
            msg_en = write_pub(pub, cache, cur_day, fp, 'en')
            msgs = []
            for cz, en in zip(msg_cz.split('\n'), msg_en.split('\n')):
                if cz == '' or en == '':
                    continue 
                msg_both += '{}\n_{}_\n'.format(cz, en)
                if len(msg_both) > 1500:
                    msgs.append(msg_both)
                    msg_both = ''
            msgs.append(msg_both)
            for m in msgs:
                await client.send_message(message.channel, m)
        await client.send_message(message.channel, ':peace: :chestnut: <:peprasul:580322318526709780> :house: <:phoenix:578278816435273728> :man_with_turban::skin-tone-4:')
        last_mess = datetime.datetime.utcnow()
    
    if message.content.startswith('!clear'):
        cache = {}
        await client.send_message(message.channel, "Cache cleared")



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
