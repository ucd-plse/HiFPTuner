CC=clang
CFLAGS=-c -Wall
LDFLAGS=-lm
BCFLAGS=-c -emit-llvm

SOURCES := $(wildcard *.c)
BITCODES=$(SOURCES:.c=.bc)
EXECUTABLES=$(SOURCES:.c=)

all: $(SOURCES) $(EXECUTABLES) $(BITCODES)
clean: 
	rm -f $(EXECUTABLES) $(BITCODES)

$(EXECUTABLES): % : %.bc
	$(CC) -o $* $< $(LDFLAGS)

%.bc : %.c
	$(CC) $(BCFLAGS) -o $@ $<
