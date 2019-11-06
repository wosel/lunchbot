import requests
from bs4 import BeautifulSoup
import datetime
from unidecode import unidecode


def klid():

    response = requests.get('http://www.klidpopraci.cz/tydenni-menu/')

    soup = BeautifulSoup(response.content, 'lxml')
    #retstr = '[KLID]\n'
    retstr = ''
    day_ctr = 0
    today = datetime.datetime.today().weekday()
    for header in soup.find_all('h2'):
        htext = header.get_text().strip()
        if htext == '':
            continue
        htext_filtered = ''.join([x for x  in unidecode(htext.lower()) if x.isalnum()])
        if htext_filtered not in ['pondeli', 'utery', 'streda', 'ctvrtek', 'patek']:
            continue 
            
        if today != day_ctr:
            day_ctr += 1
            continue
        last_txt = ''
        for elem in header.next_siblings:
            try:
                txt = elem.get_text().strip().replace('\n', ' ')
            except:
                continue
            if elem.name and elem.name.startswith('h') and txt != '':
                break
            if elem.name == 'p' and txt != '':
                if (txt[0] != txt.lower()[0] or txt[0] in '0123456789')  and last_txt != '':
                    retstr += last_txt + '\n'
                    last_txt = txt
                else:
                    last_txt = last_txt +' '+ txt

            if elem.name == 'div':
                for el in elem.findChildren('p'):
                    eltxt = el.get_text().strip().replace('\n', ' ')
                    if eltxt != '':
                        if (eltxt[0] != eltxt.lower()[0] or eltxt[0] in '0123456789') and last_txt != '':
                            retstr += last_txt + '\n'
                            last_txt = eltxt
                        else:
                            last_txt = last_txt +' '+ eltxt

        retstr += last_txt + '\n'
        break
    return retstr

def peprasul():
    response = requests.get('https://peprasul.cz/poledni-menu/')
    soup = BeautifulSoup(response.content, 'lxml')


    body = soup.find_all('body')[0]

    mark = False
    divcl = ''
    for s in body.findChildren():
        if mark:
            if s.name == 'div':
                cl=s['class']
                cl0 = cl[0]
                if cl0.startswith('cz_') and cl0[3] in '0123456789':
                    divcl = cl0
                    break
        if s.get_text().strip().startswith('HLAV'):

            mark = True
    menudiv = soup.find_all('div', divcl)
    #retstr = '[PEPŘ A SŮL]\n'
    retstr = ''
    foodlist = []
    pricelist = []
    for food in menudiv[0].findChildren('span'):

        el = food.findChildren('b')
        if len(el) > 0:
            tx = el[0].get_text().strip()
            if unidecode(tx.lower()).startswith('kolac z domaci'):
                break
            foodlist.append(tx)
        if food.has_attr('class'):
            if food['class'][0] == 'cz_wh_right':
                tx = food.get_text().strip().replace(' Kč', '')
                pricelist.append(tx)
       
    for f, p in zip(foodlist, pricelist):
        retstr += f + ' ' + p + '\n'
    return retstr

def upecku():

    response = requests.get('http://upecku.cz/menu/')
    soup = BeautifulSoup(response.content, 'lxml')

    #retstr = '[U PECKŮ]\n'
    retstr = ''
    daily = soup.findAll('div', {'id': 'tabs-1'})

    for menuitem in daily[0].findChildren('div', {'class': 'menu-item'}):
        for span in menuitem.findChildren('span'):

            txt = span.get_text().strip()
            if len(txt) > 4:
                retstr += txt
        for div in menuitem.findChildren('div'):
            txt = div.get_text().strip().replace('Kč', '')
            retstr += ' ' + txt + ',-\n'
    return retstr

def naradnici():
    response = requests.get('http://www.hospudkanaradnici.cz/new2016-2/index.php/menu/denni-menu')
    soup = BeautifulSoup(response.content, 'lxml')

    #retstr = '[NA RADNICI]\n'
    retstr = ''
    iframe = soup.find_all('iframe')[0]
    response = requests.get(iframe.attrs['src'])
    iframe_soup = BeautifulSoup(response.content, 'lxml')
    cont_div = iframe_soup.findAll('div', {'id': 'contents'})[0]
    last = ''
    for p in cont_div.findChildren('p'):
        txt = p.get_text().strip().replace('.', '').replace('…', ' ')
        txt = ' '.join(txt.split())
        if txt == 'MOUČNÍKY':
            break
        if len(txt) < 1 or txt == 'POLÉVKY' or txt == 'NABÍDKA DNE':
            continue
        if txt[0].lower() == txt[0] and txt[0] != '¼' :
            last += ' ' + txt
        else:
            retstr += last + '\n'
            last = txt
    retstr += last
    return retstr




