NAME=airdrop

all:
	rm -rf build
	mkdir build
	eosiocpp -o build/$(NAME).wast src/$(NAME).cpp
	cp build/$(NAME).abi src/$(NAME).abi
