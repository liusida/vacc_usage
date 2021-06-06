#!/bin/sh
# This script will be called hourly using cron jobs on zoo.uvm.edu.
set -x

echo "\nStart updating..." >> ~/vacc.update.log
date >> ~/vacc.update.log

ssh vacc-user2.uvm.edu "cd ~/gpfs2/lab/vacc_usage/ && git pull"

ssh vacc-user2.uvm.edu "cd ~/gpfs2/lab/vacc_usage/data/ && sh bluemoon.sh"
ssh dg-user2.uvm.edu "cd ~/gpfs2/lab/vacc_usage/data/ && sh deepgreen.sh"

sleep 10

ssh dg-user2.uvm.edu "cd ~/gpfs2/lab/vacc_usage/ && python generate_queue.py"
ssh dg-user2.uvm.edu "cd ~/gpfs2/lab/vacc_usage/ && python generate_history.py -d /users/d/m/dmatthe1/public/vacc_database.db"

sleep 10

rsync vacc-user2.uvm.edu:/users/s/l/sliu1/gpfs2/lab/vacc_usage/public_html/* ~/public_html/vacc/

echo "Finished." >> ~/vacc.update.log
date >> ~/vacc.update.log
