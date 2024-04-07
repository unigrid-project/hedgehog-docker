## Install from python script
```bash
curl -sSL -o install.py https://raw.githubusercontent.com/unigrid-project/hedgehog-docker/master/install.py
python3 install.py
```

## Check hedgehog version
```bash
docker exec hedgehog /app/hedgehog.bin cli --version
```

## Check hedgehog conenctions
```bash
docker exec hedgehog /app/hedgehog.bin cli node-list --restport=39886
```

## Check the gridnode list
```bash
docker exec hedgehog /app/hedgehog.bin cli gridnode --restport=39886
```

```bash
docker exec -it hedgehog bash
```

## Build Container
```bash
docker build --no-cache -t unigrid/hedgehog:testnet .
```

## Stop and remove containers
```bash
docker stop watchtower hedgehog
docker rm watchtower hedgehog
```
## Run
### TESTNET
docker run -d -p 39999:39999 -p 39886:39886 -e NETWORK_ENV=testnet -e GRIDNODE_KEY=<gridnode key> -e NODE_ADD="149.102.147.45" unigrid/hedgehog:testnet
### DEVNET
docker run -d -p 40000:40000 -p 40001:40001 -e NETWORK_ENV=devnet -e NETPORT=40000 -e RESTPORT=40001 -e GRIDNODE_KEY=<gridnode key> -e NODE_ADD="173.212.208.212" unigrid/hedgehog:testnet 


