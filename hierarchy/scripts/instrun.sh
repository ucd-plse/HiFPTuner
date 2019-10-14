#!/bin/bash

##Usage: Script json_{test}.bc

my_dir="$(dirname "$0")"
source $my_dir/env.sh

test=`echo $1 | sed 's/\(.*\).bc/\1/'`

echo "start to run the instrumented file"
start=`date +%s.%N`
time ./i_$test.out
#echo ./i_$test.out
end=`date +%s.%N`
runtime=$(echo "$end - $start" | bc)
echo "instrumented file finished its execution in $runtime seconds" > auto-tuning_analyze_time.txt
