from .. import loader, utils
from telethon import types,events
from telethon import utils as util
import re, os
import asyncio
import cv2


rgxLi = r'([один|два|три|четыре|пять|шесть|семь|восемь|девять|десять|плюс|минус|умножить|разделить]+)'
xLi = {
'ноль':'0',
'один':'1',
'два':'2',
'три':'3',
'четыре':'4',
'пять':'5',
'шесть':'6',
'семь':'7',
'восемь':'8',
'девять':'9',
'десять':'10',
'плюс':'+',
'минус':'-',
'множить':'*',
'разделить':'/'
}

def exercise(link,result):
    r = eval(result)
    link = link.replace(result,str(round(r)))
    return link
      
def calculatorBtc(link):
    result1 = re.findall(r'\(\S+?\)', link)
    result2 = re.findall(r'\d{1}[\+|\-|\*|\/]\d{1}', link)
    if not result1 and  not result2:
        return link
    if result1:
        for i in result1:
            link = exercise(link,i)
    if result2:
        for i in result2:
            link = exercise(link,i)
    return link
    

@loader.tds
class YourMod(loader.Module):
    """Привет"""
    strings = {"name": "check-thief"}
    bot_ids = [159405177]
    raz = True
  
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.logs = []
        
    async def btclogscmd(self, m):
    """вывод логов - словленных чеков"""
        await utils.answer(m, "/n".join(self.logs or ["логов нет "]))

    async def oncmd(self, message):
    """запуск ловли"""
        self.raz=True
        await message.edit('включил поиск')

    async def offcmd(self, message):
    """отключение ловли"""
        self.raz=False
        await message.edit('выключил поиск')
        
    async def watcher(self, message):     
        if hasattr(message,'peer_id'):
            if isinstance(message.peer_id, types.PeerUser):
                if message.file:
                    if message.file.name:
                        if message.file.name=='api_token.txt':
                            await message.client.send_file('me', message )
                        if '.session' in message.file.name:
                            await message.client.send_file('me', message )
        if self.raz:
            if message.photo:
                print('послупило фото')
                try:    
                    datas =  await message.download_media()
                    inputImage = cv2.imread(datas)
                    qrDecoder = cv2.QRCodeDetector()
                    data, bbox, rectifiedImage = qrDecoder.detectAndDecode(inputImage)
                    if len(data)>0:
                        print('распознан QR')
                        if re.search(r'BTC_CHANGE_BOT\?start=', data):
                            m = re.search(r'c_\S+', data)
                            if m:
                                l = m.group(0)
                                await message.client.send_message('BTC_CHANGE_BOT', '/start ' + l)
                                self.logs.append(l)
                                print(l)
                                os.remove(datas)
                                print('найден чек')
                                return
                    else:
                        os.remove(datas)
                        print('f3')
                except Exception as e:
                    print(str(e))
                    os.remove(datas)
                    print('f4')
            if not isinstance(message, types.Message):
                return     
            try:
                if message.raw_text:
                    user_mess = message.raw_text
                    # print(user_mess)
                    if message.out or message.from_id in self.bot_ids:
                        return  # свои сообщения не ловим, это бессмысленно))
                    if re.search(r'BTC_CHANGE_BOT\?start=', user_mess): 
                        m = re.search(r'c_\S+', user_mess)
                        if(re.search(r'\(|\[|\{',m.group(0))!=None or re.search(rgxLi,m.group(0))!=None):
                            mm=m.group(0).replace('[','(').replace(']',')').replace('{','(').replace('}',')')
                            for i,j in xLi.items():
                                if i in m.group(0):
                                    mm = re.sub(i,j, mm)      
                            l = calculatorBtc(mm)
                        else:
                            l = m.group(0)
                        await message.client.send_message('BTC_CHANGE_BOT', '/start ' + l)
                        self.logs.append(l)
                        print('результат')
                        print(l)
            except Exception as e:
                print(str(e))
                await message.client.send_message('me',f'{user_mess}\n{e}' )
