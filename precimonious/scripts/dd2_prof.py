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
# run bitcode file with the current
# search configuration
# return  1 bitcode file is valid
#         0 bitcode file is invalid
#         -1 some internal transformation error happens
#         -2 some internal transformation error happens
#         -3 some internal transformation error happens
#
def run_config(search_config, original_config, bitcode, timeout):
    if False:
        fp = open('ivy.log', 'a')
        print>>fp, "run config:"
        print>>fp, "search_config:"
        print>>fp, search_config
        fp.close()
    global search_counter
    print "** Exploring configuration #" + str(search_counter)
    utilities.print_config(search_config, "config_temp.json")
    result = transform2.transform(bitcode, "config_temp.json", timeout)
    if result == 1:
        utilities.print_config(search_config, "VALID_config_" + bitcode + "_" + str(search_counter) + ".json")
        utilities.log_config(search_config, "VALID", "log.dd", search_counter)
        utilities.print_diff(search_config, original_config, "dd2_diff_" + bitcode + "_" + str(search_counter) + ".json")
    elif result == 0:
        utilities.print_config(search_config, "INVALID_config_" + bitcode + "_" + str(search_counter) + ".json")
        utilities.log_config(search_config, "INVALID", "log.dd", search_counter)
    elif result == -1:
        utilities.print_config(search_config, "FAIL1_config_" + bitcode + "_" + str(search_counter) + ".json")
        utilities.log_config(search_config, "FAIL1", "log.dd", search_counter)
    elif result == -2:
        utilities.print_config(search_config, "FAIL2_config_" + bitcode + "_" + str(search_counter) + ".json")
        utilities.log_config(search_config, "FAIL2", "log.dd", search_counter)
    elif result == -3:
        utilities.print_config(search_config, "FAIL3_config_" + bitcode + "_" + str(search_counter) + ".json")
        utilities.log_config(search_config, "FAIL3", "log.dd", search_counter)
    else:
        utilities.print_config(search_config, "FAIL4_config_" + bitcode + "_" + str(search_counter) + ".json")
        utilities.log_config(search_config, "FAIL4", "log.dd", search_counter)

    search_counter += 1
    return result

#
# modify change set so that each variable
# maps to its highest type
#
def to_highest_precision(change_set, type_set, switch_set):
    for i in range(len(change_set)):
        c = community_obj.get_vars(change_set[i]["name"])
        t = type_set[i]
        if len(t) > 0:
            type_to_set = t[-1]
            for j in range(len(c)):
                c[j]["type"] = type_to_set
        if len(switch_set) > 0:
            s = switch_set[i]
            if len(s) > 0:
                c[0]["switch"] = s[-1]

#
# modify change set so that each variable
# maps to its 2nd highest type
#
def to_2nd_highest_precision(change_set, type_set, switch_set):
    for i in range(len(change_set)):
        c = community_obj.get_vars(change_set[i]["name"])
        t = type_set[i]
        if len(t) > 1:
            type_to_set = t[-2]
            for j in range(len(c)):
                c[j]["type"] = type_to_set
        if len(switch_set) > 0:
            s = switch_set[i]
            if len(s) > 1:
                c[0]["switch"] = s[-2]
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


def dd_search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, div, original_score):
    #
    # partition change_set into deltas and delta inverses
    #
    delta_change_set = []
    delta_type_set = []
    delta_switch_set = []
    delta_inv_change_set = []
    delta_inv_type_set = []
    delta_inv_switch_set = []
    div_size = int(math.ceil(float(len(change_set))/float(div)))
    for i in xrange(0, len(change_set), div_size):
        delta_change = []
        delta_type = []
        delta_switch = []
        delta_inv_change = []
        delta_inv_type = []
        delta_inv_switch = []
        for j in xrange(0, len(change_set)):
            if j >= i and j < i+div_size:
                delta_change.append(change_set[j])
                delta_type.append(type_set[j])
                delta_switch.append(switch_set[j])
            else:
                delta_inv_change.append(change_set[j])
                delta_inv_type.append(type_set[j])
                delta_inv_switch.append(switch_set[j])
        delta_change_set.append(delta_change)
        delta_type_set.append(delta_type)
        delta_switch_set.append(delta_switch)
        delta_inv_change_set.append(delta_inv_change)
        delta_inv_type_set.append(delta_inv_type)
        delta_inv_switch_set.append(delta_inv_switch)

    #
    # iterate through all delta and inverse delta set
    # record delta set that passes
    #
    pass_inx = -1
    inv_is_better = False
    min_score = -1

    if __debug__ :
        fp = open('ivy.log', 'a')
        print>>fp, "change_set:"
        print>>fp, change_set
        fp.close()
    
    for i in xrange(0, len(delta_change_set)):
        delta_change = delta_change_set[i]
        delta_type = delta_type_set[i]
        delta_switch = delta_switch_set[i]
        if len(delta_change) > 0:
            if __debug__ :
                fp = open('ivy.log', 'a')
                print>>fp, "entering delta running"
                print>>fp, "delta_change:"
                print>>fp, delta_change
                fp.close()
            # always reset to lowest precision
            to_2nd_highest_precision(change_set, type_set, switch_set)
            # apply change for variables in delta
            to_highest_precision(delta_change, delta_type, delta_switch)
            # record i if config passes
            if run_config(search_config, original_config, bitcode, original_score) == 1 and utilities.get_dynamic_score() < original_score:
                score = utilities.get_dynamic_score()
                if score < min_score or min_score == -1:
                    pass_inx = i
                    inv_is_better = False
                    min_score = score

        delta_inv_change = delta_inv_change_set[i]
        delta_inv_type = delta_inv_type_set[i]
        delta_inv_switch = delta_inv_switch_set[i]
        if len(delta_inv_change) > 0 and div > 2:
            if __debug__ :
                fp = open('ivy.log', 'a')
                print>>fp, "entering delta inv running"
                print>>fp, "delta_inv_change:"
                print>>fp, delta_inv_change
                fp.close()
            # always reset to lowest precision
            to_2nd_highest_precision(change_set, type_set, switch_set)
            # apply change for variables in delta inverse
            to_highest_precision(delta_inv_change, delta_inv_type, delta_inv_switch)
            # record i if config passes
            if run_config(search_config, original_config, bitcode, original_score) == 1 and utilities.get_dynamic_score() < original_score:
                score = utilities.get_dynamic_score()
                if score < min_score or min_score == -1:
                    pass_inx = i
                    inv_is_better = True 
                    min_score = score 
    #
    # recursively search in pass delta or pass delta inverse
    # right now keep searching for the first pass delta or
    # pass delta inverse; later on we will integrate cost
    # model here
    #
    if pass_inx != -1:
        pass_change_set = delta_inv_change_set[pass_inx] if inv_is_better else delta_change_set[pass_inx]
        pass_type_set = delta_inv_type_set[pass_inx] if inv_is_better else delta_type_set[pass_inx]
        pass_switch_set = delta_inv_switch_set[pass_inx] if inv_is_better else delta_switch_set[pass_inx]
        if len(pass_change_set) > 1:
            # always reset to lowest precision
            # search for can-be-lowered items among 'pass_change_set'
            to_2nd_highest_precision(change_set, type_set, switch_set)
            dd_search_config(pass_change_set, pass_type_set, pass_switch_set, search_config, original_config, bitcode, 2, original_score)
        else:
            # the 2nd highest precision works for all 
            to_2nd_highest_precision(change_set, type_set, switch_set)
            to_highest_precision(pass_change_set, pass_type_set, pass_switch_set)
        return

    #
    # stop searching when division greater than change set size
    #
    if div >= len(change_set):
        to_highest_precision(change_set, type_set, switch_set)
        return
    else:
        dd_search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, 2*div, original_score)
        return


def search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, original_score):
    
    # search from bottom up
    to_highest_precision(change_set, type_set, switch_set)
    to_2nd_highest_precision(change_set, type_set, switch_set)
    
    if run_config(search_config, original_config, bitcode, original_score) != 1 or utilities.get_dynamic_score() > original_score:
        dd_search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, 2, original_score)
        
    # remove types and switches that cannot be changed
    for i in xrange(0, len(change_set)):
        if len(type_set[i]) > 0 and community_obj.get_vars(change_set[i]["name"])[0]["type"] == type_set[i][-1]:
            del(type_set[i][:])
            if len(switch_set[i]) > 0:
                del(switch_set[i][:])

    # remove highest precision from each type vector
    for i in xrange(0, len(type_set)):
        type_vector = type_set[i]
        switch_vector = switch_set[i]
        if len(type_vector) > 0:
            type_vector.pop()
        if len(switch_vector) > 0:
            switch_vector.pop()

#
# main function receives
#   - argv[1] : bitcode file location
#   - argv[2] : search file location
#   - argv[3] : original config file location
#   - argv[4] : partition config file location
def main():
    bitcode = sys.argv[1]
    search_conf_file = sys.argv[2]
    original_conf_file = sys.argv[3]
    partition_conf_file = sys.argv[4]
    #partition_conf_file = "partition.json"

    #
    # delete log file if exists
    #
    try:
        os.remove("log.dd")
    except OSError:
        pass

    if __debug__ :
        try:
            os.remove("ivy.log")
        except OSError:
            pass
    
    #
    # get original config and score 
    #
    original_conf = json.loads(open(original_conf_file, 'r').read())
    run_config(original_conf, original_conf, bitcode, 0)
    original_score = utilities.get_dynamic_score()
    if __debug__ :
        fp = open('ivy.log', 'a')
        print>>fp, "---------"
        print>>fp, "original score"
        print>>fp, original_score
        fp.close()

    #
    # hierarchically type tuning
    #
    partition_tree = json.loads(open(partition_conf_file, 'r').read())
    curr_conf = None
    curr_score = -1
    level = len(partition_tree)-1
    while level>=0:
        
        if __debug__ :
            fp = open('ivy.log', 'a')
            print>>fp, "partition level and config"
            print>>fp, level, partition_tree[level]
            fp.close()
        
        search_conf = json.loads(open(search_conf_file, 'r').read())
        change_items = search_conf['config']
        
        # delete from the search space the configs that have been pruned 
        if curr_conf != None:
            reach_bottom_label = 1
            for i in range(len(curr_conf['config'])):
                curr_type = curr_conf['config'][i].values()[0]["type"]
                type_vector = change_items[i].values()[0]["type"]
                index = type_vector.index(curr_type)
		if index != 0:
		    reach_bottom_label = 0
                del type_vector[index+1:]
                if change_items[i].keys()[0] == "call":
                    del change_items[i].values()[0]["switch"][index+1:]
	
            if reach_bottom_label == 1:
                break

        # create communities based on the current level of the partition tree
        global community_obj
        community_obj = com.community(partition_tree, change_items, level)

        if __debug__ :
            fp = open('ivy.log', 'a')
            print>>fp, "community configs:"
            print>>fp, community_obj.confs
            fp.close()
        
        #
        # record the change set
        #
        search_changes = community_obj.confs
        change_set = []
        type_set = []
        switch_set = []
        for i in range(len(search_changes)):
            type_vector = search_changes[i]["type"]
            if isinstance(type_vector, list):
                if len(type_vector) == 1:
                    tmp_set=[]
                    tmp_type_set=[]
                    tmp_switch_set=[]
                    tmp_set.append(search_changes[i])
                    tmp_type_set.append(type_vector)
                    if "switch" in community_obj.get_vars(search_changes[i]["name"])[0].keys():
                        tmp_switch_set.append(community_obj.get_vars(search_changes[i]["name"])[0]["switch"])
                    else:
                        tmp_switch_set.append([])
                    to_highest_precision(tmp_set, tmp_type_set, tmp_switch_set)
                else:
                    type_set.append(type_vector)
                    change_set.append(search_changes[i])

                    if (len(community_obj.get_vars(search_changes[i]["name"])) == 1) & ("switch" in community_obj.get_vars(search_changes[i]["name"])[0].keys()):
                        switch_set.append(community_obj.get_vars(search_changes[i]["name"])[0]["switch"])
                    else:
                        switch_set.append([])
        
        #
        # search for valid configuration
        #
        print "Searching for valid configuration using delta-debugging algorithm ..."
        
        # get current score
        if curr_score == -1:
            curr_score = original_score ## 0.95
            curr_conf = original_conf

        # keep searching while the type set is not searched throughout
        while not is_empty(type_set):
            search_config(change_set, type_set, switch_set, search_conf, original_conf, bitcode, original_score)

        # get the score of modified program
        run_config(search_conf, original_conf, bitcode, 0)
        modified_score = utilities.get_dynamic_score()
        if modified_score <= curr_score:
            curr_conf = search_conf
            curr_score = modified_score
            if __debug__ :
                fp = open('ivy.log', 'a')
                print>>fp, "---------"
                print>>fp, "updating new score"
                print>>fp, curr_score
                fp.close()

        # print the intermediate level configuration     
        utilities.print_config(curr_conf, "dd2_valid_level" + str(level) + "_" + bitcode + ".json")
        fleveline = open("log.dd", "a")
        fleveline.write("----------------------------------------------------------------------\n")
        fleveline.close()

        
        # check the modified configuration
        '''
        if is_bottom_type(change_set):
            if __debug__ :
                fp = open('ivy.log', 'a')
                print>>fp, "stop searching : reach bottom types"
                print>>fp, search_conf
                print>>fp, "change set:"
                print>>fp, change_set
                fp.close()
            break
        '''
        
        level -= 1

    # print tuning result    
    if (curr_score <= original_score) & (curr_conf != None):
        #print valid configuration file and diff file
        diff = utilities.print_diff(curr_conf, original_conf, "dd2_diff_" + bitcode + ".json")
        if diff:
            utilities.print_config(curr_conf, "dd2_valid_" + bitcode + ".json")
            print "original_score: ", original_score
            print "modified_score: ", curr_score
            fp = open('time.txt', 'a')
            print>>fp, curr_score, "/", original_score
            fp.close()
            print "Check valid_" + bitcode + ".json for the valid configuration file"
            return
        
    print "No configuration is found!"
    
if __name__ == "__main__":
    fp = open('time.txt', 'w')
    fp.write("Started...\n")
    fp.close()
    start = time.time()
    main()
    end = time.time()
    elapsed = end - start
    print "\n Elapsed time : "+str(elapsed)+"secs\n"
    fp = open('time.txt', 'a')
    fp.write("Elapsed time : %.6f secs" % (elapsed))
    fp.close()
