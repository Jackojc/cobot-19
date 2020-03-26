#!/usr/bin/env python3

import requests
import json
import os





if __name__ == "__main__":
	r = requests.get("https://pomber.github.io/covid19/timeseries.json")

	if r.status_code != 200:
		print(f"Error while fetching new data. http {r.status_code}")

	data = r.json()
	trimmed_data = {}

	for country, info in data.items():
		for i, entry in enumerate(info):
			cases      = entry["confirmed"]
			deaths     = entry["deaths"]

			cases      = cases > 0
			deaths     = deaths > 0

			# If we find an entry which has at least one
			# value >0, we can assume that all following entries will
			# >0 too. We add one previous day before the countries first
			# case so we can plot it properly.
			if any([cases, deaths]):
				trimmed_data[country] = info[max(i - 1, 0):]
				break



	for country, info in trimmed_data.items():
		info[0]["daily"] = {
			"confirmed": 0,
			"deaths": 0
		}

		del info[0]["confirmed"]
		del info[0]["deaths"]

		info[0]["cumulative"] = {
			"confirmed": 0,
			"deaths": 0
		}


		for i, x in enumerate(info[1:]):
			cases      = x["confirmed"]
			deaths     = x["deaths"]

			del x["confirmed"]
			del x["deaths"]

			x["cumulative"] = {
				"confirmed": cases,
				"deaths": deaths
			}

			prev_cases      = info[i]["cumulative"]["confirmed"]
			prev_deaths     = info[i]["cumulative"]["deaths"]


			trimmed_data[country][i + 1]["daily"] = {
				"confirmed": abs(prev_cases - cases),
				"deaths":    abs(prev_deaths - deaths)
			}




	timeline = {}

	for country, days in trimmed_data.items():
		for day in days:
			date = day["date"]

			if date not in timeline:
				timeline[date] = {}

			if country not in timeline[date]:
				timeline[date][country] = day


	for day, countries in timeline.items():
		total_confirmed = 0
		total_deaths    = 0

		daily_confirmed = 0
		daily_deaths    = 0

		for country in countries:
			confirmed = timeline[day][country]["cumulative"]["confirmed"]
			deaths    = timeline[day][country]["cumulative"]["deaths"]

			today_confirmed = timeline[day][country]["daily"]["confirmed"]
			today_deaths    = timeline[day][country]["daily"]["deaths"]


			total_confirmed += confirmed
			total_deaths    += deaths

			daily_confirmed += today_confirmed
			daily_deaths    += today_deaths


		if "World" not in trimmed_data:
			trimmed_data["World"] = []

		world = {
			"date": day,
			"cumulative": {
				"confirmed": total_confirmed,
				"deaths": total_deaths
			},
			"daily": {
				"confirmed": daily_confirmed,
				"deaths": daily_deaths
			}
		}

		trimmed_data["World"].append(world)



	if not os.path.isdir("data"):
		os.mkdir("data")

	with open("data/data.json", "w") as f:
		f.write(json.dumps(trimmed_data, indent = 4))


	print("done!")
