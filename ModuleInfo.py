from .. import loader, utils
from time import time
import asyncio
import re
import json
import requests

@loader.tds
class modInfoMod(loader.Module):
    strings = {"name": "ModuleInfo"}

    def __init__(self):
        self.config = loader.ModuleConfig("maximum_fw_error", 5, lambda: "Порог срабатывания защиты от FloodWait")

    async def modinfocmd(self, message):
        """.modinfo <reply_to_file|file> - Check the file for malisious code"""
        TEMPLATE = "👮‍♂️ <b>Информация о {0}</b>\n\n<b>👀 Зависимости:</b>\n{1}\n{2}"
        reply = await message.get_reply_message()
        if not reply and type(message.media) is None:
            await message.edit("<b>Мне какой файл проверять, не подскажешь?... 🗿</b>")
            return
        if not reply:
            media = message.media
        else:
            media = reply.media

        file = await message.client.download_file(media)
        try:
            code = file.decode('utf-8').replace('\r\n', '\n')
        except:
            await message.edit('<b>Не могу проверить файл...</b>')
            await asyncio.sleep(3)
            await message.delete()
            return

        filter_regex = {
            ('DeleteAccou' + 'ntRequest'): r'[dD].*[eE].*[lL].*[eE].*[tT].*[eE].*[aA].*[cC].*[oO].*[uU].*[nN].*[tT].*[rR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]', 
            'ChangePhoneRequest': r'[CC].*[hH].*[aA].*[nN].*[gG].*[eE].*[PP].*[hH].*[oO].*[nN].*[eE].*[RR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]', 
            'FinishTakeoutSession': r'[fF].*[iI].*[nN].*[iI].*[sS].*[hH].*[TT].*[aA].*[kK].*[eE].*[oO].*[uU].*[tT].*[SS].*[eE].*[sS].*[sS].*[iI].*[oO].*[nN]', 
            'SetAccountTTL': r'[sS].*[eE].*[tT].*[AA].*[cC].*[cC].*[oO].*[uU].*[nN].*[tT].*[TT].*[TT].*[LL].*[RR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]', 
            'UpdatePasswordSettings': r'[uU].*[pP].*[dD].*[aA].*[tT].*[eE].*[PP].*[aA].*[sS].*[sS].*[wW].*[oO].*[rR].*[dD].*[SS].*[eE].*[tT].*[tT].*[iI].*[nN].*[gG].*[sS]', 
            'GetAllSecureValuesRequest': r'[GG].*[eE].*[tT].*[AA].*[lL].*[lL].*[SS].*[eE].*[cC].*[uU].*[rR].*[eE].*[VV].*[aA].*[lL].*[uU].*[eE].*[sS].*[RR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]',
            'client.phone': r'[.]phone[^_]',
            'client.session': r'[.]session[^_]',
            'StringSession': r'StringSession',
        }

        try:
            mod_name = re.search(r"""strings[ ]*=[ ]*{.*?name['"]:[ ]*['"](.*?)['"]""", code, re.S).group(1)
        except:
            mod_name = "Unknown"

        import_regex = [r'^[^#]rom ([^\n\r]*) import [^\n\r]*$', r'^[^#]mport ([^\n\r]*)[^\n\r]*$', r"""__import__[(]['"]([^'"]*)['"][)]"""]
        imports = []
        for import_re in import_regex:
            imports = imports + re.findall(import_re, code, flags=re.M|re.DOTALL)

        if '..' in imports:
            del imports[imports.index('..')]

        imports_formatted = ""
        for dependency in imports:
            imports_formatted += f"    ▫️ {dependency}\n"

        if len(imports) == 0:
            imports_formatted = "<i>Нет</i>"

        comments = ""

        if 'requests' in imports:
            comments += "🔅 Найдена библиотека <b>requests</b>. Она может быть использована для слива сессии. Рекомендуется проверить код.\n"
        if 'urllib' in imports:
            comments += "🔅 Найдена библиотека <b>urllib</b>. Она может быть использована для слива сессии. Рекомендуется проверить код.\n"
        if 'urllib3' in imports:
            comments += "🔅 Найдена библиотека <b>urllib3</b>. Она может быть использована для слива сессии. Рекомендуется проверить код.\n"
        if 'base64' in imports:
            comments += "🔅 Найдена библиотека <b>base64</b>. Она может быть использована для скрытия вредоносного кода. Рекомендуется ручная проверка.\n"
        if 'while True' in code or 'while 1' in code:
            comments += "🔅 Найден <b>бесконечный цикл</b>. Зачастую это плохо сказывается на асинхронности кода.\n"
        if '.edit(' in code:
            comments += "🔅 Найдено <b>классическое редактирование сообщений</b>. Данный модуль не получится использовать с твинка.\n"
        if re.search(r'@.*?[bB][oO][tT]', code) is not None:
            comments += "🔅 Найден <b>Бот-абьюз</b>. Данный модуль умрет вместе с используемым ботом.\n"

        for comm, regex in filter_regex.items():
            if re.search(regex, code) is not None:
                comments = "🚫 Найден вредоносный код по фильтру <code>" + comm + "</code>!\n" + comments

        functions = {}
        watching_function = False
        cmd_name = ""
        for line in code.split('\n'):
            if len(line) <= 1:
                continue
            if not watching_function:
                match = re.search(r'[\t ]*?def (.*?)cmd.*', line)
                if match is not None:
                    cmd_name = match.group(1)
                else:
                    continue

                num_of_tabs = 0
                i = 0
                while line[i:][:4] == "    " or line[i] == '\t':
                    num_of_tabs += 1
                    i += 1
                    if line[i - 1:][:4] == "    ":
                        i += 3

                num_of_tabs += 1
                watching_function = True
            else:
                current_tabs = 0
                i = 0
                while len(line) > i and ((len(line) > 5 and line[i:][:4] == "    ") or line[i] == '\t'):
                    current_tabs += 1
                    i += 1
                    if line[i - 1:][:4] == "    ":
                        i += 3

                if current_tabs >= num_of_tabs:
                    if cmd_name not in functions:
                        functions[cmd_name] = ""
                    functions[cmd_name] += line + '\n'
                else:
                    watching_function = False

        for func_name, func_code in functions.items():
            number_of_occurencies = func_code.count('.answer(') + func_code.count('.edit(') + func_code.count('.delete(') + func_code.count('.send(')
            if number_of_occurencies >= self.config['maximum_fw_error']:
                comments += f"⏱ В функции <b>{func_name}</b> найден <b>потенциальный</b> FloodWait. Количество запросов: <b>{number_of_occurencies}</b>\n"


        await utils.answer(message, TEMPLATE.format(mod_name, imports_formatted, comments))


