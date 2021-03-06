#!/usr/bin/python

##########################################################
# Graph Analysis with profiling info.
#
#          Input file: VarDepPairs_pro.json
#                      edgeProfilingOut.json
#
#         outPut file: varDepGraph_pro.png
#                      partition.json (grouping)
#                      sorted_partition.json (grouping + sorting)
#                      topolOrder_pro.json (sorting)
#                      
##########################################################
import sys, getopt
import matplotlib.pyplot as plt
import networkx as nx
import json
import community as com
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_agraph import to_agraph
from networkx.drawing.nx_agraph import write_dot

part_para = 1
wfilter = 1

def getData(graphfile="varDepPairs_pro.json", profile="edgeProfilingOut.json"):
    with open(graphfile) as gdata_f, open(profile) as pdata_f:
        fgdata = gdata_f.read()
        gdata = json.loads(fgdata)
        fpdata = pdata_f.read()
        pdata = json.loads(fpdata)
        return gdata, pdata
    print "Input files:varDepPairs_pro.json and edgeProfilingOut.json not found!"
    return -1, -1

def createGraph(gdata, pdata):
    G=nx.DiGraph()
    funcs=gdata["Catalog"]
    for i in range(len(funcs)):
        #print funcs[i]
        func=funcs[i]
        graph=gdata["Content"]
        for i in range(len(graph[func])):
            ld = graph[func][i][0]
            st = graph[func][i][1]
            #ignore unkown variables
            if (ld[-1]=='.' or st[-1]=='.'):
                continue
            #wt = long(pdata[func][i])
            wtstr = pdata[func][i]
            if type(wtstr)==int:
                wtstr=str(wtstr)
            if "INDEX" in wtstr:
                index=long(pdata[func][i][5:])
                wt = long(pdata[func][index])
                #print pdata[func][i], index, wt
            else:
                wt = long(pdata[func][i])

            if G.has_edge(ld, st):
                G[ld][st]['weight']+=wt
            else:
                G.add_edge(ld, st, weight=wt)

    global wfilter
    for (u, v, d) in G.edges(data=True):
        if d['weight'] < wfilter:
            G.remove_edge(u, v)
    return G

def pgv_saveGraph(G):
    for (u, v, d) in G.edges(data=True):
        d['label'] = d['weight']
        #print u, v, d['weight']
    A = to_agraph(G)
    write_dot(G, "mydot.dot")
    #A.layout(prog='dot')
    #A.draw("varDepGraph_pro.png")
    #print "  Check Image\"varDepGraph_pro.png\"."

def plt_showGraph(G):
    pos=nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.axis('off')
    plt.savefig("varDepGraph_pro.png")
    print "  Check Image\"varDepGraph_pro.png\"."
    plt.show()

def example():
    G=nx.DiGraph()
    G.add_edge("Node3", "Node2", weight=200)
    G.add_edge("Node2", "Node1", weight=2)
    G.add_edge("Node1", "Node3", weight=500)
    G.add_edge("Node1", "Node4", weight=200)
    G.add_edge("Node4", "Node2", weight=500)
    #print(G.nodes())
    #print(G.edges())
    #plt_showGraph(G)
    return G

def test_main():
    example()

def handleCycles(G):
    cycles = list(nx.simple_cycles(G))
    for i in range(len(cycles)):
        #print len(cycles[i]), cycles[i]
        # remove self-loops
        if len(cycles[i]) == 1:
            G.remove_edge(cycles[i][0], cycles[i][0])
    cycles = list(nx.simple_cycles(G))
    for i in range(len(cycles)):
        #print "cycle: ", cycles[i]
        
        if not G.has_edge(cycles[i][0], cycles[i][1]):
            continue
            
        to_del=True
        edge_to_del=0
        edge_to_del_weight=G[cycles[i][0]][cycles[i][1]]['weight']
        for j in range(1, len(cycles[i])):
            if not G.has_edge(cycles[i][j], cycles[i][(j+1)%len(cycles[i])]):
                to_del=False
                break
            if G[cycles[i][j]][cycles[i][(j+1)%len(cycles[i])]]['weight'] < edge_to_del_weight:
                edge_to_del=j
                edge_to_del_weight=G[cycles[i][j]][cycles[i][(j+1)%len(cycles[i])]]['weight']
        if to_del:
            G.remove_edge(cycles[i][edge_to_del], cycles[i][(edge_to_del+1)%len(cycles[i])])
            #print "remove: ", cycles[i][edge_to_del], cycles[i][(edge_to_del+1)%len(cycles[i])]

def topolOrder(G):
    topol = nx.topological_sort(G)
    return list(topol)

def sort_partition(G, dendo):
    curr_G = G
    pdendo = []
    sort = {}
    for i in range(len(dendo)):
        #part = com.partition_at_level(dendo, i)
        dendo_part = dendo[i]
        part = {}
        for i in (dendo_part.keys()):
            if len(sort) == 0:
                part[str(i)] = dendo_part[i]
            else:
                part[sort[str(i)]] = dendo_part[i]

        #print i, part
        new_G = nx.DiGraph()
        groups = set(part.values())
        for i in groups:
            new_G.add_node(str(i))
        for (u, v, d) in curr_G.edges(data=True):
            new_u = str(part[str(u)])
            new_v = str(part[str(v)])
            if new_u != new_v :
                #print new_u, new_v
                new_G.add_edge(new_u, new_v, weight=d['weight'])
                
        tmp_G = new_G
            
        if not(nx.is_directed_acyclic_graph(new_G)):
            handleCycles(new_G)
        if nx.is_directed_acyclic_graph(new_G):
            topol = topolOrder(new_G)
            
            #create a sorting dict.
            sort = {}
            for i in range(len(topol)):
                sort[topol[i]] = str(i)
                
            #sort the partition    
            for i in curr_G.nodes():
                #print part[i], sort[str(part[i])]
                part[i] = long(sort[str(part[i])])

            #adjust the keys
            for i in part.keys():
                if not i.isdigit():
                    break
                v = part[i]
                del part[i]
                part[long(i)] = v
                
            pdendo.append(part)
            
            # relabel the graph built for queries of next partition
            H=nx.relabel_nodes(tmp_G, sort)

            '''
            for i in H.edges():
                print i
            print "----------"
            print sort
            print "----------"
            for j in tmp_G.edges():
                print j
            '''
            
            tmp_G = H
            
        curr_G = tmp_G
        
    return pdendo

def partition(G):
    undirected_G = G.to_undirected()    
    dendo = com.generate_dendrogram(undirected_G, None, weight='weight', resolution=part_para)
    pdendo = []
    for i in range(len(dendo)):
        pdendo.append(com.partition_at_level(dendo, i))
        #print i, com.partition_at_level(dendo, i)
    outfile = open("partition.json", "w+")
    json.dump(pdendo, outfile)
    print "  Check File\"partition.json\" for the partition tree."
    sdendo = sort_partition(G, dendo)
    outfile = open("sorted_partition.json", "w+")
    pdendo = []
    for i in range(len(sdendo)):
        pdendo.append(com.partition_at_level(sdendo, i))
    json.dump(pdendo, outfile)
    print "  Check File\"sorted_partition.json\" for the sorted partition tree."
    return len(dendo)
    
def print_help():
    print 'varDepGraph [-h]'
    print "Graph Analysis with profiling info."
    print "         Input file: VarDepPairs_pro.json"
    print "                     edgeProfilingOut.json"
    print "         outPut file: varDepGraph_pro.png"
    print "                      topolOrder_pro.json(sorting)"
    print "                      partition.json(grouping)"
    print "                      sorted_partition.json(grouping + sorting)"
    
def main(argv):
    ##Processing Options
    try:
        opts, args = getopt.getopt(argv, "h")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "option: -h"
            print_help()
            sys.exit()
        else:
            print_help()
            sys.exit()

    global part_para
    if len(sys.argv) > 1:
        part_para = float(sys.argv[1])

    global wfilter
    if len(sys.argv) > 2:
        wfilter = long(sys.argv[2])

    print "community parameter: ", part_para
    
    print "\nDependence Graph Analysis:\n"
    gdata, pdata = getData()
    if gdata==-1:
        print "Error."
        return
    #G = example()
    G = createGraph(gdata, pdata)
    pgv_saveGraph(G)
    partition(G)


    if not(nx.is_directed_acyclic_graph(G)):
        handleCycles(G)
    if nx.is_directed_acyclic_graph(G):
        topol = topolOrder(G)
        outfile = open("topolOrder_pro.json", "w+")
        json.dump(topol, outfile)
        print "  Check File\"topolOrder_pro.json\" for the topological sorting result."
    else:
        print "  Cycles exist in the dependence graph."

if __name__ == "__main__":
    main(sys.argv[1:])
