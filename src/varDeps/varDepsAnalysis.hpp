#ifndef VAR_DEPS_ANALYSIS_GUARD
#define VAR_DEPS_ANALYSIS_GUARD 1

#include <llvm/Pass.h>
#include <llvm/IR/Instructions.h>
#include <list>
#include <map>
#include <utility>

using namespace std;
using namespace llvm;
/*******************************************************
* Pass Name:    varDeps-analysis 
*
* This pass aims to obtain the data dependece graph among
* floating-point scalar variables. This analysis is context
* insensitive.  
*
* Output: varDepGraph
*******************************************************/
class varDeps : public ModulePass {
  
public:
    varDeps() : ModulePass(ID) {}
  
    virtual bool runOnModule(Module &M);
    virtual bool runOnFunction(Function &F);  
    virtual void getAnalysisUsage(AnalysisUsage &AU) const;

    map< Function*, list< pair<Instruction*, Instruction*> > > getVarDepGraph(){return varDepGraph;}
    void printVarDepGraph();

    static char ID; // Pass identification, replacement for typeid

private:
    map< Function*, list< pair<Instruction*, Instruction*> > > varDepGraph;
};

#endif // VAR_DEPS_ANALYSIS_GUARD
