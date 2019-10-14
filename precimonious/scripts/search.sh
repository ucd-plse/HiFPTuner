#!/bin/bash

# #############################################################
# Shell script to create search file for a given program
# Use: ./search.sh name_of_bc_file
# #############################################################

sharedLib=$CORVETTE_PATH"/src/Passes.so"

arch=`uname -a`
name=${arch:0:6}

if [ "$name" = "Darwin" ]; then
    sharedLib=$CORVETTE_PATH"/src/Passes.dylib"    
fi

varFlags="--only-arrays --only-scalars --funs"

echo "Creating search file search file" search_$1.json
opt -load $sharedLib -search-file --original-type $varFlags $1.bc --filename search_$1.json > $1.tmp

# cleaning up
rm -f $1.tmp
