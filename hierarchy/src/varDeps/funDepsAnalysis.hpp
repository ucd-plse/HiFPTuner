#ifndef FUN_DEPS_ANALYSIS_GUARD
#define FUN_DEPS_ANALYSIS_GUARD 1

#include <llvm/Pass.h>
#include <llvm/IR/Instructions.h>
#include <llvm/Support/raw_ostream.h>
#include <vector>
#include <map>
#include <set>
#include <utility>

using namespace std;
using namespace llvm;
/*******************************************************
* Pass Name:    funDeps-analysis 
*
* This pass aims to obtain the dependence graph among
* functions.  
*
* Output: funDepGraph
*******************************************************/
class callinfo {
public:
    callinfo(){ret = callee = "";}
    void printCallInfo(){
      errs() << "    <callee:" << callee <<",  args:";
        for(set<StringRef>::iterator it = args.begin(); it != args.end(); it++){
            errs() << *it << " ";
        }
        errs() << " ret:" << ret << ">\n";
    }    
    StringRef callee;
    set<StringRef> args;
    StringRef ret;
  
};

class funDeps : public ModulePass {
  
public:
    funDeps() : ModulePass(ID) {}
  
    virtual bool runOnModule(Module &M);
    virtual bool runOnFunction(Function &F);  
    virtual void getAnalysisUsage(AnalysisUsage &AU) const;

    set< pair<StringRef, StringRef> > getFunDepGraph(){return funDepGraph;}
    void printFunDepGraph();
    void printCalls();

    static char ID; // Pass identification, replacement for typeid

private:
    set< pair<StringRef, StringRef> >  funDepGraph;
    map<StringRef, vector<callinfo> > calls;
};

#endif // FUN_DEPS_ANALYSIS_GUARD
