#!/bin/sh
set -x
squeue -O "jobid,username:100,partition,name,timeleft,batchhost,tres-per-node,tres-alloc:100" > deepgreen.queue.txt
sinfo -Nel > deepgreen.assets.txt
