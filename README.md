
# HiFPTuner

Exploiting community structure for floating-point precision tuning, ISSTA'18

## INSTALL

You can either use docker or build from scratch which is the hard way to use HiFPTuner.

### Use docker
Pull Docker Image from Docker Hub

    docker pull hguo15/hifptuner:v0
    docker run -ti --name=hifptuner hguo15/hifptuner:v0
    
Or Build a Doker Image by yourself

    git clone https://github.com/ucd-plse/HiFPTuner.git
    cd HiFPTuner
    docker build -t docker-hifptuner .
    docker run -ti --name=hifptuner docker-hifptuner

### Build from scratch
Prerequisites:

    1. llvm 3.0 & 3.8

    2. Precimonious
        repo.: https://github.com/ucd-plse/precimonious 

    3. NetworkX 2.2 python package
        install: pip install 'networkx==2.2'
        repo.:   https://github.com/networkx/networkx

    4. Community python package
        install: pip install python-louvain
        repo.: https://bitbucket.org/taynaud/python-louvain

    5. pygraphviz and other graph python packages
        pip install graphviz
        pip install pygraphviz
        apt-get install python-matplotlib
        apt-get install libgraphviz-dev
        apt-get install python-dev

Install HiFPTuner:

    1. git clone https://github.com/ucd-plse/HiFPTuner.git
    2. cd HiFPTuner/precimonious/logging
    3. make clean; make
    4. switch to llvm 3.8
       in the docker image of HiFPTuner, switching to llvm 3.8 as following, 
       4.1 modify ~/.bashrc: $LLVM_VERSION=llvm-3.8
       4.2 . ~/.bashrc
    5. cd HiFPTuner/src/varDeps
    6. make clean; make

## Example


#### To generate HiFPTuner config files : "sorted_partition.json"    
    1. $cd HiFPTuner/examples/simpsons
 
    2. generate llvm_3.0 bitcode file
        switch to llvm 3.0
        $clang -c -emit-llvm simpsons.c -o simpsons.bc
        $path/to/HiFPTuner/scripts/compile.sh simpsons.bc

    3. Run llvm analysis and transformation passes to attain the dependence graph
        switch to llvm 3.8
        $path/to/HiFPTuner/scripts/analyze.sh json_simpsons.bc
        (Check outputs: "varDepPairs_pro.json" and "edgeProfilingOut.json" for the dependece pairs and edge weights.)

    4. Run Networkx and community packages to attain the unsorted and sorted hierarchy
        $path/to/HiFPTuner/scripts/config.sh
        (Check outputs: "partition.json", "sorted_partition.json" and "topolOrder_pro.json" for the unsorted hierarchy, sorted hierarchy and the topological ordered variable list)
        (Also, check varDepGraph_pro.png for the visualized dependence graph)

#### Dynamic TUNING 
    1. switch to llvm 3.0

    2. create current precision configuration file
      $path/to/HiFPTuner/precimonious/scripts/pconfig.sh simpsons .

    3. create search space
      $path/to/HiFPTuner/precimonious/scripts/search.sh simpsons .

    4. dynamic tuning
      $python -O path/to/HiFPTuner/precimonious/scripts/dd2_prof.py simpsons.bc search_simpsons.json config_simpsons.json sorted_partition.json
