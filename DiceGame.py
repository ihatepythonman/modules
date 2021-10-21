from .. import loader, utils
import random
class DiceGameMod(loader.Module):
	strings = {"name": "DiceGame"}
	
	async def kostcmd(self, message):
		args = utils.get_args_raw(message)
		if args == "1":
			await message.edit("⬜⬜⬜\n⬜⬛⬜\n⬜⬜⬜\n\nВам выпало 1!")
		if args == "2":
			await message.edit("⬜⬛⬜\n⬜⬜⬜\n⬜⬛⬜\n\nВам выпало 2!")
		if args == "3":
			await message.edit("⬛⬜⬜\n⬜⬛⬜\n⬜⬜⬛\n\nВам выпало 3!")
		if args == "4":
			await message.edit("⬛⬜⬛\n⬜⬜⬜\n⬛⬜⬛\n\nВам выпало 4!")
		if args == "5":
			await message.edit("⬛⬜⬛\n⬜⬛⬜\n⬛⬜⬛\n\nВам выпало 5!")
		if args == "6":
			await message.edit("⬛⬜⬛\n⬛⬜⬛\n⬛⬜⬛\n\nВам выпало 6!")
		if args == "0":
			a = "⬜⬜⬜\n⬜⬛⬜\n⬜⬜⬜\n\nВам выпало 1!"
			b = "⬜⬛⬜\n⬜⬜⬜\n⬜⬛⬜\n\nВам выпало 2!"
			c = "⬛⬜⬜\n⬜⬛⬜\n⬜⬜⬛\n\nВам выпало 3!"
			d = "⬛⬜⬛\n⬜⬜⬜\n⬛⬜⬛\n\nВам выпало 4!"
			e = "⬛⬜⬛\n⬜⬛⬜\n⬛⬜⬛\n\nВам выпало 5!"
			f = "⬛⬜⬛\n⬛⬜⬛\n⬛⬜⬛\n\nВам выпало 6!"
			kost = [a, b, c, d, e, f]
			rand = random.choice(kost)
			await message.edit(rand)
			
			