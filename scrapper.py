import requests
from bs4 import BeautifulSoup
import re
import time
from telegram.ext import Updater, CommandHandler
import json
import constants
import threading

updater = Updater(token=constants.key_token, use_context=True)
dispatcher = updater.dispatcher

def getPageContent(str):
    URL = str
    page = requests.get(URL)
    return page.content

def getData(page,local,type,Class):
    soup = BeautifulSoup(page, "html.parser")
    results = soup.find(local)
    results = results.find_all(type, class_=Class)
    return results

def scrapper(int,str, local, type, Class):
    results = getData(getPageContent(str),local,type,Class)
    return results[int].text.strip()

def removeLetters(str):
    return re.sub('[^0-9]','',str)

def getAgeFromSite():
    return int(removeLetters(scrapper(3,"https://deolhonaconsulta.jaboatao.pe.gov.br/vac/formulario_de_olho.php","body","label","form-check-label")))

def commandProcessingStart(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=
    ("Oi!\nSou um bot que te indica a idade atual da vacinação em Jaboatão!\n\n"))
    commandProcessingComandos(update, context)

def commandProcessingComandos(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=
    (
    "Lista de Comandos:\n"
    "/start          = iniciar o bot(vc já usou esse comando ;) )\n"
    "/idade          = Saber a idade atual de vacinação\n"
    "/comandos       = Imprimir lista de comandos\n"
    "/watcher IDADE  = Coloca um Watcher sobre uma idade\n"
    "/stop           = Fechar o bot\n"
    )
    )

def commandProcessingIdade(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=
    ("A idade atual em Jaboatão é {0}!".format(internalAge)))

def commandProcessingStop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=
    ("Bot encerrando :D !"))
    updater.stop()
    context.bot.send_message(chat_id=update.effective_chat.id, text=
    ("Bot encerrado :D !"))

def loopForAge(idade,update,context):
    actualAge = getAgeFromSite()
    while actualAge > idade:
        time.sleep(900)
        actualAge = getAgeFromSite()
    context.bot.send_message(chat_id=update.effective_chat.id, text=
    ("Hey! A idade que você selecionou esta sendo acobertada agora, idade atual é {0}".format(actualAge)))

def internalWatcher():
    global internalAge
    internalAge = getAgeFromSite()
    while internalAge > 18:
        time.sleep(900)
        internalAge = getAgeFromSite()
    

def commandProcessingWatcher(update, context):
    desireAge = removeLetters(update.message.text)
    try:
        desireAge = int(desireAge)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text=
        ("Idade Invalida!"))
    else:
        
        if threading.active_count() < 10:
            context.bot.send_message(chat_id=update.effective_chat.id, text=
            ("Okay vamos ficar de olho nessa idade para você!"))
            thread = threading.Thread(target=loopForAge, args=(desireAge,update,context,))
            thread.start()

        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=
            ("Eita nossos observadores estão ocupados, tenta mais tarde! :( "))


def startBot():

    start_handler     = CommandHandler('start', commandProcessingStart)
    idade_handler     = CommandHandler('idade', commandProcessingIdade)
    stop_handler      = CommandHandler('stop', commandProcessingStop)
    comandos_handler  = CommandHandler('comandos', commandProcessingComandos)
    watcher_handler   = CommandHandler('watcher', commandProcessingWatcher)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(idade_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(comandos_handler)
    dispatcher.add_handler(watcher_handler)

    thread = threading.Thread(target=internalWatcher, args=())
    thread.start()

    updater.start_polling()

startBot()
