import discord
import datetime
import time, sys
from pubs import *
import json
from bs4 import BeautifulSoup
from unidecode import unidecode

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
rib_alert = None

pub2name = {
    'klid': 'Klid',
    'upecku': 'U Pecků',
    'naradnici': 'Na Radnici',
    'peprasul': 'Pepř a sůl',
    'hollar': 'U Hollara',
    'ukocoura': 'U kocoura',
}

pub2emoji = {
    'klid': ':peace:',
    'upecku': ':chestnut:',
    'naradnici': ':house:',
    'ukocoura': ':cat2:',
    'peprasul': '<:peprasul:580322318526709780>'
}

import random

vote_gif_list = [
    'https://tenor.com/view/domo-mascot-elections-vote-gif-5454353',
    'https://tenor.com/view/your-vote-counts-vote-go-vote-encourage-promote-gif-14816222',
    'https://tenor.com/view/fist-matt-huyn-vota-vote-go-vote-gif-12755720',
    'https://tenor.com/view/vote-cat-pusheen-excited-bounce-gif-7398664',
    'https://tenor.com/view/time-to-vote-go-vote-vote-gif-12835582',
    'https://tenor.com/view/vote-primary-day-voting-ballot-gif-12451002',
    'https://tenor.com/view/vote-go-vote-dark-knight-joker-heath-ledger-gif-5111826',
    'https://tenor.com/view/vote-obama-yourvotematters-gif-5111894',
    'https://tenor.com/view/vote-ready-election-america-usa-gif-12664504',
    'https://tenor.com/view/vote-jimcarrey-type-computer-voting-gif-5111579'
]

def get_all_emoji():
    gif_idx = random.randint(1, len(vote_gif_list))
    all_emoji = 'Vote below: '
    all_emoji += ' '.join(list(pub2emoji.values()) + ['<:phoenix:578278816435273728>'] + [':man_with_turban::skin-tone-4:'])
    all_emoji += '{}\n'.format(vote_gif_list[gif_idx-1])
    return all_emoji




def all_upper(inp_string):
    return all(x.isupper() for x in inp_string.replace(',', '').replace('.', '').replace(' ', '').replace(':', '').replace(';', ''))

def translate_string(inp_string):
    r = requests.post('https://lindat.mff.cuni.cz/services/translation/api/v2/models/cs-en', {'input_text': inp_string} )
    dec = r.content.decode()
    #print(dec)
    #ev = eval(dec)
    #tx = dec.strip()
    tx = dec.strip()
    return tx

def translate_msg(msg_cz):
    msg_split = msg_cz.split('\n')
    msg_en_split = []
    for mline in msg_split:
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
    global rib_alert

    try:

        pre_string = '[{}] {}\n'.format(pub2name[pub].upper(), pub2emoji[pub])
        if pub in cache and cache[pub]['day'] == cur_day:
            msg_cz = cache[pub]['msg_cz']
            if 'žebra' in msg_cz.lower() or 'žebírka' in msg_cz.lower() or 'žebro' in msg_cz.lower() or 'žebírko' in msg_cz.lower():
                rib_alert = pub
            if lang == 'cz':
                return pre_string + msg_cz
            if lang == 'en':
                if 'msg_en' in cache[pub]:
                    msg_en = cache[pub]['msg_en']
                    return pre_string + msg_en
                else:
                    msg_cz = cache[pub]['msg_cz']
                    msg_en = translate_msg(msg_cz)
                    cache[pub]['msg_en'] = msg_en
                    return pre_string + msg_en
        else:
            msg_cz = fp[pub]()
            if 'žebra' in msg_cz.lower() or 'žebírka' in msg_cz.lower() or 'žebro' in msg_cz.lower() or 'žebírko' in msg_cz.lower():
                rib_alert = pub
            cache[pub] = {}
            if lang == 'cz':
                cache[pub]['msg_cz'] = msg_cz
                cache[pub]['day'] = cur_day
                return pre_string + msg_cz
            if lang == 'en':
                msg_en = translate_msg(msg_cz)
                cache[pub]['msg_cz'] = msg_cz
                cache[pub]['msg_en'] = msg_en
                cache[pub]['day'] = cur_day
                return pre_string + msg_en
    except Exception as e:
        print(e)
        return 'error in {}'.format(pub)
        #return 'error in {}: {}'.format(pub, e)
        

warned = False
def hollar():

    response = requests.get('http://www.restauraceuhollara.cz/')
    soup = BeautifulSoup(response.content, 'lxml')
    retstr = ''
    for header in soup.find_all('h3'):
        htext = header.get_text().strip()
        if htext.startswith('MENU') or htext.startswith('Hotovky') or htext.startswith('Poledn'):
            for elem in header.next_siblings:
                if elem.name and elem.name.startswith('table'):
                    tds = elem.find_all('td')
                    for td in tds:
                        try:
                            txt = td.get_text().strip().replace('\n', ' ')
                
                        except:
                            continue
                        retstr += txt + '\n'
                    break
    return retstr 

def hollar_ribs():
    hollar_menu = hollar()
        
    if 'žebra' in hollar_menu.lower() or 'žebírka' in hollar_menu.lower() or 'žebro' in hollar_menu.lower() or 'žebírko' in hollar_menu.lower():
        return True
    else:
        return False
        

@client.event
async def on_message(message):
    global cache
    global last_mess
    global warned
    global rib_alert
    rib_alert = None
    fp = {'klid': klid, 'upecku': upecku, 'peprasul': peprasul, 'naradnici': naradnici, 'ukocoura': ukocoura}
    cur_day = datetime.datetime.now().day

    # we do not want the bot to reply to itself
    delta = datetime.timedelta(seconds=10)
    if message.author == client.user:
        return
    if not message.content.startswith('!'):
        return

    
    mt = datetime.datetime.utcnow()

    if (mt < last_mess + delta) and message.content.startswith('!'):
        if not warned:
            await message.channel.send("You're doing that too often. Try again in 10 seconds")
            await message.channel.send("To list all available menus, use !all (or !en_all for English)")
            warned = True
        print('too soon')
        return
    else:
        warned = False
        print('working on {}'.format(message.content))
    for pub in fp.keys():
        if message.content.startswith('!'+pub):
            msg = write_pub(pub, cache, cur_day, fp, 'cz')
            while len(msg) >= 2000:
                msg_a = msg[:1800]
                msg_b = msg[1800:]
                await message.channel.send(msg_a)
                msg = msg_b
            await message.channel.send(msg)
            last_mess = datetime.datetime.utcnow()

        elif message.content.startswith('!en_'+pub):
            msg = write_pub(pub, cache, cur_day, fp, 'en')
            while len(msg) >= 2000:
                msg_a = msg[:1800]
                msg_b = msg[1800:]
                await message.channel.send(msg_a)
                msg = msg_b
            await message.channel.send(msg)
            last_mess = datetime.datetime.utcnow()

    if message.content.startswith('!all'):
        rib_list = []
        for pub in fp.keys():
            rib_alert = None
            msg = write_pub(pub, cache, cur_day, fp, 'cz')
            if rib_alert is not None:
                rib_list.append(rib_alert)
            if msg.strip() != '':
                while len(msg) >= 2000:
                    msg_a = msg[:1800]
                    msg_b = msg[1800:]
                    await message.channel.send(msg_a)
                    msg = msg_b
                await message.channel.send(msg)
        try:
            if hollar_ribs():
                rib_list.append('hollar')
        except:
            print('hollar error')
        if len(rib_list) > 0:
            m = 'POZOR!!!! Nalezena žebra: {}'.format(','.join([pub2name[x] for x in rib_list]))
            await message.channel.send('```css\n[{}]\n```'.format(m))
        #await client.send_message(message.channel, ':peace: :chestnut: <:peprasul:580322318526709780> :house: <:phoenix:578278816435273728> :man_with_turban::skin-tone-4:')
        await message.channel.send(get_all_emoji())
        last_mess = datetime.datetime.utcnow()
    
    if message.content.startswith('!en_all'):
        rib_list = []
        for pub in fp.keys():
            rib_alert = None
            msg = write_pub(pub, cache, cur_day, fp, 'en')
            if rib_alert is not None:
                rib_list.append(rib_alert)
            await message.channel.send(msg)
        try:
            if hollar_ribs():
                rib_list.append('hollar')
        except:
            print('hollar error')
        if len(rib_list) > 0:
            m = 'ALERT!!! Ribs found: {}'.format(','.join([pub2name[x] for x in rib_list]))
            await message.channel.send('```css\n[{}]\n```'.format(m))
        await message.channel.send(get_all_emoji())
        last_mess = datetime.datetime.utcnow()
    
    if message.content.startswith('!both_all'):
        rib_list = []
        for pub in fp.keys():
            rib_alert = None
            msg_both  = ''
            msg_cz = write_pub(pub, cache, cur_day, fp, 'cz')
            if rib_alert is not None:
                rib_list.append(rib_alert)
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
                if len(m.strip()) > 0:
                    await message.channel.send(m)

        try:
            if hollar_ribs():
                rib_list.append('hollar')
        except:
            print('hollar error')
        if len(rib_list) > 0:
            m = 'POZOR!!!! Nalezena žebra: {}'.format(','.join([pub2name[x] for x in rib_list]))
            await message.channel.send('```css\n[{}]\n```'.format(m))
            m = 'ALERT!!! Ribs found: {}'.format(','.join([pub2name[x] for x in rib_list]))
            await message.channel.send('```css\n[{}]\n```'.format(m))
        await message.channel.send(get_all_emoji())
        last_mess = datetime.datetime.utcnow()
    
    if message.content.startswith('!clear'):
        cache = {}
        await message.channel.send("Cache cleared")



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.close()
client.logout()
client.run(TOKEN)
client.close()
client.logout()
