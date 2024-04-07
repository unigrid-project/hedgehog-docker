import subprocess
import random

def is_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_docker():
    print("Installing Docker...")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "apt-transport-https", "ca-certificates", "curl", "software-properties-common"], check=True)
    subprocess.run(["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "|", "sudo", "apt-key", "add", "-"], check=True)
    subprocess.run(["sudo", "add-apt-repository", "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"], shell=True)
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
    existing_container = subprocess.run(["sudo", "docker", "ps", "-a", "-q", "--filter", "name=^/watchtower$"], capture_output=True, text=True)
    if existing_container.stdout.strip():
        print("Watchtower container already exists. Removing...")
        subprocess.run(["sudo", "docker", "rm", "-f", "watchtower"], check=True)

    print("Installing Watchtower...")
    interval = random.randint(86400, 172800)
    subprocess.run(["sudo", "docker", "run", "-d", "--name", "watchtower", "-v", "/var/run/docker.sock:/var/run/docker.sock", "containrrr/watchtower", "--interval", str(interval)], check=True)

def setup_hedgehog_volume():
    print("Setting up Docker volume for Hedgehog data...")
    subprocess.run(["sudo", "docker", "volume", "create", "hedgehog_data"], check=True)

def start_hedgehog_container(network, netport, restport, gridnode_key):
    print(f"Starting Hedgehog container on {network}...")
    docker_run_cmd = [
        "sudo", "docker", "run", "-d", "-p", f"{netport}:{netport}", "-p", f"{restport}:{restport}",
        "--name", "hedgehog", "-v", "hedgehog_data:/root/.local/share/hedgehog",
        "unigrid/hedgehog:testnet"
    ]
    if gridnode_key:
        docker_run_cmd.extend(["-e", f"GRIDNODE_KEY={gridnode_key}"])
    docker_run_cmd.extend(["-e", f"NETWORK_ENV={network}"])
    subprocess.run(docker_run_cmd, check=True)

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
    return input("Enter your Gridnode Key (leave blank if not available): ").strip()

def main():
    if not is_docker_installed():
        install_docker()
    else:
        print("Docker is already installed.")

    network, netport, restport = ask_for_network()
    gridnode_key = ask_for_gridnode_key()

    setup_firewall()
    pull_hedgehog_image()
    install_watchtower()
    setup_hedgehog_volume()
    start_hedgehog_container(network, netport, restport, gridnode_key)

if __name__ == "__main__":
    main()
