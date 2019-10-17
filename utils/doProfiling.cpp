#include <json/json.h>
#include <fstream>
//#include <string>
#include <sstream>
#include <stdlib.h>
#include <stdio.h>

using namespace std;
//#define jsonFile "profOut.json" 

Json::Value root;
string str;
long counts;
//ostringstream strout;

void readJson(const char * jsonFile){
    ifstream content(jsonFile);
    content >> root;
    content.close();
}

void writeJson(const char * jsonFile){
    ofstream output(jsonFile);
    output << root;
    output.close();
}

void doProfiling(const char * funcName, int index){
    str = root[funcName][index].asString();
    //istringstream strin(str);
    //strin >> counts;

    counts = strtol(str.c_str(), NULL, 0);

    counts++;

    ostringstream strout;
    strout << counts;

    root[funcName][index] = strout.str();
}
/*
int main(){
    readJson("profOut.json");
    writeJson("ivy.json");
    return 0;   
}*/
