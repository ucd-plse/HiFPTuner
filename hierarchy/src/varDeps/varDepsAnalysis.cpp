#include "varDepsAnalysis.hpp"
#include "CreateCallDependency.hpp"

#include <llvm/IR/Function.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/User.h>
#include <llvm/IR/ValueSymbolTable.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/IR/InstIterator.h>
#include <queue>
#include <set>

using namespace std;
using namespace llvm;


bool varDeps::runOnModule(Module &M) {
  
    errs() << "\nPass varDeps-analysis:\n\n";

    CreateCallDependency &calldep = getAnalysis<CreateCallDependency>();
    set<string> calls = calldep.getFunCalls();

    for(Module::iterator f = M.begin(), fe = M.end(); f != fe; f++) {
      //if(!f->isDeclaration())
      if(calls.find(f->getName()) != calls.end())
            runOnFunction(*f);
    }

/********************************************************* 
 * Print Data Dependence Graph
*********************************************************/
    printVarDepGraph();
    
    return false;
}  


bool varDeps::runOnFunction(Function &F) {
    //errs() << "Func: " << F.getName() << "\n";

    list< pair<Instruction*, Instruction*> > deppairs;
    deppairs.clear();

/********************************************************* 
 * 1. Collect "store" instructions
*********************************************************/
    queue<Instruction*> storequeue;
    for(inst_iterator I = inst_begin(F), Ie = inst_end(F); I != Ie; ++I){
        Instruction* inst = dyn_cast<Instruction>(&*I);
        if(inst->getOpcode() == Instruction::Store){
            storequeue.push(inst);
        }
    }

/******************************************************** 
 * 2. For each "store", find "load"s it depends. Each 
 * "load"->"store" pair demenstrates the dependence between 
 * two variables.  
********************************************************/
    queue<Instruction*> workqueue;
    while(!storequeue.empty()){
        Instruction* inst = storequeue.front();
        storequeue.pop();
        workqueue.push(inst);
        while(!workqueue.empty()){
            Instruction* v = workqueue.front();
            workqueue.pop();
            for(User::op_iterator i = v->op_begin(), ie = v->op_end(); i != ie; ++i){
                Instruction* vi = dyn_cast<Instruction>(*i);
                if(vi == NULL)
                    continue;
                if(vi->getOpcode() == Instruction::Load){
                    /*define-use instruction pair*/
                    //errs() << "    def-use:" << *inst << "," << *vi << "\n";
		    deppairs.push_back(make_pair(vi, inst));
                }else{
		    workqueue.push(vi);
                }
            }
        }
    }
        
    varDepGraph[&F] = deppairs;       
    return false;
}


void varDeps::printVarDepGraph(){
    for(map<Function*, list< pair<Instruction*, Instruction*> > >::iterator it = varDepGraph.begin(); it != varDepGraph.end(); it++){
        Function* fp = dyn_cast<Function>(it->first);
        errs() << "Func: " << fp->getName() << "\n";
        list< pair<Instruction*, Instruction*> > deppairs = it->second;
        for(list< pair<Instruction*, Instruction*> >::iterator i = deppairs.begin(); i != deppairs.end(); i++){
            errs() << "    <" << *i->first << " , " << *i->second << ">\n";
        }
    }
}

void varDeps::getAnalysisUsage(AnalysisUsage &AU) const {
    AU.setPreservesAll();
    AU.addRequired<CreateCallDependency>();
}

char varDeps::ID = 0;
static const RegisterPass<varDeps> registration("varDeps-analysis", "variable dependence analysis");
