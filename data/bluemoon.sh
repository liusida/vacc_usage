#!/bin/sh
set -x
squeue -O "jobid,username,partition,name,timeleft,batchhost,tres-per-node,tres-alloc" > bluemoon.queue.txt
