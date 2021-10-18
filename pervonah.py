from .. import loader, utils

from telethon.utils import get_peer_id
from asyncio import sleep


@loader.tds
class PerconahMod(loader.Module):
    """
    Спешиал фор @Ihatepython
    """

    strings = {"name": "PervoNah"}

    async def client_ready(self, client, db):
        self.db = db
        if not dict(self.db).get("PervoNah"):
            self.db.set("PervoNah", "text", "Я первый, в списке даунов")
            self.db.set("PervoNah", "status", False)
            self.db.set("PervoNah", "list", [])


    async def pnswcmd(self, message):
        """
        Используй: .pnsw, для включения/выключения режима
        """

        self.db.set("PervoNah", "status", (not self.db.get("PervoNah", "status")))
        return await message.edit(
            "Теперь статус: " + ("Включен" if self.db.get("PervoNah", "status") else "Выключен")
        )


    async def pntextcmd(self, message):
        """
        Используй .pntext <текст>, для изменения текста отправки комментария
        """

        self.db.set("PervoNah", "text", utils.get_args_raw(message))
        return await message.edit(
            "Текст был изменён успешно")


    async def pnaddcmd(self, message):
        """
        Используй: .pnadd <@ или ID> (через запятую), для добавления канала в базу
        """

        if not (args := utils.get_args_raw(message).split()):
            return await message.edit(
                "Нет аргументов")

        channels = self.db.get("PervoNah", "list", [])
        for arg in args:
            try:
                channels.append(
                    str(get_peer_id(
                        await message.client.get_entity(int(arg) if arg.isdigit() else arg)
                    ))
                )
            except Exception as e:
                await message.reply(
                    f"{arg} не был добавлен в базу, потому что невозможно было получить информацию по причине: {e}")

        self.db.set("PervoNah", "list", channels)
        return await message.edit(
            "Канал(-ы) были добавлены в базу")


    async def pndelcmd(self, message):
        """
        Используй: .pndel <ID или all>, для удаления канала из базы
        """

        if not (args := utils.get_args_raw()):
            return await message.edit(
                "Нет аргументов")

        if args == "all":
            self.db.set("PervoNah", "list", [])
            return await message.edit(
                "Теперь база пуста")

        if args not in (channels := self.db.get("PervoNah", "list")):
            return await message.edit(
                "Этого айди нет в базе")

        channels.remove(args) 
        self.db.set("PervoNah", "list", channels)

        return await message.edit(
            f"Из базы был удален {args}")


    async def pnscmd(self, message):
        """
        Используй: .pns, для просмотра всех айди в базе
        """

        if not (channels := self.db.get("PervoNah", "list")):
            return await message.edit(
                "База пуста")

        msg = "".join(f"— <code>{channel}</code>\n" for channel in channels)
        return await message.edit(f"Айди каналов, в которых будут отправляться сообщения:\n\n{msg}")


    async def watcher(self, message):
        if (
            not self.db.get("PervoNah", "status")
            or message.chat_id not in self.db.get("PervoNah", "list")
        ):
            return

        try:
            await message.client.send_message(
                message.chat_id, self.db.get("PervoNah", "text"),
                comment_to = message.id
            )
        except Exception as e:
            await message.client.send_message(-1001384735383, str(e))

