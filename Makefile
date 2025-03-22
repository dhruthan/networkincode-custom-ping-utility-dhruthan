# Default values
TARGET ?= 127.0.0.1
COUNT ?= 4
TTL ?= 64
TIMEOUT ?= 2

# Python executable
PYTHON = python3

# Paths
SRC = src/main.py
TEST_SCRIPT = scripts/test.sh

# Commands
.PHONY: ping test clean

ping:
	@sudo $(PYTHON) $(SRC) $(TARGET) -c $(COUNT) -t $(TTL) -W $(TIMEOUT)

test:
	@bash $(TEST_SCRIPT)

clean:
	@echo "Nothing to clean yet (no compiled files)."
