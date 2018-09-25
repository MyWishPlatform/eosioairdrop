NAME=airdrop

all:
	rm -rf $(NAME)/*.w*
	eosiocpp -o $(NAME)/$(NAME).wast $(NAME).cpp
