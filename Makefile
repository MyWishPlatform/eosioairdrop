.PHONY: all clean test debug
NAME=airdrop

all:
	rm -rf build
	mkdir build
	eosiocpp -o build/$(NAME).wast src/$(NAME).cpp
	cp src/$(NAME).abi build/$(NAME).abi

clean:
	rm -rf build

test:
	python3 test/unittest_airdrop.py

debug:
	python3 test/unittest_airdrop.py --verbose
