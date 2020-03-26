#!/usr/bin/env python3

import plotly.graph_objects as go
import plotly.io as plotio

plotio.orca.config.server_url = "127.0.0.1:9091"

import shutil
import json
import os









def render_barchart(title, names, dates, datas, colours, scale = 2):
	fig = go.Figure(data = [
		go.Bar(name = name, x = dates, y = item, marker_color = colour) for
			name, item, colour in zip(names, datas, colours)
	])

	fig.update_yaxes(rangemode = "tozero")
	fig.update_xaxes(rangemode = "tozero")

	fig.update_layout(
		title = title,
		xaxis_title = "Date",
		yaxis_title = "Total",
		xaxis_tickangle = -45,
		barmode = "stack"
	)

	return plotio.to_image(fig, format = "png", scale = scale)


def render_daily_cases(country, dates, cases):
	return render_barchart(
		title = f"Daily cases in {country}",
		names = ["Cases"],
		dates = dates,
		datas = [cases],
		colours = ["red"]
	)


def render_daily_deaths(country, dates, deaths):
	return render_barchart(
		title = f"Daily deaths in {country}",
		names = ["Deaths"],
		dates = dates,
		datas = [deaths],
		colours = ["darkgrey"]
	)











def render_linechart(title, names, dates, datas, colours, scale = 2):
	fig = go.Figure()

	for name, data, colour in zip(names, datas, colours):
		fig.add_trace(
			go.Scatter(
				x = dates,
				y = data,
				name = name,
				line = dict(color = colour, width = 2),
				line_shape = "linear",
				mode = "lines+markers"
			)
		)

	fig.update_yaxes(rangemode = "tozero")
	fig.update_xaxes(rangemode = "tozero")

	fig.update_layout(
		title = title,
		xaxis_title = "Date",
		yaxis_title = "Total",
		xaxis_tickangle = -45
	)

	return plotio.to_image(fig, format = "png", scale = scale)


def render_cumulative_cases(country, dates, cases):
	return render_linechart(
		title = f"Cumulative cases in {country}",
		names = ["Cases"],
		dates = dates,
		datas = [cases],
		colours = ["red"]
	)


def render_cumulative_deaths(country, dates, deaths):
	return render_linechart(
		title = f"Cumulative deaths in {country}",
		names = ["Deaths"],
		dates = dates,
		datas = [deaths],
		colours = ["darkgrey"]
	)











def generate(data):
	num_countries = len(data.keys())

	if not os.path.isdir("graphs"):
		os.mkdir("graphs")


	for i, (country, info) in enumerate(data.items()):
		printer = f"[{i + 1}/{num_countries}] {country}"
		print(f"\r{printer} [......]", end = "")


		dates = [x["date"] for x in info]


		cumulative_cases     = [x["cumulative"]["confirmed"] for x in info]
		cumulative_deaths    = [x["cumulative"]["deaths"] for x in info]

		daily_cases     = [x["daily"]["confirmed"] for x in info]
		daily_deaths    = [x["daily"]["deaths"] for x in info]


		path = "graphs/" + "".join(
			[x for x in country.lower().replace(" ", "_") if x in "abcdefghijklmnopqrstuvwxyz_0123456789"]
		)

		if not os.path.isdir(path):
			os.mkdir(path)






		print(f"\r{printer} [=.....]", end = "")
		cum = render_linechart(
			title = f"Cumulative graph for {country}",
			names = ["Cases", "Deaths"],
			dates = dates,
			datas = [cumulative_cases, cumulative_deaths],
			colours = ["red", "darkgrey"]
		)


		print(f"\r{printer} [==....]", end = "")
		daily = render_barchart(
			title = f"Daily graph for {country}",
			names = ["Cases", "Deaths"],
			dates = dates,
			datas = [daily_cases, daily_deaths],
			colours = ["red", "darkgrey"]
		)


		with open(path + "/cum.png", "wb") as f:
			f.write(cum)


		with open(path + "/daily.png", "wb") as f:
			f.write(daily)



		print(f"\r{printer} [===...]", end = "")
		with open(path + "/cum_cases.png", "wb") as f:
			f.write(render_cumulative_cases(country, dates, cumulative_cases))


		print(f"\r{printer} [====..]", end = "")
		with open(path + "/cum_deaths.png", "wb") as f:
			f.write(render_cumulative_deaths(country, dates, cumulative_deaths))


		print(f"\r{printer} [=====.]", end = "")
		with open(path + "/daily_cases.png", "wb") as f:
			f.write(render_daily_cases(country, dates, daily_cases))


		print(f"\r{printer} [======]", end = "")
		with open(path + "/daily_deaths.png", "wb") as f:
			f.write(render_daily_deaths(country, dates, daily_deaths))


		print(f"\r{printer} [ done ]")






if __name__ == "__main__":
	with open("data/data.json") as f:
		f = json.load(f)

	generate(f)

	print("done!")
