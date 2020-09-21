from time import sleep
import telepotpro
from telepotpro import Bot, glance
from telepotpro.exception import TelegramError, BotWasBlockedError
from telepotpro.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
from threading import Thread
from datetime import datetime, timedelta
from json import load as jsload
from os.path import abspath, dirname, join
import requests
import lxml.html



with open(join(dirname(abspath(__file__)), "settings.json")) as settings_file:
    js_settings = jsload(settings_file)

bot = Bot(js_settings["key"])
maintenance = js_settings["maintenance"]

jump = 0
fullDate = ""

xpaths = {
    "nomeSanto":    '//*[@id="CenterDiv"]/div[2]/div[1]/div[1]',
    "tipoSanto":    '//*[@id="CenterDiv"]/div[2]/div[1]/div[2]',
    "imgSanto":     '//*[@id="CenterDiv"]/div[2]/img'
}

if not maintenance:
    print("Bot Started Successfully")
else:
    print("WARNING! You started the bot is in maintenance mode, change this setting in settings.json")

html = requests.get('https://www.santodelgiorno.it/')
doc = lxml.html.fromstring(html.content)

def reply(msg):
    santo = ["nome","tipo","img"]
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    global maintenance
    global html
    global doc

    try:
        text = msg['text']
    except ValueError:
        text = ""
    
    command = getCommand(text)

    if not maintenance:
        if command == "/dona":
            bot.sendMessage(chatId, "Ecco qui il mio link PayPal, Grazie mille! \n"
                                    "https://www.paypal.me/wapeetyofficial")

        elif command == "/start":
            bot.sendMessage(chatId, "Benvenuto \n"
                                    "Prima di iniziare ci tengo a dire che questo bot <b>NON</b> manda le notifiche in automatico, \n"
                                    "dovrai essere tu a richiedere il santo del giorno tramite: \n\n" 
                                    "<code>/santo</code>\n\n"
                                    "Se invece vuoi specificare un giorno basterá aggiungere la data in formato: \n\n" 
                                    "<code>gg/mm</code>\n\n"
                                    "avendo cura di anteporre uno zero per i mesi e i giorni con una sola cifra, ad esempio:\n\n"
                                    "<code>02/01</code>", parse_mode="HTML")
        
        elif command == "/santo":

            if(len(text) > len(command)):
                data = text[len(command)+1:]

                giorno = Truncate(data, 0)
                mese = Truncate(data, 1)
                print(giorno + "/" + mese)

                html = requests.get('https://www.santodelgiorno.it/' + giorno + "/" + mese)
                doc = lxml.html.fromstring(html.content)
            else:
                html = requests.get('https://www.santodelgiorno.it/')
                doc = lxml.html.fromstring(html.content)

            santo[0] = getNomeSanto()
            santo[1] = getTipoSanto()
            santo[2] = getImgSanto()
            bot.sendMessage(chatId, "<b>" + santo[0] + ":</b> \n <i>" + santo[1] + "</i>\n\n" + "<a href='" + santo[2] + "'> link alla foto </a>", parse_mode="HTML")

        else:
            bot.sendMessage(chatId, "Comando non riconosciuto")
    else:
        bot.sendMessage(chatId, "<b>Bot Attualmente in manutenzione.</b> \n"
                                "<i>Ci scusiamo per il disagio.</i>", parse_mode="HTML")

def getNomeSanto():
    nomeSanto =  doc.xpath(xpaths['nomeSanto'])[0]
    return nomeSanto.text_content()

def getTipoSanto():
    tipoSanto =  doc.xpath(xpaths['tipoSanto'])[0]
    return tipoSanto.text_content()

def getImgSanto():
    pathSanto =  doc.xpath(xpaths['imgSanto'])[0]
    return "https://www.santodelgiorno.it" + pathSanto.attrib['src']

def Truncate(content, sel):
    if sel == 0:
        output = content[0:2]
        if(content[3:] == "02" and int(output) <= 29):
            return output
        elif(content[3:] == "01" or content[3:] == "03" or content[3:] == "05" or content[3:] == "07" or content[3:] == "08" or content[3:] == "10" or content[3:] == "12" and int(output) <= 31):
            return output
        elif(content[3:] == "04" or content[3:] == "06" or content[3:] == "09" or content[3:] == "11" and int(output) <= 30):
            return output
        else:
            return "01"
    else:
        code = content[3:]
        print(code)
        if code == "01":
            output = "gennaio"
        elif code == "02":
            output = "febbraio"
        elif code == "03":
            output = "marzo"
        elif code == "04":
            output = "aprile"
        elif code == "05":
            output = "maggio"
        elif code == "06":
            output = "giugno"
        elif code == "07":
            output = "luglio"
        elif code == "08":
            output = "agosto"
        elif code == "09":
            output = "settembre"
        elif code == "10":
            output = "ottobre"
        elif code == "11":
            output = "novembre"
        elif code == "12":
            output = "dicembre"
        else:
            output = "gennaio"        
        return output

def getCommand(content):
    t=0
    output = ""
    for i in content:
        if i != " " and t == 0:
            output += i
        else:
            t = 1
        
    return output

def on_inline_query(msg):
    query_id, from_id, query_string = telepotpro.glance(msg, flavor='inline_query')
    print ('Inline Query:', query_id, from_id, query_string)

    global html
    global doc

    if(len(query_string) ==  5):
        giorno = Truncate(query_string, 0)
        mese = Truncate(query_string, 1)
        print(giorno + "/" + mese)

        html = requests.get('https://www.santodelgiorno.it/' + giorno + "/" + mese)
        doc = lxml.html.fromstring(html.content)

        articles = [InlineQueryResultArticle(
                        id='Santo del giorno',
                        title= getNomeSanto(),
                        description= getTipoSanto(),
                        thumb_url= getImgSanto(),
                        input_message_content=InputTextMessageContent(
                            message_text="<b>" + getNomeSanto() + "</b> \n <i>" + getTipoSanto() + "</i>\n\n" + "<a href='" + getImgSanto() + "'> link alla foto </a>",
                            parse_mode="HTML"
                        )
                    )]

    else:    
        html = requests.get('https://www.santodelgiorno.it/')
        doc = lxml.html.fromstring(html.content)

        articles = [InlineQueryResultArticle(
                        id='Santo del giorno',
                        title= getNomeSanto(),
                        description= getTipoSanto(),
                        thumb_url= getImgSanto(),
                        input_message_content=InputTextMessageContent(
                            message_text="<b>" + getNomeSanto() + "</b> \n <i>" + getTipoSanto() + "</i>\n\n" + "<a href='" + getImgSanto() + "'> link alla foto </a>",
                            parse_mode="HTML"
                        )
                    )]

    bot.answerInlineQuery(query_id, articles)

bot.message_loop({'chat': reply, 'inline_query': on_inline_query})
while True:
    sleep(60)