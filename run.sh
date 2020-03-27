#!/usr/bin/env sh

echo "updating data and graphs"

./update_data.py
if [ -d "./graphs" ]; then
	echo "graphs dir exists"
	./generate_graphs.py &
else
	echo "graphs dir does not exist"
	./generate_graphs.py
fi


./bot.py &


i=0

while true; do
	# update every 5 hours
	if [ "$i" = "18000" ]; then
		echo "updating data and graphs"

		./update_data.py
		./generate_graphs.py &

		i=0
	fi


	if [ $(( i % 3600 )) -eq 0 ]; then
		hours_left=$(( ( 18000 - ( i / 3600 ) ) / 3600 ))
		echo "updating in $hours_left hours"
	fi


	i=$(( i + 1 ))

	sleep 1
done
