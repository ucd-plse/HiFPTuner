#!/bin/bash

sfile=$1

cat $sfile | grep "SPEEDUP" >tmp_content

count=0
s=0
while read line; do
    echo $line
    count=$((count+1)) 
    si=`echo $line | sed "s/.*SPEEDUP = \(.*\) SPEEDUP2.*/\1/"`
    echo $si
    s=$(echo $s+$si | bc)       
done <tmp_content

s=$(echo "scale=7; $s/$count" | bc)
echo $s%
