import subprocess
import random
import os

DEFAULT_NODE_ADD = "207.180.254.48"


def is_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def install_docker():
    print("Installing Docker...")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(
        [
            "sudo",
            "apt-get",
            "install",
            "-y",
            "apt-transport-https",
            "ca-certificates",
            "curl",
            "software-properties-common",
        ],
        check=True,
    )
    subprocess.run(
        [
            "curl",
            "-fsSL",
            "https://download.docker.com/linux/ubuntu/gpg",
            "|",
            "sudo",
            "apt-key",
            "add",
            "-",
        ],
        check=True,
    )
    subprocess.run(
        [
            "sudo",
            "add-apt-repository",
            "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable",
        ],
        shell=True,
    )
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "docker-ce"], check=True)


def setup_firewall():
    print("Configuring UFW to allow required ports...")
    subprocess.run(["sudo", "ufw", "allow", "39999"], check=True)
    subprocess.run(["sudo", "ufw", "allow", "39886"], check=True)
    subprocess.run(["sudo", "ufw", "allow", "40000"], check=True)
    subprocess.run(["sudo", "ufw", "allow", "40001"], check=True)


def pull_hedgehog_image():
    print("Pulling unigrid/hedgehog:testnet Docker image...")
    subprocess.run(["sudo", "docker", "pull", "unigrid/hedgehog:testnet"], check=True)


def install_watchtower():
    print("Checking if Watchtower is already installed...")
    existing_container = subprocess.run(
        ["sudo", "docker", "ps", "-a", "-q", "--filter", "name=^/watchtower$"],
        capture_output=True,
        text=True,
    )
    if existing_container.stdout.strip():
        print("Watchtower container already exists. Removing...")
        subprocess.run(["sudo", "docker", "rm", "-f", "watchtower"], check=True)

    print("Installing Watchtower...")
    interval = random.randint(86400, 172800)
    subprocess.run(
        [
            "sudo",
            "docker",
            "run",
            "-d",
            "--name",
            "watchtower",
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
            "containrrr/watchtower",
            "--interval",
            str(interval),
        ],
        check=True,
    )


def setup_hedgehog_volume():
    print("Setting up Docker volume for Hedgehog data...")
    subprocess.run(["sudo", "docker", "volume", "create", "hedgehog_data"], check=True)


def start_hedgehog_container(network, netport, restport, node_add, rest_expose_cmd):
    print(f"Starting Hedgehog container on {network}...")
    print("Using seed node: " + node_add)
    docker_run_cmd = [
        "sudo",
        "docker",
        "run",
        "-d",
        "-p",
        f"{netport}:{netport}",
        "-p",
        f"{restport}:{restport}",
        "--name",
        "hedgehog",
        "-v",
        "hedgehog_data:/root/.local/share/hedgehog"
    ]

    # Set NETWORK_ENV environment variable
    docker_run_cmd.extend(["-e", f"NETWORK_ENV={network}"])
    # Set NODE_ADD environment variable if provided
    if node_add:
        docker_run_cmd.extend(["-e", f"NODE_ADD={node_add}"])
    # Set REST_EXPOSE environment variable if provided
    if rest_expose_cmd:
        docker_run_cmd.extend(["-e", f"REST_HOST={rest_expose_cmd}"])
    # Append the Docker image name at the end
    docker_run_cmd.append("unigrid/hedgehog:testnet")

    print("Docker run command:", " ".join(docker_run_cmd))
    print(f"Network: {network}, Node Add: {node_add}")
    subprocess.run(" ".join(docker_run_cmd), shell=True, check=True)
    copy_key_to_container()

def ask_for_network():
    print("Please select a network to connect to:")
    print("1) Testnet")
    print("2) Devnet")
    choice = input("Enter your choice (1/2): ").strip()
    if choice == "1":
        return "testnet", 39999, 39886
    elif choice == "2":
        return "devnet", 40000, 40001
    else:
        print("Invalid choice. Defaulting to Testnet.")
        return "testnet", 39999, 39886


def ask_for_gridnode_key():
    gridnode_key = input(
        "Enter your Gridnode Key (leave blank if not available): "
    ).strip()
    if gridnode_key:
        local_key_file_path = (
            "gridnode_key.txt"  # Saves the file in the current directory
        )
        with open(local_key_file_path, "w") as file:
            file.write(gridnode_key)


def copy_key_to_container():
    local_key_file_path = "gridnode_key.txt"
    if os.path.exists(local_key_file_path):
        container_path = "hedgehog:/root/.local/share/hedgehog/gridnode_key.txt"  # Adjust if necessary
        subprocess.run(
            ["sudo", "docker", "cp", local_key_file_path, container_path], check=True
        )
    else:
        print("Gridnode key file does not exist, not copying to container.")


def ask_for_node_add():
    print("Select the Node Address option:")
    print(
        f"1) Use default ({DEFAULT_NODE_ADD}) - This will use the predefined default IP address."
    )
    print("2) Leave blank - No specific node address will be set.")
    print("3) Enter a new IP address - You can specify a custom IP address.")
    choice = input("Enter your choice (1/2/3), default [1]: ").strip()

    if choice == "1" or choice == "":
        return DEFAULT_NODE_ADD  # Use the default IP address
    elif choice == "2":
        return ""  # Leave blank
    elif choice == "3":
        return input("Enter the new Node Address: ").strip()

def ask_for_rest_exposure():
    print("Do you want to expose the REST service to the world? This allows anyone to send commands to this node.")
    print("1) Yes - Expose REST service")
    print("2) No - Do not expose REST service (default)")
    choice = input("Enter your choice (1/2), default [2]: ").strip()

    if choice == "1":
        return "--resthost=0.0.0.0"
    else:
        return ""

def main():
    if not is_docker_installed():
        install_docker()
    else:
        print("Docker is already installed.")

    network, netport, restport = ask_for_network()
    ask_for_gridnode_key()
    node_add = ask_for_node_add()
    rest_expose_cmd = ask_for_rest_exposure()
    setup_firewall()
    pull_hedgehog_image()
    install_watchtower()
    setup_hedgehog_volume()
    start_hedgehog_container(network, netport, restport, node_add, rest_expose_cmd)


if __name__ == "__main__":
    main()
