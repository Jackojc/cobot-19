#!/usr/bin/env sh

echo "updating data and graphs"
./update.sh

./bot.py &

while true; do
	echo "sleeping for 6hrs"
	sleep 21600

	echo "updating data and graphs"
	./update.sh
done
