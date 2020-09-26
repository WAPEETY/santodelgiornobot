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
import secret


with open(join(dirname(abspath(__file__)), "settings.json")) as settings_file:
    js_settings = jsload(settings_file)

bot = Bot(js_settings["key"])
maintenance = js_settings["maintenance"]

jump = 0
fullDate = ""

xpaths = {
    "nomeSanto":    '//*[@id="CenterDiv"]/div[2]/div[1]/div[1]',
    "tipoSanto":    '//*[@id="CenterDiv"]/div[2]/div[1]/div[2]',
    "imgSanto":     '//*[@id="CenterDiv"]/div[2]/img',
    "linkSanto":    '//*[@id="CenterDiv"]/div[2]/div[1]/div[3]/div/a',
    "ricorrenza":   '//*[@id="CenterDiv"]/div[2]/div[4]/b/a',
    "tipoFesta":    '//*[@id="CenterDiv"]/div[2]/div[5]/b',
    "protetti":     '//*[@id="CenterDiv"]/div[2]/div[6]/span[2]'
}

if not maintenance:
    print("Bot Started Successfully")
else:
    print("WARNING! You started the bot is in maintenance mode, change this setting in settings.json")

html = requests.get('https://www.santodelgiorno.it/')
doc = lxml.html.fromstring(html.content)

def reply(msg):
    santo = ["nome","tipo","img","link","ricorrenza","tipoFesta","protetti"]
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    global maintenance
    global html
    global doc
    global secret

    try:
        text = msg['text']
    except ValueError:
        text = ""
    
    command = getCommand(text).lower()

    if not maintenance:
        if command == "/dona":
            bot.sendMessage(chatId, "Ecco qui il mio link PayPal, Grazie mille! ❤️\n"
                                    "https://www.paypal.me/wapeetyofficial")
            bot.sendVideo(chatId, open('img/jesoo.mp4', 'rb'))
        
        elif command == secret.getSecretCommand():
            bot.sendMessage(chatId, secret.getSecretMessage(), parse_mode="HTML")
            print("Comando Segreto Attivato")

        elif command == "/source":
            bot.sendMessage(chatId, "Ecco qui il link Github, Aggiungi una stellina! 😘\n"
                                    "https://github.com/WAPEETY/santodelgiornobot")

        elif command == "/start":
            bot.sendMessage(chatId, "Benvenuto ❗️\n"
                                    "Prima di iniziare ci tengo a dire che questo bot <b>NON</b> manda le notifiche in automatico, \n"
                                    "dovrai essere tu a richiedere il santo del giorno tramite: \n\n" 
                                    "/santo\n\n"
                                    "Se invece vuoi specificare un giorno basterá aggiungere la data in formato: \n\n" 
                                    "<code>gg/mm</code>\n\n"
                                    "avendo cura di anteporre uno zero per i mesi e i giorni con una sola cifra, ad esempio:\n\n"
                                    "<code>02/01</code>\n\n"
                                    "✨ <b>Novita!</b> ✨\n"
                                    "<i>Sapevi che questo bot funziona anche inline?</i> 😍\n\n"
                                    "Vai in una qualsiasi chat e scrivi @wap_sdgbot con la data e scopri la sorpresa 🤩", parse_mode="HTML")
        
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
            santo[3] = getLinkSanto()
            santo[4] = getRicorrenza(santo[3])
            santo[5] = getTipologia(santo[3])
            santo[6] = getProtetti(santo[3])

            bot.sendMessage(chatId, "<b>" + santo[0] + ":</b> \n <i>" + santo[1] + "</i>\n\n" + "<b>Ricorrenza:</b> " + " <i>" + santo[4] + "</i>\n" + "<b>Tipo Festa:</b> " + " <i>" + santo[5] + "</i>\n" + "<b>Protetti:</b> " + " <i>" + santo[6] + "</i>\n" + "\n\n" + "<a href='" + santo[2] + "'> link alla foto </a>", parse_mode="HTML")

        else:
            bot.sendMessage(chatId, "Comando non riconosciuto ☹️")
    else:
        bot.sendMessage(chatId, "⚠️ <b>Bot Attualmente in manutenzione.</b> ⚠️\n"
                                "<i>Ci scusiamo per il disagio.</i>", parse_mode="HTML")

def getNomeSanto():
    nomeSanto =  doc.xpath(xpaths['nomeSanto'])[0]
    return nomeSanto.text_content()

def getTipoSanto():
    tipoSanto =  doc.xpath(xpaths['tipoSanto'])[0]
    return tipoSanto.text_content()

def getImgSanto():
    pathimgSanto =  doc.xpath(xpaths['imgSanto'])[0]
    return "https://www.santodelgiorno.it" + pathimgSanto.attrib['src']

def getLinkSanto():
    linkSanto =  doc.xpath(xpaths['linkSanto'])[0]
    return "https://www.santodelgiorno.it" + linkSanto.attrib['href']

def getRicorrenza(linkSanto):
    html = requests.get(linkSanto)
    doc = lxml.html.fromstring(html.content)
    ricorrenza =  doc.xpath(xpaths['ricorrenza'])[0]
    return ricorrenza.text_content()

def getTipologia(linkSanto):
    html = requests.get(linkSanto)
    doc = lxml.html.fromstring(html.content)
    ricorrenza =  doc.xpath(xpaths['tipoFesta'])[0]
    return ricorrenza.text_content()

def getProtetti(linkSanto):
    html = requests.get(linkSanto)
    doc = lxml.html.fromstring(html.content)
    ricorrenza =  doc.xpath(xpaths['protetti'])[0]
    return ricorrenza.text_content()

def Truncate(content, sel):
    if sel == 0:
        output = content[0:2]
        if(content[3:] == "02" and int(output) <= 29 and int(output) > 0):
            return output
        elif(content[3:] == "01" or content[3:] == "03" or content[3:] == "05" or content[3:] == "07" or content[3:] == "08" or content[3:] == "10" or content[3:] == "12" and int(output) <= 31 and int(output) > 0):
            return output
        elif(content[3:] == "04" or content[3:] == "06" or content[3:] == "09" or content[3:] == "11" and int(output) <= 30 and int(output) > 0):
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
    global maintenance

    if not maintenance:

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

    else:
        articles = [InlineQueryResultArticle(
                        id='Santo del giorno',
                        title= "⚠️ Bot in Manutenzione ⚠️",
                        description= "Ci scusiamo per il disagio",
                        input_message_content=InputTextMessageContent(
                            message_text="⚠️ <b>Bot Attualmente in manutenzione.</b> ⚠️ \n\n <i>Ci scusiamo per il disagio.</i>",
                            parse_mode="HTML"
                        )
                    )]

bot.message_loop({'chat': reply, 'inline_query': on_inline_query})
while True:
    sleep(60)