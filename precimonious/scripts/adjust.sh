#!/bin/bash

sfile=$1
cfile=$2

###################
# parse search file
count=`cat $sfile | grep -n '{"' | wc -l`
count=$((count-1))
ecount=`cat $cfile | grep -n '}}' | wc -l`

if [ $count -ne $ecount ]
then
    echo "Fail to parse \"$sfile\". *$count!=$ecount*"
    exit -1
fi

i=1
while [ $i -le $count ]
do
    index[$i]=$i
    start[$i]=`cat $sfile | grep -n '{"' | cut -d ":" -f 1 | sed -n "$((i+1)) p"` 
    end[$i]=`cat $sfile | grep -n '}}' | cut -d ":" -f 1 | sed -n "$i p"` 
    echo ${index[$i]} : ${start[$i]}, ${end[$i]}
    i=$((i+1))
done

###################
# parse config file
ccount=`cat $cfile | grep -n '{"' | wc -l`
ccount=$((ccount-1))
cecount=`cat $cfile | grep -n '}}' | wc -l`

if [ $ccount -ne $cecount ]
then
    echo "Fail to parse \"$cfile\". *$ccount!=$cecount*"
    exit -1
fi

if [ $ccount -ne $count ]
then
    echo "Fail to parse \"$sfile\" and \"$cfile\". *$ccount!=$count*"
    exit -1
fi

i=1
while [ $i -le $count ]
do
    cstart[$i]=`cat $cfile | grep -n '{"' | cut -d ":" -f 1 | sed -n "$((i+1)) p"` 
    cend[$i]=`cat $cfile | grep -n '}}' | cut -d ":" -f 1 | sed -n "$i p"` 
    echo ${index[$i]} : ${cstart[$i]}, ${cend[$i]}
    i=$((i+1))
done

###############
# sort randomly
i=1
while [ $i -le $count ]
do
    r=$[ $RANDOM % $count ]
    r=$((r+1))
    tmp=${index[$i]}
    index[$i]=${index[$r]}
    index[$r]=$tmp
    i=$((i+1))
done

i=1
while [ $i -le $count ]
do
    echo ${index[$i]}
    i=$((i+1))
done

##############################
#output new-sorted search file
err=`cat $sfile | sed -n "1p" > $sfile.out`
i=1
while [ $i -le $count ]
do
    j=${index[$i]}
    s=${start[$j]}
    e=${end[$j]}
    err=`cat $sfile | sed -n "$s, $((e-1)) p" >> $sfile.out`
    #err=`cat $sfile | sed -n "${end[$i]} p" >> $sfile.out`
    err=`cat $sfile | sed -n "$e p" | sed "s/}}$/}},/" >> $sfile.out`
    #echo $con
    i=$((i+1))
done
last=`cat $sfile | wc -l`
err=`sed -i "$((last-1))s/}},/}}/" $sfile.out`
err=`cat $sfile | sed -n "$last p" >> $sfile.out`

##############################
#output new-sorted config file
err=`cat $cfile | sed -n "1p" > $cfile.out`
i=1
while [ $i -le $count ]
do
    j=${index[$i]}
    s=${cstart[$j]}
    e=${cend[$j]}
    err=`cat $cfile | sed -n "$s, $((e-1)) p" >> $cfile.out`
    #err=`cat $cfile | sed -n "${cend[$i]} p" >> $cfile.out`
    err=`cat $cfile | sed -n "$e p" | sed "s/}}$/}},/" >> $cfile.out`
    #echo $con
    i=$((i+1))
done
last=`cat $cfile | wc -l`
err=`sed -i "$((last-1))s/}},/}}/" $cfile.out`
err=`cat $cfile | sed -n "$last p" >> $cfile.out`
