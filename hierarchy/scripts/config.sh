#!/bin/bash

##Usage: Script

my_dir="$(dirname "$0")"
source $my_dir/env.sh

#analyze the weighted dependence graph to generate config files
start=`date +%s.%N`
time python -O $auto_tuning/src/graphAnalysis/varDepGraph_pro.py
end=`date +%s.%N`
runtime=$(echo "$end - $start" | bc)
echo "auto-tuning config finishes in $runtime seconds" > auto-tuning_config_time.txt
