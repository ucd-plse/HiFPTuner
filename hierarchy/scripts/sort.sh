#!/bin/bash
my_dir="$(dirname "$0")"
source $my_dir/env.sh

sfile=$1
cfile=$2
order=$3

python $auto_tuning/src/sorting/topological_sort.py $sfile $cfile $order
