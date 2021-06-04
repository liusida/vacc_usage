#!/bin/sh
set -x
squeue -O "jobid,username:100,partition,name,timeleft,batchhost,tres-per-node,tres-alloc:100" > bluemoon.queue.txt
sinfo -Nel > bluemoon.assets.txt
