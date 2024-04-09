#!/bin/sh

# Log file location
LOG_FILE="/var/log/hedgehog_startup.log"

# Function to log messages
log() {
    echo "$(date): $1" >> $LOG_FILE
}

# Timeout in seconds
TIMEOUT=5
ELAPSED=0
INTERVAL=1

# Define the path to the Gridnode key file
GRIDNODE_KEY_FILE="/root/.local/share/hedgehog/gridnode_key.txt"

log "Waiting for Gridnode key file..."

while [ ! -f "$GRIDNODE_KEY_FILE" ]; do
    if [ $ELAPSED -ge $TIMEOUT ]; then
        log "Timeout reached. Continuing without Gridnode key file."
        break
    fi
    sleep $INTERVAL
    ELAPSED=$((ELAPSED+INTERVAL))
done

# Start the Hedgehog daemon with the specified arguments
log "NETWORK_ENV: $NETWORK_ENV"
# Check the network environment and set keys
if [ "$NETWORK_ENV" = "devnet" ]; then
    NETWORK_KEYS=$DEVNET_KEYS
    log "Using devnet keys"
else
    # Default to testnet if NETWORK_ENV is not set or is set to any other value
    NETWORK_KEYS=$TESTNET_KEYS
    log "Using testnet keys"
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

log "Starting Hedgehog with the following settings:"
log "Network Port: $NETPORT"
log "REST Port: $RESTPORT"
log "Network Keys: $NETWORK_KEYS"
log "Gridnode Key: $GRIDNODE_KEY (if available)"
log "--------------------------"

# Execute the Hedgehog command
eval $HEDGEHOG_COMMAND &

# Wait for the Hedgehog daemon to fully start
sleep 15

# Check if NODE_ADD is set and not empty before executing node-add command
if [ -n "$NODE_ADD" ]; then
    log "Executing node-add command with NODE_ADD set to $NODE_ADD"
    /app/hedgehog.bin cli --netport="$NETPORT" --restport="$RESTPORT" node-add "$NODE_ADD":"$NETPORT"
else
    log "NODE_ADD is not set, skipping node-add command"
fi

# Keep the container running
tail -f $LOG_FILE

# Keep the container running
# tail -f /dev/null
