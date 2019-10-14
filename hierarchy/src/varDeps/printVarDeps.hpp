#ifndef PRINT_VAR_DEPS_GUARD
#define PRINT_VAR_DEPS_GUARD 1

#include <llvm/Pass.h>
#include <llvm/IR/Instructions.h>
#include <list>
#include <map>
#include <utility>

using namespace std;
using namespace llvm;
/*******************************************************
* Pass Name:    printVarDeps
*
* Output: varDepPairs.json
*******************************************************/
#define varDepOutFile_print "varDepPairs_pro.json"

class printVarDeps : public ModulePass {
  
public:
    printVarDeps() : ModulePass(ID) {}
  
    virtual bool runOnModule(Module &M);
    virtual void getAnalysisUsage(AnalysisUsage &AU) const;

    void printDepPairs(Function* fp, list< pair<Instruction*, Instruction*> > deppairs);
    void printVarDepGraph();
    void printDepPairs2Json();

    static char ID; // Pass identification, replacement for typeid

private:
    map< Function*, list< pair<Instruction*, Instruction*> > > varDepGraph;
    map< StringRef, list< pair<StringRef, StringRef> > >  varDepGraph_str;
};

#endif
