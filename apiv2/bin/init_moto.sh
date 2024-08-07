#!/bin/bash

# Script to initialize moto server; runs inside the motoserver container

# Launch moto server
moto_server --host 0.0.0.0 --port $MOTO_PORT & 

# Initialize data once server is ready
sleep 1 && curl -X POST "http://localhost:${MOTO_PORT}/moto-api/recorder/replay-recording"

# Go back to moto server
wait
