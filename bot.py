#!/usr/bin/env python3

from fuzzywuzzy import process

import argparse
import discord
import json
import io



# Custom class to override automatically exiting and printing errors/help.
class ArgumentParser(argparse.ArgumentParser):
	def error(self, message):
		raise Exception(message)

	def print_help(self, *args, **kwargs):
		pass








# Setup parser.
parser = ArgumentParser(prog = ".covid", description = "Get statistics on Covid-19 across the globe.")
modes = parser.add_mutually_exclusive_group()
stat = parser.add_mutually_exclusive_group()



modes.add_argument(
	 "-C","--cumulative",
	action = "store_const",
	dest = "mode",
	const = "cumulative",
	help = "plot cumulative statistics."
)

modes.add_argument(
	"-D", "--daily",
	action = "store_const",
	dest = "mode",
	const = "daily",
	help = "plot daily statistics."
)



stat.add_argument(
	"-a", "--all",
	action = "store_const",
	dest = "stat",
	const = "all",
	help = "show stats for cases and deaths."
)

stat.add_argument(
	"-c", "--cases",
	action = "store_const",
	dest = "stat",
	const = "cases",
	help = "show stats for cases."
)

stat.add_argument(
	"-d", "--deaths",
	action = "store_const",
	dest = "stat",
	const = "deaths",
	help = "show stats for deaths."
)


parser.add_argument(
	"country",
	type = str,
	nargs = "?",
	default = "",
	help = "the country to get stats for."
)



modes.set_defaults(mode = "cumulative")
stat.set_defaults(stat = "all")


# parser.add_argument(
# 	"-r", "--refresh",
# 	action = "store_true",
# 	dest = "refresh",
# 	help = "do not use the cached graph, force it to be rendered anew."
# )





FILE_CACHE = {}



def get_graph(country, mode, stat):
	path = "graphs/" + "".join(
		[x for x in country.lower().replace(" ", "_") if x in "abcdefghijklmnopqrstuvwxyz_0123456789"]
	) + "/"


	if mode == "cumulative":
		path += "cum"

	elif mode == "daily":
		path += "daily"



	if stat == "all":
		path += ".png"

	elif stat == "cases":
		path += "_cases.png"

	elif stat == "deaths":
		path += "_deaths.png"


	return path




def get_embed(country, mode, data):
	embed = None
	data = data[country]


	if mode == "cumulative":
		cases      = data[-1]["cumulative"]["confirmed"]
		deaths     = data[-1]["cumulative"]["deaths"]

		embed = discord.Embed(
			title = f"Covid-19",
			description = f"Cumulative statistics for Covid-19 in {country}",
			color = 0x55ff55
		)

		embed.add_field(name="Total cases", value=f"{cases}")
		embed.add_field(name="Total deaths", value=f"{deaths}")


	elif mode == "daily":
		cases      = data[-1]["daily"]["confirmed"]
		deaths     = data[-1]["daily"]["deaths"]

		embed = discord.Embed(
			title = f"Covid-19",
			description = f"Daily statistics for Covid-19 in {country}",
			color = 0xff55ff
		)

		embed.add_field(name="New cases today", value=f"{cases}")
		embed.add_field(name="New deaths today", value=f"{deaths}")


	return embed




class Client(discord.Client):
	async def on_ready(self):
		print(f"logged in: {self.user}")
		await self.change_presence(status = discord.Status.online, activity = discord.Game(".covid -h for help"))



	async def on_message(self, message):
		# Only look at messages from other users.
		if message.author == self.user or message.author.bot or message.content == "":
			return

		# Split up arguments and check for prefix.
		msg = message.content.split()
		prefix, args = msg[0], msg[1:]

		if prefix != ".covid":
			return






		parsed_args = None

		try:
			parsed_args = parser.parse_args(args)

		# Catch errors.
		except Exception as e:
			await message.channel.send(str(e))
			return

		# Catch help.
		except SystemExit as e:
			await message.channel.send(f"```{parser.format_help()}```")
			return



		author = message.author.name
		guild = None

		try:
			guild = message.guild.name

		except:
			guild = "private message"

		print(author + " " + guild)





		# Valid command.
		country = parsed_args.country

		with open("data/data.json") as f:
			data = json.load(f)



		if country == "":
			country = "World"

		else:
			country = " ".join(country)
			match, confidence = process.extractOne(country, data.keys())

			if confidence < 95:
				await message.channel.send(f"\t'{country}' does not match any known countries.")
				return

			print(f"\tconfidence: {confidence}")

			country = match



		mode = parsed_args.mode
		stat = parsed_args.stat


		path = get_graph(country, mode, stat)
		embed = get_embed(country, mode, data)

		print(f"\t{path}")


		with open(path, "rb") as f:
			f = discord.File(f, filename = "graph.png")
			await message.channel.send(file = f, content = "", embed = embed)










if __name__ == "__main__":
	if not os.path.isfile("token.txt"):
		print("No token.txt file, create it and insert your bot token there.")

	with open("token.txt") as token:
		token = token.read()

	client = Client()
	client.run(token)

