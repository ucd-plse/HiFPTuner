import json, sys

class part_conf:
    def find_local(self, fun, var, var_items):
        for i in range(len(var_items)):
            if var_items[i].has_key("localVar"):
                if (var_items[i]["localVar"]["function"] == fun) & (var_items[i]["localVar"]["name"] == var):
                    return i
        return -1

    def find_global(self, var, var_items):
        for i in range(len(var_items)):
            if var_items[i].has_key("globalVar"):
                if var_items[i]["globalVar"]["name"] == var :
                    return i
        return -1

    def common_type(self, varlist, var_items):
        index = varlist[0]
        tylist = var_items[index].values()[0]["type"]
        '''
        to_del = []
        for i in range(len(tylist)):
            for j in range(1, len(varlist)):
                index_cmp = varlist[j]
                tylist_cmp = var_items[index_cmp].values()[0]["type"]
                if tylist[i] not in tylist_cmp:
                    to_del.append(i)
                    break
        for i in range(len(to_del)):
            d = do_del[i] - i
            del tylist[d]
        '''
        return tylist

    def type_identical(self, var1, var2, var_items):
        ty1 = var_items[var1].values()[0]["type"]
        ty2 = var_items[var2].values()[0]["type"]
                    
        if len(ty1) != len(ty2):
            return False
        for i in range(len(ty1)):
            if ty1[i] != ty2[i]:
                return False
        
        return True
    
    def type_grouping(self, varlist, var_items):
        tp_groups = []
        
        while len(varlist)>0:
            tp_group=[]
            tp_group.append(varlist[0])
            varlist.remove(tp_group[0])
            for var in varlist:
                if self.type_identical(var, tp_group[0], var_items):
                    tp_group.append(var)
            for i in range(1, len(tp_group)):
                varlist.remove(tp_group[i])
                    
            tp_groups.append(tp_group)

        if len(tp_groups)==0:
            tp_groups.append([])
        
        return tp_groups
    
    def configure(self, var_items, level):
        part_at_level = self.part_tree[level]
        for com in set(part_at_level.values()):
            list_nodes = [nodes for nodes in part_at_level.keys() if part_at_level[nodes] == com]
            #print com, list_nodes
            name = "Com"*level+"Community"+str(com)
            vars = []
            for i in range(len(list_nodes)):
                #print i, list_nodes[i]
                node_items = list_nodes[i].split('.')
                if (len(node_items) == 2):
                    fun = node_items[0]
                    var = node_items[1]
                    i = self.find_local(fun, var, var_items)
                    if i!= -1:
                        vars.append(i)
                if (len(node_items) == 1):
                    var = node_items[0]
                    i = self.find_global(var, var_items)
                    if i!= -1:
                        vars.append(i)

            if len(vars) != 0:
                tp_groups = self.type_grouping(vars, var_items)
                for i in range(len(tp_groups)):
                    conf = {}
                    conf["vars"] = tp_groups[i]
                    conf["type"] = self.common_type(tp_groups[i], var_items)
                    name_i = name + "_" + str(i)
                    self.confs[name_i] = conf
                    self.catalog.append(name_i)
        self.level = level
            
    def __init__(self, partition_conf, var_items, level):
        self.part_tree = partition_conf
        self.var_items = var_items
        #level_max = len(partition_conf)-1
        self.catalog = []
        self.confs = {}
        self.configure(var_items, level)
        
    def print_confs(self):
        print self.confs

    def get_vars(self, part_name):
        dlist = self.confs[part_name]["vars"]
        vars = []
        for i in dlist:
            vars.append(self.var_items[i].values()[0])
        return vars
    
class community:
    def __init__(self, partition_tree, var_items, level):
        self.partition = part_conf(partition_tree, var_items, level)
        self.var_items = var_items
        self.confs = []
        varlist = []
        for part in self.partition.catalog:
            config = {}
            config["name"] = part
            config["type"] = self.partition.confs[part]["type"]
            self.confs.append(config)
            varlist += self.partition.confs[part]["vars"]
        if __debug__ :
            fp = open('ivy.log', 'a')
            print>>fp, "Community Construction"
            print>>fp, self.confs
            print>>fp, varlist
            fp.close()
        
        for i in range(len(var_items)):
            if i not in varlist:
                config = {}
                config["name"] = str(i)
                config["type"] = var_items[i].values()[0]["type"]
                self.confs.append(config)

    def print_confs(self):
        print self.confs
        print self.partition.print_confs()

    def get_vars(self, name):
        #name = self.confs[index]["name"]
        vars = []
        if "Community" in name:
            vars += self.partition.get_vars(name)
        else:
            vars.append(self.var_items[long(name)].values()[0])
        return vars

