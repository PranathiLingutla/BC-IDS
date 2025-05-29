import csv
import os
import time
from brownie import IPBlacklist, accounts, network
from web3 import Web3

def ip_to_bytes32(ip_string):
    """Convert an IP string to bytes32 padded hex."""
    ip_bytes = Web3.to_bytes(text=ip_string)
    return Web3.to_hex(ip_bytes).ljust(66, '0')  # '0x' + 64 hex chars

def deploy_contract():
    """Deploys the IPBlacklist smart contract to Sepolia network."""
    if not network.is_connected():
        network.connect("sepolia")

    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable is missing!")

    account = accounts.add(private_key)

    contract = IPBlacklist.deploy({"from": account})
    print(f"\n Smart contract deployed at: {contract.address}\n")
    return contract, account

def upload_ips(contract, account):
    """Reads attack IPs from attack_ips_Combined_Dataset.xls and uploads them in batches."""
    csv_file = r"C:\Users\L.Pranathi\BC-IDSs\ml-IDS\attack_ips_Combined_Dataset.xls"
    source_ips = []
    destination_ips = []

    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                source_ip = row["Source IP"].strip()
                destination_ip = row["Destination IP"].strip()

                if source_ip and destination_ip:
                    source_ips.append(ip_to_bytes32(source_ip))
                    destination_ips.append(ip_to_bytes32(destination_ip))

        if source_ips and destination_ips:
            total_pairs = len(source_ips)
            print(f" Preparing to upload {total_pairs} IP pairs to the blockchain...")

            BATCH_SIZE = 200
            DELAY_BETWEEN_BATCHES = 0.15  # seconds

            for i in range(0, total_pairs, BATCH_SIZE):
                batch_source = source_ips[i:i+BATCH_SIZE]
                batch_destination = destination_ips[i:i+BATCH_SIZE]

                print(f" Uploading batch {i//BATCH_SIZE + 1} / {(total_pairs+BATCH_SIZE-1)//BATCH_SIZE} "
                      f"({len(batch_source)} pairs)")

                try:
                    tx = contract.batchUpdateIpList(batch_source, batch_destination, {"from": account})
                    tx.wait(1)
                    print(f" Batch {i//BATCH_SIZE + 1} uploaded. TxHash: {tx.txid}")
                except Exception as e:
                    print(f" Error uploading batch {i//BATCH_SIZE + 1}: {e}")

                time.sleep(DELAY_BETWEEN_BATCHES)

            print(" All IP pairs successfully uploaded in batches.")
        else:
            print(" No valid IP data found in the CSV file.")

    except FileNotFoundError:
        print(" Error: attack_ips_Combined_Dataset.xls not found! Make sure it exists at the specified path.")
    except Exception as e:
        print(f" Unexpected error: {e}")

def main():
    contract, account = deploy_contract()
    upload_ips(contract, account)
