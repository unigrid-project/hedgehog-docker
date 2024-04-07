#!/bin/sh

# Define the path to the Gridnode key file
GRIDNODE_KEY_FILE="/etc/hedgehog/gridnode_key.txt"

# Start the Hedgehog daemon with the specified arguments
echo "NETWORK_ENV: $NETWORK_ENV"
# Check the network environment and set keys
if [ "$NETWORK_ENV" = "devnet" ]; then
    NETWORK_KEYS=$DEVNET_KEYS
    echo "Using devnet keys"
else
    # Default to testnet if NETWORK_ENV is not set or is set to any other value
    NETWORK_KEYS=$TESTNET_KEYS
    echo "Using testnet keys"
fi

# Initialize command to start the Hedgehog daemon
HEDGEHOG_COMMAND="/app/hedgehog.bin daemon --netport=\"$NETPORT\" --restport=\"$RESTPORT\" --no-seeds --network-keys=\"$NETWORK_KEYS\""

# Check if the Gridnode key file exists and is not empty
if [ -s "$GRIDNODE_KEY_FILE" ]; then
    # Read the key from the file
    GRIDNODE_KEY=$(cat "$GRIDNODE_KEY_FILE")
    # Append the gridnode key to the command
    HEDGEHOG_COMMAND="$HEDGEHOG_COMMAND --gridnode=\"$GRIDNODE_KEY\""
fi

echo "Starting Hedgehog with the following settings:"
echo "Network Port: $NETPORT"
echo "REST Port: $RESTPORT"
echo "Network Keys: $NETWORK_KEYS"
echo "Gridnode Key: $GRIDNODE_KEY (if available)"
echo "--------------------------"

# Execute the Hedgehog command
eval $HEDGEHOG_COMMAND &

# Wait for the Hedgehog daemon to fully start
sleep 15

# Echo the node-add command for visibility
echo "Executing node-add command:"
/app/hedgehog.bin cli --netport="$NETPORT" --restport="$RESTPORT" node-add "$NODE_ADD":"$NETPORT"

# Keep the container running
tail -f /dev/null
