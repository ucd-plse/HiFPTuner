CC=gcc
CFLAGS=-c -Wall -fPIC
LDFLAGS=-shared
BCFLAGS=-c -emit-llvm

SOURCES := $(wildcard *.c)
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=liblog.so

all: $(SOURCES) $(EXECUTABLE)
clean: 
	rm -f $(EXECUTABLE) $(OBJECTS)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $(OBJECTS)

%.o : %.c
	$(CC) $(CFLAGS) -o $@ $<
