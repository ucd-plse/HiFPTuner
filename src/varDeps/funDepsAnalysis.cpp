#include "funDepsAnalysis.hpp"
#include "CreateCallDependency.hpp"

#include <llvm/IR/Function.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/User.h>
#include <llvm/IR/ValueSymbolTable.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/IR/InstIterator.h>
#include <queue>
using namespace std;
using namespace llvm;


bool funDeps::runOnModule(Module &M) {
  
    errs() << "\nPass funDepAnalysis:\n\n";
    
    CreateCallDependency &calldep = getAnalysis<CreateCallDependency>();
    set<string> calls = calldep.getFunCalls();

    for(Module::iterator f = M.begin(), fe = M.end(); f != fe; f++) {
      //if(!f->isDeclaration())
      if(calls.find(f->getName()) != calls.end())
            runOnFunction(*f);
    }

/********************************************************* 
 * Print Function Dependence Graph
*********************************************************/
    printFunDepGraph();
    printCalls();
    return false;
}  


bool funDeps::runOnFunction(Function &F) {
    //errs() << "Func: " << F.getName() << "\n";

    vector<callinfo> items;
    callinfo item;
/********************************************************* 
 * Explore "call" instructions
*********************************************************/
    for(inst_iterator I = inst_begin(F), Ie = inst_end(F); I != Ie; ++I){
        Instruction* inst = dyn_cast<Instruction>(&*I);
        if(inst->getOpcode() == Instruction::Call){
            CallInst* ci = dyn_cast<CallInst>(inst);
            
            Function* fcalled = ci->getCalledFunction();
            if(!fcalled->isDeclaration()){
                
                //errs() << *ci << "\n";
	        //insert into funDepsGraph
                funDepGraph.insert(make_pair(F.getName(), fcalled->getName()));
		//record callee name
		item.callee = fcalled->getName();
		//record the arguments
                for(unsigned i = 0; i < ci->getNumArgOperands(); i++){
                    Instruction* arginst = dyn_cast<Instruction>(ci->getArgOperand(i));
                    if(arginst == NULL)  
                        continue;                  

                    queue<Instruction*> worklist;
                    worklist.push(arginst);
                    while(!worklist.empty()){
                        Instruction* a = worklist.front();
                        worklist.pop();
                        for(User::op_iterator j = a->op_begin(), je = a->op_end(); j != je; ++j){
                            Instruction* aj = dyn_cast<Instruction>(*j);
                            if(aj == NULL)
                                continue;
                            
                            if(aj->getOpcode() == Instruction::Load){
                                if(aj->getOperand(0)->getType()->getPointerElementType()->isFloatingPointTy()){
                                    StringRef argname = aj->getOperand(0)->getName();
                                    if(argname == "")
                                        argname = "****";
                                    item.args.insert(argname);
                                    //errs() << *aj <<"\n";
                                }
				//to find all the variables that contributes to this argument, e.g. find a and b in arg "a*b"
                                continue;
                            }
                            worklist.push(aj);
                        }
                    }
                }

                queue<Instruction*> worklist;
                worklist.push(ci);
                while(!worklist.empty()){
                    Instruction* a = worklist.front();
                    worklist.pop();
                    for(Value::use_iterator k = a->use_begin(), ke = a->use_end(); k != ke; ++k){
                        Instruction* ak = dyn_cast<Instruction>(*k);
                        if (ak == NULL)
                            continue;
                        if(ak->getOpcode() == Instruction::Store){
                            if(ak->getOperand(1)->getType()->getPointerElementType()->isFloatingPointTy()){
                                StringRef retname = ak->getOperand(1)->getName();
                                if(retname == "")
                                    retname = "****";
                                item.ret = retname;
                                //errs() << *ak <<"\n";
                            }
                            break;    
                        }
                    }
                }
                items.insert(items.end(), item);
            }
        }
    }
 
    calls[F.getName()] = items;
    return false;
}

void funDeps::printFunDepGraph(){
    errs() << "Caller-Callee Pairs:\n";
    for(set< pair<StringRef, StringRef> >::iterator it = funDepGraph.begin(); it != funDepGraph.end(); it++){
        errs() << "    <" << it->first << " , " << it->second << ">\n";
    }
}

void funDeps::printCalls(){
    errs() << "\nCallInfo:\n\n";
    for(map<StringRef, vector<callinfo> >::iterator it = calls.begin(); it != calls.end(); it++){
        if(it->second.size() == 0)
            continue;
        errs() << "Func:  " << it->first << "\n";
        for(vector<callinfo>::iterator j = it->second.begin(); j != it->second.end(); j++){
            j->printCallInfo();
       }
    }
}

void funDeps::getAnalysisUsage(AnalysisUsage &AU) const {
    AU.setPreservesAll();
    AU.addRequired<CreateCallDependency>();
}

char funDeps::ID = 0;
static const RegisterPass<funDeps> registration("funDeps-analysis", "function dependence analysis");
