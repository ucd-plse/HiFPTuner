#!/usr/bin/env python

import types, sys, os, math, json
import transform2, utilities
import community as com
import time

#
# global variables: search counter and community object
#
search_counter = 0
community_obj = []

#
# Check if all vars have been set to the bottom type
#               
def is_bottom_type(change_set):
    for i in range(len(change_set)):
        c = community_obj.get_vars(change_set[i]["name"])
        for j in range(len(c)):
            if len(c[j]["type"]) == 1 and c[j]["type"][0:5] != "float":
                return False
            if len(c[j]["type"]) == 2 and c[j]["type"][0][0:5] != "float":
                return False
    return True
#
# check if we have search through all 
# types in type_set
#
def is_empty(type_set):
    for t in type_set:
        if len(t) > 1:
            return False
    return True

#
# main function receives
#   - argv[1] : bitcode file location
#   - argv[2] : search file location
#   - argv[3] : original config file location
#   - argv[4] : partition config file location
def main():
    search_conf_file = sys.argv[1]
    original_conf_file = sys.argv[2]
    partition_conf_file = sys.argv[3]
    #partition_conf_file = "partition.json"


    #
    # get original config and score 
    #
    original_conf = json.loads(open(original_conf_file, 'r').read())

    #
    # hierarchically type tuning
    #
    partition_tree = json.loads(open(partition_conf_file, 'r').read())
    level = len(partition_tree)-1
    while level>=0:

        search_conf = json.loads(open(search_conf_file, 'r').read())
        change_items = search_conf['config']

        # create communities based on the current level of the partition tree
        global community_obj
        community_obj = com.community(partition_tree, change_items, level)

        if __debug__ :
            fp = open('ivy.log', 'a')
            print>>fp, "----level:", level
            print>>fp, "community configs:"
            print>>fp, "lens:", len(community_obj.confs)
            print>>fp, community_obj.confs
            fp.close()

        level -= 1

if __name__ == "__main__":

    main()

