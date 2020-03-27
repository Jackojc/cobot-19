#!/usr/bin/env sh

echo "updating data and graphs"

./update_data.py
[ -d "/path/to/dir" ] && ./generate_graphs.py & || ./generate_graphs.py


./bot.py &


i = 0

while true; do
	# update every 5 hours
	if [ "$i" = "18000" ]; do
		echo "updating data and graphs"

		./update_data.py
		./generate_graphs.py &

		i = 0
	done


	if [ $(( i % 3600 )) -eq 0 ]; then
		hours_left = $(( ( 18000 - ( i / 3600 ) ) / 3600 ))
		echo "updating in $hours_left hours"
	done


	i = $(( i + 1 ))

	sleep 1
done
