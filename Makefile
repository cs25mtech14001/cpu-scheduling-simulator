CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -pedantic
BACKEND := backend

SOURCES := fcfs sjf srtf rr priority hrrn mqs mlfq ljf lrtf
BINARIES := $(addprefix $(BACKEND)/,$(SOURCES))

.PHONY: all clean

all: $(BINARIES)

$(BACKEND)/%: $(BACKEND)/%.cpp $(BACKEND)/json.hpp
	$(CXX) $(CXXFLAGS) $< -o $@

clean:
	rm -f $(BINARIES)
	rm -f $(BACKEND)/*.o
