BcFilePrefix=$1
ScriptPath=$CORVETTE_PATH"/scripts"

##############################
#create search and config files
sfile=search_$BcFilePrefix.json
cfile=config_$BcFilePrefix.json

if [ -e $sfile.ori ] && [ -e $cfile.ori ]
then
    cp $sfile.ori $sfile
    cp $cfile.ori $cfile
else
    $ScriptPath/search.sh $BcFilePrefix .
    $ScriptPath/config.sh $BcFilePrefix .
    cp $sfile $sfile.ori
    cp $cfile $cfile.ori
fi

##########################################################################
#create "count" number of search files with different orders of variables
#, and run Precimonious on these search files respectively
count=5
i=0
while [ $i -le $count ]
do 
    #init log
    echo 0 >$BcFilePrefix-runtimes
   
    #adjust the order of variables in search and config files 
    if [ $i -ne 0 ]
    then
        $ScriptPath/adjust.sh $sfile $cfile
        mv $sfile.out $sfile
        mv $cfile.out $cfile
    fi

    cp $sfile $i-$sfile
    cp $cfile $i-$cfile

    #run
    $ScriptPath/dd2.py $BcFilePrefix.bc $sfile $cfile

    #save the results
    mv dd2_valid_$BcFilePrefix.bc.json  $i-dd2_valid_$BcFilePrefix.bc.json 
    mv dd2_diff_$BcFilePrefix.bc.json  $i-dd2_diff_$BcFilePrefix.bc.json
    #mv $BcFilePrefix-runtimes $i-$BcFilePrefix-runtimes
    mv log.dd $i-log.dd
    mv time.txt $i-time.txt

    #clear temp files
    rm VALID* INVALID* dd2_* temp* 2> /dev/null

    #increase the index
    i=$((i+1))
done
