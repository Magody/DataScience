#!/bin/bash
from_job=$1
to_job=$2
for (( job=$from_job; job<=$to_job; job++ ))
do
  job_name="${job}"
  gnome-terminal -- python app_worker.py $job_name
  sleep 5
done
