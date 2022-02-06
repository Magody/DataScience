#!/bin/bash
conda activate ridetel_chatbot
export LC_ALL=en_US.UTF-8
MODE="${1}"
USERNAME="${2}"
nohup python messenger_io_websockets.py "${MODE}" & > "nohup_socket_${MODE}.out"
