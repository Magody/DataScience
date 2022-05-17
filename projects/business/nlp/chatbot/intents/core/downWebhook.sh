#!/bin/bash
USERNAME="${1}"
echo "ABOUT TO EXECUTE |pkill -f ${USERNAME}| check is not empty the parameter and the name is not common"
if [ "${USERNAME}" == "" ]; then
  echo "FATAL INSTRUCTION: DONT SEND EMPTY PARAMETER TO pkill -f, closing program"
  return
fi
echo "parameter not empty, waiting 10s"
sleep 10
pkill -f "${USERNAME}"
