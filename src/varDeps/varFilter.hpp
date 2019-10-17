#ifndef VAR_FILTER_GUARD
#define VAR_FILTER_GUARD 1

#include <llvm/Pass.h>
#include <llvm/IR/Instructions.h>
#include <list>
#include <map>
#include <utility>

using namespace std;
using namespace llvm;
/*******************************************************
* Pass Name:    varFilter
*
* Output: varDepGraph
*******************************************************/
#define varDepOutFile_filter "varDepPairs.json"

class varFilters : public ModulePass {
  
public:
    varFilters() : ModulePass(ID) {}
  
    virtual bool runOnModule(Module &M);
    virtual void getAnalysisUsage(AnalysisUsage &AU) const;

    void filters(Function* fp, list< pair<Instruction*, Instruction*> > &depparis);
    map< Function*, list< pair<Instruction*, Instruction*> > > getVarDepGraph(){return varDepGraph;}
    void printVarDepGraph();
    void printDepPairs2Json();

    static char ID; // Pass identification, replacement for typeid

private:
    map< Function*, list< pair<Instruction*, Instruction*> > > varDepGraph;
    list< pair<StringRef, StringRef> >  vDepGraph;
};

#endif // VAR_FILTER_GUARD
