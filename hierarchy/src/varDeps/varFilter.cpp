#include "varFilter.hpp"
#include "varDepsAnalysis.hpp"

#include <llvm/IR/Function.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/User.h>
#include <llvm/IR/ValueSymbolTable.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/IR/InstIterator.h>
#include <queue>
#include <assert.h>
#include <stdio.h>

using namespace std;
using namespace llvm;


bool varFilters::runOnModule(Module &M) {
  
    errs() << "\nPass varFilters:\n\n";

    varDeps &vardeps = getAnalysis<varDeps>();
    varDepGraph = vardeps.getVarDepGraph();
    
    for(map<Function*, list< pair<Instruction*, Instruction*> > >::iterator it = varDepGraph.begin(); it != varDepGraph.end(); it++){
      Function* fp = dyn_cast<Function>(it->first);
      Function* ffp = M.getFunction(fp->getName());
      if (fp == ffp){
	    filters(fp, it->second);
      }else{
	    varDepGraph.erase(it);
      }
    }
  
/********************************************************* 
 * Print Data Dependence Graph
*********************************************************/
    errs() << "\n  Check File:\"varDepPairs.json\" for the var dependence pairs.\n";
    printDepPairs2Json();
    //printVarDepGraph();
    return false;
}  

Value* allocaVar_ivy(AllocaInst * aInst){
    Value* aVar = aInst;
    BasicBlock* allocaBB = dyn_cast<BasicBlock>(aInst->getParent());
    for(BasicBlock::iterator i = allocaBB->begin(), ie = allocaBB->end(); i != ie; ++i){
        Instruction* inst = dyn_cast<StoreInst>(i);
        if(inst == NULL)
	    continue;
	if(inst->getOperand(1) == aVar){
	    //errs() << *inst << "\n";		  
	    aVar = inst->getOperand(0);
	    break;
	}
    }
    return aVar;
}

void varFilters::filters(Function* fp, list< pair<Instruction*, Instruction*> > &deppairs) {
    errs() << "Func: " << fp->getName() << ".....\n";

    for(list<pair <Instruction*, Instruction*> >::iterator i = deppairs.begin(); i != deppairs.end(); i++){
      Instruction* ldInst = dyn_cast<LoadInst>(i->first);
      Instruction* stInst = dyn_cast<StoreInst>(i->second);
      if(ldInst == NULL or stInst == NULL){
	    deppairs.erase(i);
	    i--;
	    continue;
      }
      Value* ldVar = ldInst->getOperand(0);
      Value* stVar = stInst->getOperand(1);
      assert(isa<PointerType>(ldVar->getType)&&isa<PointerType>(stVar->getType()));
      Type* ldTy = cast<PointerType>(ldVar->getType())->getElementType();
      Type* stTy = cast<PointerType>(stVar->getType())->getElementType();
      if(!ldTy->isFloatingPointTy() || !stTy->isFloatingPointTy()){
	    deppairs.erase(i);
	    i--;
	    continue;	
      }

      StringRef ldName = ldVar->getName();
      StringRef stName = stVar->getName();

      /* ldVar or stVar is an element of a structure*/
      while(ldName == "" && isa<GetElementPtrInst>(ldVar)){
	    GetElementPtrInst* gepInst = dyn_cast<GetElementPtrInst>(ldVar);
	    Value* ldStructure = gepInst->getPointerOperand();
        if(isa<AllocaInst>(ldStructure)){
	      //errs() << "ldStructure: allocateInst" << "\n";
	      ldVar = allocaVar_ivy(cast<AllocaInst>(ldStructure));
	    }
	    if(isa<LoadInst>(ldStructure)){
	      //errs() << "ldStructure: loadInst" << "\n";
	      ldVar = (cast<LoadInst>(ldStructure))->getOperand(0);
	    }
	    if(isa<GlobalVariable>(ldStructure)){
	      //errs() << "ldStructure: GlobalVariable" << "\n";
	      ldVar = ldStructure;
	    }

	    ldName = ldVar->getName();
	    if(ldName == "" ){
	      //errs() << "             ldVar:" << *ldVar << "," << *ldTy << "\n";
	      //errs() << "             ldStructure:" << *ldStructure  << "\n";
          ldVar = ldStructure;
	    }

      }

       /* find the load variable for allocate/load instructions*/
      while(ldName == "" && (isa<AllocaInst>(ldVar) || isa<LoadInst>(ldVar))){      
        if(isa<AllocaInst>(ldVar)){
	        ldVar = allocaVar_ivy(cast<AllocaInst>(ldVar));
	        ldName = ldVar->getName();
        }
	    if(isa<LoadInst>(ldVar)){
	        ldVar = (cast<LoadInst>(ldVar))->getOperand(0);
	        ldName = ldVar->getName();
	    }
      }
      if(ldName == ""){
	  errs() << "             ldVar:" << *ldVar << "," << *ldTy << "\n";
      }
  
      while(stName == "" && isa<GetElementPtrInst>(stVar)){	  
	  GetElementPtrInst* stgepInst = dyn_cast<GetElementPtrInst>(stVar);
	  Value* stStructure = stgepInst->getPointerOperand();
          if(isa<AllocaInst>(stStructure)){
	      //errs() << "stStructure: allocateInst" << "\n";
	      stVar = allocaVar_ivy(cast<AllocaInst>(stStructure));
	      }
	      if(isa<LoadInst>(stStructure)){
	      //errs() << "stStructure: loadInst" << "\n";
	      stVar = (cast<LoadInst>(stStructure))->getOperand(0);
	      }
	      if(isa<GlobalVariable>(stStructure)){
	      //errs() << "stStructure: GlobalVariable" << "\n";
	      stVar = stStructure;
	      }

	      stName = stVar->getName();
          if(stName == "" ){
            stVar = stStructure;
          }
      }
      
      /* find the load variable for allocate instructions*/      
      while(stName == "" && (isa<AllocaInst>(stVar) || isa<LoadInst>(stVar))){      
        if(isa<AllocaInst>(stVar)){
	        stVar = allocaVar_ivy(cast<AllocaInst>(stVar));
	        stName = stVar->getName();
        }
	    if(isa<LoadInst>(stVar)){
	        stVar = (cast<LoadInst>(stVar))->getOperand(0);
	        stName = stVar->getName();
	    }
      }
      if(stName == ""){
	  errs() << "             stVar:" << *stVar << "," << *stTy << "\n";
      }
      
      //errs() << "    <" << *i->first << " , " << *i->second << ">\n";
      //errs() << "    <" << ldName << "::" << *ldTy << " , " << stName << "::" << *stTy << ">\n";
      //errs() << "    <" << ldName << " , " << stName << ">\n";
      string ldstr;
      if(isa<GlobalValue>(ldVar)){	
	    ldstr.append(ldName.str());
      }else{
	    ldstr.append(fp->getName().str()).append(".").append(ldName.str());
      }
      
      string ststr;
      if(isa<GlobalValue>(stVar)){
	  ststr.append(stName.str());
      }else{
	  ststr.append(fp->getName().str()).append(".").append(stName.str());
      }
      
      char * dldstr = (char *)malloc(ldstr.size()+1 * sizeof(char));
      char * dststr = (char *)malloc(ststr.size()+1 * sizeof(char));
      ldstr.copy(dldstr, ldstr.size());
      dldstr[ldstr.size()] = '\0';
      ststr.copy(dststr, ststr.size());
      dststr[ststr.size()] = '\0';
      ldName = StringRef(dldstr);
      stName = StringRef(dststr);

      errs() << "    <" << ldName << " , " << stName << ">\n";

      vDepGraph.push_back(make_pair(ldName, stName));
    }
}

void varFilters::printVarDepGraph(){
    for(map<Function*, list< pair<Instruction*, Instruction*> > >::iterator it = varDepGraph.begin(); it != varDepGraph.end(); it++){
        Function* fp = dyn_cast<Function>(it->first);
        errs() << "Func: " << fp->getName() << "\n";
        list< pair<Instruction*, Instruction*> > deppairs = it->second;
        for(list< pair<Instruction*, Instruction*> >::iterator i = deppairs.begin(); i != deppairs.end(); i++){
            errs() << "    <" << *i->first << " , " << *i->second << ">\n";
        }
    }
}

void varFilters::printDepPairs2Json(){
    FILE * fp = fopen(varDepOutFile_filter, "w+");
    fprintf(fp, "[\n");
    for(list< pair<StringRef, StringRef> >::iterator i = vDepGraph.begin(); i != vDepGraph.end(); i++){
        //errs() << "    <" << i->first << " , " << i->second << ">\n";
        if(i!=vDepGraph.begin()){
	        fprintf(fp, ",\n");	
        }
        fprintf(fp, "    [\"%s\",\"%s\"]", i->first.str().c_str(), i->second.str().c_str());
    }
    fprintf(fp, "\n]");
    fclose(fp);
}

void varFilters::getAnalysisUsage(AnalysisUsage &AU) const {
    AU.setPreservesAll();
    AU.addRequired<varDeps>();
}

char varFilters::ID = 0;
static const RegisterPass<varFilters> registration("varFilters", "the variable filter");
