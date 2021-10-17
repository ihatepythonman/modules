import asyncio
import time
import requests
import json
from lxml import etree
from random import randint
from userbot.events import register
@register(outgoing=True, pattern='^.crypto(?: |$)(.*)')
async def typewriter(type):
	args = type.message.text.split(" ", maxsplit=2)
	await type.edit("Wait...")
	try:
		xml_response = etree.fromstring(requests.get("http://www.cbr.ru/scripts/XML_daily.asp").text.encode("1251"))
		curs = xml_response.find("Valute[@ID='R01235']/Value").text
		curs = float(curs.replace(',', '.'))
		url = f"https://api.bittrex.com/api/v1.1/public/getticker?market=USD-{args[1]}"
		j = requests.get(url)
		data = json.loads(j.text)
		price = data['result']['Ask']
		oldprice = data['result']['Last']
		if price < oldprice:
			x = "📉"
		elif price > oldprice:
			x = "📈"
		else:
			x = "📊"
		alo = float(price) * float(curs)
		alo = float(round(alo, 2))
		btcproce = f"💰 Price {args[1]}: \n\nUSD: {price}$ {x}\n" + str("RUB: ") + str(alo) + str(
			"₽") + f"\n**This auto-generated message shall be self destructed in 60 seconds.**"
		await type.edit(btcproce)
		time.sleep(60)
		await type.delete()
	except:
		await type.edit("error")
