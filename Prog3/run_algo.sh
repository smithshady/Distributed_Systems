#!/bin/bash

# Initialize variable
nodes=20
max=400

# Loop until var is greater than or equal to some limit (e.g., 200)
while [ $nodes -le $max ]
do
    python main.py 1 basic files/inp-$nodes-random.txt
    if [ $? -ne 0 ]; then
        echo "The command failed with an error."
        exit 1
    fi
    nodes=$((nodes + 20))
done