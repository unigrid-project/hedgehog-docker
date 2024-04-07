## Install from python script


## Build Container
docker build -t unigrid/hedgehog:testnet .

## Run
### TESTNET
docker run -d -p 39999:39999 -p 39886:39886 -e NETWORK_ENV=testnet -e GRIDNODE_KEY=<gridnode key> -e NODE_ADD="149.102.147.45" unigrid/hedgehog:testnet
### DEVNET
docker run -d -p 40000:40000 -p 40001:40001 -e NETWORK_ENV=devnet -e NETPORT=40000 -e RESTPORT=40001 -e GRIDNODE_KEY=<gridnode key> -e NODE_ADD="173.212.208.212" unigrid/hedgehog:testnet 


