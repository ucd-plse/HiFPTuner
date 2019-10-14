#include "edgeProfiling.hpp"
#include "varFilter.hpp"

#include <llvm/IR/Function.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/User.h>
#include <llvm/IR/ValueSymbolTable.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/IR/InstIterator.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Type.h>
#include <queue>
#include <vector>
#include <assert.h>
#include <stdio.h>

#include <fstream>
#include <stdlib.h>

using namespace std;
using namespace llvm;


bool edgeProf::runOnModule(Module &M) {
  
    errs() << "\nPass edgeProfiling:\n\n";

    varFilters &vardeps = getAnalysis<varFilters>();
    varDepGraph = vardeps.getVarDepGraph();

    errs() << "\n  Check File:\"edgeProfilingOut.json\" for the var dependence pairs regarding to each function.\n";
    printProf();

    ifstream content(profOutFile);
    content >> root;
    content.close();

     for(Module::iterator f = M.begin(), fe = M.end(); f != fe; f++) {
	 //if(!f->isDeclaration())
	  //errs() << f->getName() << "\n";
    }

    //add the initialization call to main
    Function * Main = M.getFunction("main");
    if(Main == 0){
	errs() << "WARNING: cannot insert edge profiling instrumentation"
	       << "into a module with no main function!\n";
	errs() << "Exit with errors.\n";
	return false;
    }
    InsertProfilingInitCall(M, Main);
    
    //add edge instrumentation calls
    for(map<Function*, list< pair<Instruction*, Instruction*> > >::iterator it = varDepGraph.begin(); it != varDepGraph.end(); it++){
      Function* fp = dyn_cast<Function>(it->first);
      Function* ffp = M.getFunction(fp->getName());
      if (fp == ffp){
	  list < pair<Instruction*, Instruction*> > deppairs = it->second;
	  instrument_edge(fp, deppairs);
      }else{
	  errs() << "Incorrect data.\n";
	  errs() << "Exit with errors.\n";
	  return true;
      }
    }

    //add the finalization call to main
    InsertProfilingFinalCall(M, Main);
    
/********************************************************* 
 * Print Data Dependence Graph
*********************************************************/
    //errs() << "\n  Check File:\"edgeProfilingOut.json\" for the var dependence pairs regarding to each function.\n";
    //printProf();

    ofstream output(profOutFile);
    output << root;
    output.close();

    return true;
}

void edgeProf::InsertProfilingInitCall(Module & M, Function *MainFn){
    Function* callee = M.getFunction("_Z8readJsonPKc");
    if(callee == 0){
	errs() << "Ivy checkpoint: readJson Function not found!\n";
	return;
    }
    
    // Skip over any allocas in the entry block.
    BasicBlock *Entry = dyn_cast<BasicBlock>(MainFn->begin());
    if(Entry == 0){
	errs() << "Error.\n"; 
	return;
    }
    BasicBlock::iterator InsertPos = Entry->begin();
    while (isa<AllocaInst>(InsertPos)) ++InsertPos;
    Instruction * inst = dyn_cast<Instruction>(InsertPos);
    
    IRBuilder<> builder(inst);
    Value * argv = builder.CreateGlobalStringPtr(profOutFile);
    builder.CreateCall(callee, argv);

    errs() << "  Instrumentation of the initalization call: readJson finished.\n";
}

void edgeProf::InsertProfilingFinalCall(Module& M, Function* MainFn){
    Function* callee = M.getFunction("_Z9writeJsonPKc");
    if(callee == 0){
	errs() << "Ivy checkpoint: writeJson Function not found!\n";
	return;
    }
	
    for(Function::iterator b = MainFn->begin(); b != MainFn->end(); b++){
	for(BasicBlock::iterator i = b->begin(); i != b->end(); i++){
	    if(ReturnInst * ret = dyn_cast<ReturnInst>(i)){
		 IRBuilder<> builder(ret);
		 Value * argv = builder.CreateGlobalStringPtr(profOutFile);
		 builder.CreateCall(callee, argv);
	    }
	}
    }

    errs() << "  Instrumentation of the finalization call: writeJson finished.\n";
}

void edgeProf::instrument_edge(Function* fp, list< pair<Instruction*, Instruction*> > deppairs){    
    Module * M = fp->getParent();
    Function* callee = M->getFunction("_Z11doProfilingPKci");
    if(callee == 0){
	errs() << "Ivy checkpoint: doProfiling Function not found!\n";
	return;
    }
    
    StringRef fname = fp->getName();
    //errs() << fp->getName() <<"\n";
    int index=0;

    if(deppairs.empty()){
	errs() << "  Func " << fname << ": instrumentation of the edge profiling call: doProfiling finished.\n";
	return;
    }
    
    /*Instrument the first pair of the function*/
    Instruction * ldinst = dyn_cast<Instruction>(deppairs.begin()->first);
    //errs() << "ivy print ldinst:" << index << "--" << *ldinst << "\n";
	
    IRBuilder<> builder(ldinst);
    vector<Value *> args;
    args.push_back(builder.CreateGlobalStringPtr(fname));
    args.push_back(ConstantInt::get(Type::getInt32Ty(M->getContext()), index));
    builder.CreateCall(callee, args);
	
    map<BasicBlock*, int> bbitems;
    bbitems[ldinst->getParent()]=index;
    index++;
    
    for(list< pair<Instruction *, Instruction*> >::iterator i = deppairs.begin()++; i!=deppairs.end(); i++){
	ldinst = dyn_cast<Instruction>(i->first);	

	map<BasicBlock*, int>::iterator bi = bbitems.find(ldinst->getParent());
	if(bi == bbitems.end()){
	    errs() << "ivy print ldinst:" << index << "--" << *ldinst << "\n";
	    IRBuilder<> builder(ldinst);
	    vector<Value *> args;
	    args.push_back(builder.CreateGlobalStringPtr(fname));
	    args.push_back(ConstantInt::get(Type::getInt32Ty(M->getContext()), index));
	    builder.CreateCall(callee, args);
	    bbitems[ldinst->getParent()]=index;
	}else{
	    //-to-do: UPDATE THE JSON FILE.
	    string strindex ("INDEX");
	    strindex.append(to_string(bi->second));
	    errs() << "Print strindex:" << strindex << "\n";
	    errs() << "json " << index << " context:" << root[fname][index].asString() << "\n";
	    root[fname][index] = strindex.c_str();
	}
	index++;
    }

    //instrumentedEdges[fp]=bbitems;
    errs() << "  Func " << fname << ": instrumentation of the edge profiling call: doProfiling finished.\n";
}


void edgeProf::printProf(){
    FILE * fp = fopen(profOutFile, "w+");
    fprintf(fp, "{\n");
    for(map<Function*, list< pair<Instruction*, Instruction*> > >::iterator it = varDepGraph.begin(); it != varDepGraph.end(); it++){
	Function* funcp = dyn_cast<Function>(it->first);
	if(it!=varDepGraph.begin()){
	        fprintf(fp, ",\n");	
	}
	fprintf(fp, "  \"%s\":\n", funcp->getName().str().c_str());
	
	list< pair<Instruction*, Instruction*> > deppairs = it->second;
	fprintf(fp, "    [\n");
	for(list< pair<Instruction*, Instruction*> >::iterator i = deppairs.begin(); i != deppairs.end(); i++){
	    if(i!=deppairs.begin()){
	        fprintf(fp, ",\n");	
	    }
	    fprintf(fp, "      0");
	}
	fprintf(fp, "\n    ]");
	
    }
    fprintf(fp, "\n}");
    fclose(fp);
}

void edgeProf::getAnalysisUsage(AnalysisUsage &AU) const {
    AU.setPreservesAll();
    AU.addRequired<varFilters>();
}

char edgeProf::ID = 0;
static const RegisterPass<edgeProf> registration("edge-profiling", "edge profiling for varDep Graph");
