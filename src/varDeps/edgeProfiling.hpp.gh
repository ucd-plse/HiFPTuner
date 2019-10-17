#ifndef EDGE_PROFILING_GUARD
#define EDGE_PROFILING_GUARD 1

#include <llvm/Pass.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/BasicBlock.h>
#include <list>
#include <map>
#include <utility>

#include <json/json.h>

using namespace std;
using namespace llvm;
/*******************************************************
* Pass Name:    edge-profiling 
*
* This pass instruments the program and profiles the edges 
* gained from the varDep-analysis pass. 
*
* Output: instrumented code for varDep edge profiling
*         edgeProfilingOut.json
*******************************************************/
#define profOutFile "edgeProfilingOut.json"

class edgeProf : public ModulePass {
  
public:
    edgeProf() : ModulePass(ID) {}
  
    virtual bool runOnModule(Module &M);
    //virtual bool runOnFunction(Function &F);  
    virtual void getAnalysisUsage(AnalysisUsage &AU) const;

    void InsertProfilingInitCall(Module& M, Function* MainFn);
    void InsertProfilingFinalCall(Module& M, Function* MainFn);
    void instrument_edge(Function* fp, list< pair<Instruction*, Instruction*> > deppairs);
    void printProf();
    
    static char ID; // Pass identification, replacement for typeid

private:
    map< Function*, list< pair<Instruction*, Instruction*> > > varDepGraph;
    //map< string, list< unsigned long long int > > edgecounts;
    /* for intrumenting edges */
    //map< Function*, map< BasicBlock*, int> > instrumentedEdges;
    //int counters;
    Json::Value root;
};

#endif
