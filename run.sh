#!/usr/bin/env sh

./bot.py &

while true; do
	echo "updating data and graphs"
	./update.sh

	echo "sleeping for 6hrs"
	sleep 21600
done
