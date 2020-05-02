#!/usr/bin/env python3

import requests
import json
import os





if __name__ == "__main__":
	r = requests.get("https://pomber.github.io/covid19/timeseries.json")

	if r.status_code != 200:
		print(f"Error while fetching new data. http {r.status_code}")

	data = r.json()


	for country, info in data.items():
		info[0]["daily"] = {
			"confirmed": 0,
			"deaths": 0,
			"recovered": 0
		}

		del info[0]["confirmed"]
		del info[0]["deaths"]
		del info[0]["recovered"]

		info[0]["cumulative"] = {
			"confirmed": 0,
			"deaths": 0,
			"recovered": 0
		}

		info[0]["active"] = 0


		for i, x in enumerate(info[1:]):
			cases      = x["confirmed"]
			deaths     = x["deaths"]
			recovered  = x["recovered"]

			del x["confirmed"]
			del x["deaths"]
			del x["recovered"]

			x["cumulative"] = {
				"confirmed": cases,
				"deaths": deaths,
				"recovered": recovered
			}

			prev_cases      = info[i]["cumulative"]["confirmed"]
			prev_deaths     = info[i]["cumulative"]["deaths"]
			prev_recovered  = info[i]["cumulative"]["recovered"]


			data[country][i + 1]["daily"] = {
				"confirmed": abs(prev_cases - cases),
				"deaths":    abs(prev_deaths - deaths),
				"recovered":    abs(prev_recovered - recovered)
			}

			x["active"] = cases - (deaths + recovered)



	timeline = {}

	for country, days in data.items():
		for day in days:
			date = day["date"]

			if date not in timeline:
				timeline[date] = {}

			if country not in timeline[date]:
				timeline[date][country] = day

	# Data for all cases globally for a certain day
	for day, countries in timeline.items():
		total_confirmed = 0
		total_deaths    = 0
		total_recovered = 0

		daily_confirmed = 0
		daily_deaths    = 0
		daily_recovered = 0

		total_active 	= 0

		for country in countries:
			confirmed = timeline[day][country]["cumulative"]["confirmed"]
			deaths    = timeline[day][country]["cumulative"]["deaths"]
			recovered = timeline[day][country]["cumulative"]["recovered"]

			today_confirmed = timeline[day][country]["daily"]["confirmed"]
			today_deaths    = timeline[day][country]["daily"]["deaths"]
			today_recovered = timeline[day][country]["daily"]["recovered"]

			today_active = timeline[day][country]["active"]

			total_confirmed += confirmed
			total_deaths    += deaths
			total_recovered += recovered

			daily_confirmed += today_confirmed
			daily_deaths    += today_deaths
			daily_recovered += today_recovered

			total_active += today_active


		if "World" not in data:
			data["World"] = []

		world = {
			"date": day,
			"cumulative": {
				"confirmed": total_confirmed,
				"deaths": total_deaths,
				"recovered": total_recovered
			},
			"daily": {
				"confirmed": daily_confirmed,
				"deaths": daily_deaths,
				"recovered": daily_recovered
			},
			"active": total_active
		}

		data["World"].append(world)


	trimmed_data = {}

	for country, info in data.items():
		for i, entry in enumerate(info):
			cases      = entry["cumulative"]["confirmed"]
			deaths     = entry["cumulative"]["deaths"]
			recovered  = entry["cumulative"]["recovered"]

			cases      = cases > 0
			deaths     = deaths > 0
			recovered  = recovered > 0

			# If we find an entry which has at least one
			# value >0, we can assume that all following entries will
			# >0 too. We add one previous day before the countries first
			# case so we can plot it properly.
			if any([cases, deaths, recovered]):
				trimmed_data[country] = info[max(i - 1, 0):]
				break


	for country in list(trimmed_data.keys()):
		new_key = "".join([x for x in country if x.lower() in "abcdefghijklmnopqrstuvwxyz "])
		trimmed_data[new_key] = trimmed_data.pop(country)



	if not os.path.isdir("data"):
		os.mkdir("data")

	with open("data/data.json", "w") as f:
		f.write(json.dumps(trimmed_data, indent = 4))


	print("done!")
