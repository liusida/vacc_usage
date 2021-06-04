#!/bin/sh
set -x
squeue -O "jobid,username:100,partition,name,timeleft,batchhost,tres-per-node,tres-alloc:100" > deepgreen.queue.txt
sinfo -N -O "partition,nodelist,cpus,gres,gresused,memory" > deepgreen.assets.txt
