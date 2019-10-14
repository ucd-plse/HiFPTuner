#include "printVarDeps.hpp"
#include "varFilter.hpp"

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

bool printVarDeps::runOnModule(Module &M) {
  
    errs() << "\nPass print-varDeps -- " << M.getName()<< " :\n\n";

    varFilters &vardeps = getAnalysis<varFilters>();
    varDepGraph = vardeps.getVarDepGraph();
    
    for(map<Function*, list< pair<Instruction*, Instruction*> > >::iterator it = varDepGraph.begin(); it != varDepGraph.end(); it++){
	Function* fp = dyn_cast<Function>(it->first);
	list< pair<Instruction*, Instruction*> > deppairs = it->second;
	printDepPairs(fp, deppairs);
    }
  
/********************************************************* 
 * Print Data Dependence Graph
*********************************************************/
    errs() << "\n  Check File:\"varDepPairs_pro.json\" for the var dependence pairs.\n";
    printDepPairs2Json();
    return false;
}  

Value* allocaVar(AllocaInst * aInst){
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

void printVarDeps::printDepPairs(Function* fp, list< pair<Instruction*, Instruction*> > deppairs) {
    errs() << "Func: " << fp->getName() << ".....\n";

    list< pair<StringRef, StringRef> > varDeps;
    for(list<pair <Instruction*, Instruction*> >::iterator i = deppairs.begin(); i != deppairs.end(); i++){
      Instruction* ldInst = dyn_cast<LoadInst>(i->first);
      Instruction* stInst = dyn_cast<StoreInst>(i->second);
      if(ldInst == NULL or stInst == NULL){
	    errs() << "Error.\n";
	    return;
      }
      Value* ldVar = ldInst->getOperand(0);
      Value* stVar = stInst->getOperand(1);
      assert(isa<PointerType>(ldVar->getType)&&isa<PointerType>(stVar->getType()));
      Type* ldTy = cast<PointerType>(ldVar->getType())->getElementType();
      Type* stTy = cast<PointerType>(stVar->getType())->getElementType();

      StringRef ldName = ldVar->getName();
      StringRef stName = stVar->getName();

      /* ldVar or stVar is an element of a structure*/
      while(ldName == "" && isa<GetElementPtrInst>(ldVar)){
	    GetElementPtrInst* gepInst = dyn_cast<GetElementPtrInst>(ldVar);
	    Value* ldStructure = gepInst->getPointerOperand();
        if(isa<AllocaInst>(ldStructure)){
	      //errs() << "ldStructure: allocateInst" << "\n";
	      ldVar = allocaVar(cast<AllocaInst>(ldStructure));
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
	        ldVar = allocaVar(cast<AllocaInst>(ldVar));
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
	      stVar = allocaVar(cast<AllocaInst>(stStructure));
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
	        stVar = allocaVar(cast<AllocaInst>(stVar));
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

      varDeps.push_back(make_pair(ldName, stName));
    }

    varDepGraph_str[fp->getName()] = varDeps;
}

void printVarDeps::printDepPairs2Json(){
    FILE * fp = fopen(varDepOutFile_print, "w+");
    // print "{"
    fprintf(fp, "{\n");

    // print Catalog
    fprintf(fp, "\"Catalog\":\n");
    
    fprintf(fp, "  [\n");
    for(map<StringRef, list< pair<StringRef, StringRef> > >::iterator it = varDepGraph_str.begin(); it != varDepGraph_str.end(); it++){
	if(it!=varDepGraph_str.begin()){
	        fprintf(fp, ",\n");	
	}
	fprintf(fp, "    \"%s\"", it->first.str().c_str());
    }
    fprintf(fp, "\n  ],\n");
    
    // print Content
    fprintf(fp, "\"Content\":\n");
    fprintf(fp, "  {\n");
    for(map<StringRef, list< pair<StringRef, StringRef> > >::iterator it = varDepGraph_str.begin(); it != varDepGraph_str.end(); it++){
	
	if(it!=varDepGraph_str.begin()){
	        fprintf(fp, ",\n");	
	}
	fprintf(fp, "    \"%s\":\n", it->first.str().c_str());
	fprintf(fp, "      [\n");

	list< pair<StringRef, StringRef> > deppairs = it->second;
	for(list< pair<StringRef, StringRef> >::iterator i = deppairs.begin(); i != deppairs.end(); i++){
            //errs() << "    <" << i->first << " , " << i->second << ">\n";
	    if(i!=deppairs.begin()){
	        fprintf(fp, ",\n");	
	    }
	    fprintf(fp, "        [\"%s\",\"%s\"]", i->first.str().c_str(), i->second.str().c_str());
	}
	fprintf(fp, "\n      ]");
    }
    
    fprintf(fp, "\n  }");

    // print "}"
    fprintf(fp, "\n}");
    fclose(fp);
}

void printVarDeps::getAnalysisUsage(AnalysisUsage &AU) const {
    AU.setPreservesAll();
    AU.addRequired<varFilters>();
}

char printVarDeps::ID = 0;
static const RegisterPass<printVarDeps> registration("print-varDeps", "print the variable dependence graph");
