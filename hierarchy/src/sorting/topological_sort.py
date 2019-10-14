import sys
import json

#searchfile = "search.json"
#configfile = "config.json"
#tfile = "topolOrder.json"
def find(srclist, a):
    if (a.has_key("localVar")):
        localv = a["localVar"]
        for i in range(len(srclist)):
            items = srclist[i].split('.')
            #print i, items
            if (len(items) == 2):
                fun = items[0]
                var = items[1]
                #print fun, var, localv["function"], localv["name"]
                if ((localv["function"] == fun) & (localv["name"] == var)):
                    #print fun, var, localv["function"], localv["name"], i
                    return i
        return -1
    
    if (a.has_key("globalVar")):
        globalv = a["globalVar"]
        for i in range(len(srclist)):
            items = srclist[i].split('.')
            if (len(items) == 1):
                var = items[0]
                if (localv["name"] == var):
                    return i
        return -1
    
    return -1

def sort(search_conf, ori_conf, t_order):
    search_items = search_conf["config"]
    ori_items = ori_conf["config"]
    pairs = []
    src = []
    des = []

    for i in range(len(search_items)):
        j = find(t_order, search_items[i])
        if (j != -1):
            pairs.append((i, j))
            src.append(i)
            des.append(j)      
   
    des.sort() 
    pos = {}
    for i in range(len(des)):        
        pos[des[i]] = src[i]

    new_search_items = []
    new_ori_items = []
    for i in range(len(search_items)):
        new_search_items.append(search_items[i])
        new_ori_items.append(ori_items[i])

    for i in range(len(pairs)):
        index = pairs[i][0]
        new_index = pos[pairs[i][1]]
        new_search_items[new_index] = search_items[index]
        new_ori_items[new_index] = ori_items[index]

    #for i in range(len(new_search_items)):
    #    print new_search_items[i]["localVar"]["function"], new_search_items[i]["localVar"]["name"]

    search_conf["config"] = new_search_items
    ori_conf["config"] = new_ori_items

def main():
    searchfile = sys.argv[1]
    configfile = sys.argv[2]
    tfile = sys.argv[3]

    search_conf = json.loads(open(searchfile, 'r').read())
    ori_conf = json.loads(open(configfile, 'r').read())
    t_order = json.loads(open(tfile, 'r').read())

    sort(search_conf, ori_conf, t_order)


    sortedsearchfile = "sorted_" + searchfile
    sortedconfigfile = "sorted_" + configfile    
    open(sortedsearchfile, 'w+').write(json.dumps(search_conf, indent=4, separators=(',', ':')))
    open(sortedconfigfile, 'w+').write(json.dumps(ori_conf, indent=4, separators=(',', ':')))

if __name__ == "__main__":
    main()
