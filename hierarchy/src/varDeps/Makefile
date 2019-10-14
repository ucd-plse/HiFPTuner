CC=g++
#CFLAGS=-c -Wall -Wformat=2 -std=c++11 -Wextra -Werror -O3 -fomit-frame-pointer -fno-exceptions -fno-rtti -fPIC -Woverloaded-virtual -Wcast-qual -fPIC -DNDEBUG -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D_STDC_LIMIT_MACROS
CFLAGS=-c -Wformat=2 -std=c++11 -Wextra -O3 -fomit-frame-pointer -fno-exceptions -fno-rtti -fPIC -Woverloaded-virtual -Wcast-qual -fPIC -DNDEBUG -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D_STDC_LIMIT_MACROS
LDFLAGS=-Wall -Wformat=2 -Wextra -Werror -shared -lpthread -ldl -lm

SOURCES=varDepsAnalysis.cpp funDepsAnalysis.cpp varFilter.cpp CreateCallDependency.cpp edgeProfiling.cpp printVarDeps.cpp
OBJECTS=$(SOURCES:.cpp=.os) jsoncpp.o
EXECUTABLE=Passes.so

all: $(SOURCES) $(EXECUTABLE)

clean:
	rm -f *.os *.so *.o
    
$(EXECUTABLE): $(OBJECTS) 
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

%.os: %.cpp jsoncpp.cpp
	$(CC) $(CFLAGS) $< -o $@

jsoncpp.o: jsoncpp.cpp
	$(CC) -c -O2 -fPIC jsoncpp.cpp -o jsoncpp.o 
