#!/usr/bin/env python

import types, sys, os, math, json
import transform2, utilities
import time,random

#
# global search counter
#
search_counter = 0

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
  global search_counter
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
  for i in range(0, len(change_set)):
    c = change_set[i]
    t = type_set[i]
    if len(t) > 0:
      c["type"] = t[-1]
    if len(switch_set) > 0:
      s = switch_set[i]
      if len(s) > 0:
        c["switch"] = s[-1]


#
# modify change set so that each variable
# maps to a random precision type
#
def to_random_precision(change_set, type_set, switch_set):
  for i in range(0, len(change_set)):
    c = change_set[i]
    t = type_set[i]
    index = -1
    if len(t) > 0:
      index = random.randint(0, len(t)-1)
      c["type"] = t[index]
    if len(switch_set) > 0:
      s = switch_set[i]
      if len(s) > 0:
        c["switch"] = s[index]

#
# modify change set so that a random set of variables
# lowers down to their 2nd highest precision types
#
def randomly_to_2nd_highest_precision(change_set, type_set, switch_set, initial_change_set):
  changed_flag=False
  for i in range(0, len(change_set)):
    curr_type = initial_change_set[i]
    c = change_set[i]
    t = type_set[i]
    cur_index=0
    if len(t) > 0:
      for j in range(1, len(t)):
        if curr_type == t[j]:
          cur_index=j
    if cur_index==0:
      continue

    changed_flag=True

    if random.randint(0,1)==1:
      index=cur_index-1
    else:
      index=cur_index

    c["type"]=t[index]
    if len(switch_set) > 0:
      s = switch_set[i]
      if len(s) > 0:
        c["switch"] = s[index]
    
  return changed_flag

#
# check if we have search through all 
# types in type_set
#
def is_empty(type_set):
  for t in type_set:
    if len(t) > 1:
      return False
  return True

def random_local_search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, div, initial_score, count):
  opt_score=initial_score
  initial_change_set=[]
  for i in range(len(change_set)):
    initial_change_set.append(change_set[i]["type"])
  #print initial_change_set
  #exit()
  while(count>0):
    lower=False
    while(not lower):
        lower = randomly_to_2nd_highest_precision(change_set, type_set, switch_set, initial_change_set)
        count=count-1
    if run_config(search_config, original_config, bitcode, initial_score) == 1 and utilities.get_dynamic_score() <= opt_score:
      opt_score = utilities.get_dynamic_score()
      initial_change_set=[]
      for i in range(len(change_set)):
        initial_change_set.append(change_set[i]["type"])
      utilities.print_config(search_config, "final_config_from_random_search.json")
      fp = open('log.dd', 'a')
      fp.write(".......................................\n")
      fp.close()
  return opt_score

def random_search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, original_score, total_count):
  utilities.print_config(search_config, "final_config_from_random_search.json")
  
  count=total_count
  opt_score=original_score
  while(count>0):
    # search starts with a random initial config
    to_random_precision(change_set, type_set, switch_set)
    count=count-1
    if run_config(search_config, original_config, bitcode, opt_score) == 1 and utilities.get_dynamic_score() <= opt_score:
      initial_score = utilities.get_dynamic_score()
      utilities.print_config(search_config, "final_config_from_random_search.json")
      fp = open('log.dd', 'a')
      fp.write("START local search <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
      fp.close()
      random_count=random.randint(0, count)
      if random_count>0:
        opt_score=random_local_search_config(change_set, type_set, switch_set, search_config, original_config, bitcode, 2, initial_score, random_count)
      count=count-random_count
      fp = open('log.dd', 'a')
      fp.write("END local search >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
      fp.close()


#
# main function receives
#   - argv[1] : bitcode file location
#   - argv[2] : search file location
#   - argv[3] : original config file location

def main():
  bitcode = sys.argv[1]
  search_conf_file = sys.argv[2]
  original_conf_file = sys.argv[3]

  if len(sys.argv)>4:
    total_count = int(sys.argv[4])
  else:
    total_count = 1000

  #
  # delete log file if exists
  #
  try:
    os.remove("log.dd")
  except OSError:
    pass

  #
  # get configs and the topological order
  #
  search_conf = json.loads(open(search_conf_file, 'r').read())
  original_conf = json.loads(open(original_conf_file, 'r').read())
  

  #
  # parsing config files
  #
  search_changes = search_conf["config"]
  change_set = []
  type_set = []
  switch_set = []

  #
  # record the change set
  #
  for search_change in search_changes:
    type_vector = search_change.values()[0]["type"]
    if isinstance(type_vector, list):
      type_set.append(type_vector)
      change_set.append(search_change.values()[0])
    if search_change.keys()[0] == "call": 
      switch_set.append(search_change.values()[0]["switch"])
    else:
      switch_set.append([])

  #
  # search for valid configuration
  #
  print "Searching for valid configuration using delta-debugging algorithm ..."

  # get original score
  to_highest_precision(change_set, type_set, switch_set)
  run_config(search_conf, original_conf, bitcode, 0)
  original_score = utilities.get_dynamic_score() ## 0.95

  # keep searching while the type set is not searched throughout
  if not is_empty(type_set):
    random_search_config(change_set, type_set, switch_set, search_conf, original_conf, bitcode, original_score, total_count)

  # get the score of modified program
  cmd="sed -i -e '1s/{/{\"config\": [/' -e 's/\"localVar/{\"localVar/' -e 's/\"call/{\"call/' -e 's/},/}},/' -e 's/\"name\(.*\),/\"name\\1/' final_config_from_random_search.json"
  os.system(cmd)
  os.system("tac <final_config_from_random_search.json | sed -e '2s/},/}/' -e '1s/}/]}/' | tac >tmp_final_config_from_random_search.json")
  os.system("mv tmp_final_config_from_random_search.json final_config_from_random_search.json")
  search_conf = json.loads(open("final_config_from_random_search.json", 'r').read())
  run_config(search_conf, original_conf, bitcode, 0)
  modified_score = utilities.get_dynamic_score()

  if modified_score <= original_score:
    # print valid configuration file and diff file
    utilities.print_config(search_conf, "dd2_valid_" + bitcode + ".json")
    diff = utilities.print_diff(search_conf, original_conf, "dd2_diff_" + bitcode + ".json")
    if diff:
      print "original_score: ", original_score
      print "modified_score: ", modified_score
      fp = open('time.txt', 'a')
      print>>fp, modified_score, "/", original_score
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
