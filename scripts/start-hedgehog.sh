#!/bin/sh

# Start the Hedgehog daemon with the specified arguments
echo "NETWORK_ENV: $NETWORK_ENV"
# Check the network environment and set keys
if [ "$NETWORK_ENV" = "devnet" ]; then
    export NETWORK_KEYS=$DEVNET_KEYS
    echo "Using devnet keys"
else
    # Default to testnet if NETWORK_ENV is not set or is set to any other value
    export NETWORK_KEYS=$TESTNET_KEYS
    echo "Using testnet keys"
fi

echo "Starting Hedgehog with the following settings:"
# echo "REST Host: 0.0.0.0"
echo "Network Port: $NETPORT"
echo "REST Port: $RESTPORT"
echo "Network Keys: $NETWORK_KEYS"
echo "--------------------------"

# dont expose the rest api to the world for now
# --resthost=0.0.0.0 
java -jar /app/hedgehog.jar daemon --netport="$NETPORT" --restport="$RESTPORT" --gridnode="$GRIDNODE_KEY" --no-seeds --network-keys="$NETWORK_KEYS" & #-vvvvvvv >> debug.log

# Wait for the Hedgehog daemon to fully start
sleep 15

# Echo the node-add command for visibility
echo "Executing node-add command:"
java -jar /app/hedgehog.jar cli --netport="$NETPORT" --restport="$RESTPORT" node-add "$NODE_ADD":"$NETPORT"


# Keep the container running
tail -f /dev/null
