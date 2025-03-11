# Makefile

.PHONY: run test clean

run:
	python3 src/main.py

test:
	bash scripts/test.sh

clean:
	rm -rf __pycache__