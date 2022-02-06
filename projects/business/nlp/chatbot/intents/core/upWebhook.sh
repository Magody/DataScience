#!/bin/bash
conda activate ridetel_chatbot
export LC_ALL=en_US.UTF-8
MODE="${1}"
USERNAME="${2}"
nohup python messenger_webhook.py "${MODE}" & > "nohup_web_hook_${MODE}.out"
