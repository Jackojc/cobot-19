#!/usr/bin/env sh

./update_data.py
./generate_graphs.py

pkill -f orca
pkill -f generate_graphs
