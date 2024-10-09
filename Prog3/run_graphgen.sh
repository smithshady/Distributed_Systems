#!/bin/bash

# Initialize variable
nodes=20
max=400

# Loop until var is greater than or equal to some limit (e.g., 200)
while [ $nodes -le $max ]
do
    python generate.py $nodes random
    nodes=$((nodes + 20))  # Increment var by 20
done