#!/usr/bin/python

##########################################################
# Graph Analysis.
#
#          Input file: VarDepPairs.json
#
#         outPut file: varDepGraph.png
#                      topolOrder.json(optional) [-s]                   
##########################################################

import sys, getopt
import matplotlib.pyplot as plt
import networkx as nx
import json
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_agraph import to_agraph

opt_print = 0
opt_sort = 1

def getData(filename="varDepPairs.json"):
    with open(filename) as data_f:
        fdata = data_f.read()
        data = json.loads(fdata)
    return data

def createGraph(data):
    G=nx.DiGraph()
    for i in range(len(data)):
        ld = data[i][0]
        st = data[i][1] 
        G.add_edge(ld, st)
        if opt_sort==1:
            if not(nx.is_directed_acyclic_graph(G)):
                G.remove_edge(ld, st);
    return G

def pgv_saveGraph(G):
    A = to_agraph(G);
    A.layout(prog='dot')
    A.draw("varDepGraph.png")
    print "  Check Image\"varDepGraph.png\"."


def plt_showGraph(G):
    pos=nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    plt.axis('off')
    plt.savefig("varDepGraph.png")
    print "  Check Image\"varDepGraph.png\"."
    plt.show()

def example():
    G=nx.Graph()
    G.add_node("spam")
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge("sp", "am")
    G.add_edge("spam", "s")
    G.add_edge("spam", "sp")
    print(G.nodes())
    print(G.edges())
    showGraph(G)

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
        print "cycle: ", cycles[i]
        pass

def topolOrder(G):
    topol = nx.topological_sort(G)
    outfile = open("topolOrder.json", "w+")
    json.dump(topol, outfile)
    print "  Check File\"topolOrder.json\" for the topological sorting result."

def print_help():
    print 'varDepGraph [-h/-p/-s]'
    print ' -h : help'
    print ' -p : print the dependence graph'
    print ' -s : sort the varaibles as in the dependence topological order'

def main(argv):
    ##Processing Options
    try:
        opts, args = getopt.getopt(argv, "hps")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    global opt_print
    global opt_sort
    for opt, arg in opts:
        if opt == '-h':
            print "option: -h"
            print_help()
            sys.exit()
        elif opt in ("-p"):
            print "option: -p"
            opt_print = 1
            opt_sort = 0
        elif opt in ("-s"):
            print "option: -s"
            opt_sort = 1
            opt_print = 0
        else:
            print_help()
            sys.exit()

    print "\nDependence Graph Analysis:\n"
    data = getData()
    G = createGraph(data)
    pgv_saveGraph(G)
    if opt_sort==1:
        topolOrder(G)


    #if not(nx.is_directed_acyclic_graph(G)):
    #    handleCycles(G)
    #if nx.is_directed_acyclic_graph(G):
    #    topolOrder(G)
    #else:
    #    print "  Cycles exist in the dependence graph."

if __name__ == "__main__":
    main(sys.argv[1:])
