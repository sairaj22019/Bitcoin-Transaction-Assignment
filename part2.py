"""
Part 2: P2SH-SegWit Address Transactions

Workflow: Similar to Part 1, but handles the creation, signing, and broadcasting of P2SH-wrapped SegWit(P2SH-P2WPKH) transactions. It uses Python's "subprocess" module to execute "bitcoin-cli" commands instead of direct RPC calls.

Execution:

1. Node Setup:
    - Uses "bitcoin-cli" commands with subprocess.

2. Address Generation & Initial Funding:
    - Generates three P2SH-SegWit addresses A', B', and C'.
    - Send bitcoins to Address A' by directly mining 101 blocks to it (instead of the "sendtoaddress" step from Part 1).

3. Transaction from A' to B':
    - Same process as Part 1, uses A's UTXO to create the transaction, extracts B's challenge script, signs, broadcasts, and mines 1 block for confirmation.

4. Transaction from B' to C':
    - Same process as Part 1, fetches B's new UTXO, creates the transaction to C', extracts the response script from the signed transaction, and broadcasts it.
"""

import subprocess
import json
import time

def run_cmd(cmd):
    """Executes a terminal command and returns the string output."""
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}\n{result.stderr}")
        exit(1)
    return result.stdout.strip()

def get_segwit_address():
    """Generates a P2SH-wrapped SegWit address."""
    # Here, Address type is "p2sh-segwit"
    return run_cmd('bitcoin-cli -regtest getnewaddress "" "p2sh-segwit"')

def mine_blocks(num_blocks, address):
    """Mines blocks to the specified address."""
    run_cmd(f'bitcoin-cli -regtest generatetoaddress {num_blocks} "{address}"')

def create_and_send_raw_tx(from_address, to_address, send_amount):
    """Automates the raw transaction workflow."""
    # Find an unspent UTXO for the sender
    unspent_out = run_cmd('bitcoin-cli -regtest listunspent')
    utxos = json.loads(unspent_out)
    
    selected_utxo = None
    for utxo in utxos:
        if utxo['address'] == from_address and utxo['amount'] >= send_amount + 0.001:
            selected_utxo = utxo
            break
            
    if not selected_utxo:
        print(f"No suitable UTXO found for {from_address}")
        exit(1)

    txid_in = selected_utxo['txid']
    vout_in = selected_utxo['vout']
    input_amount = selected_utxo['amount']
    
    fee = 0.00010000
    change_amount = round(input_amount - send_amount - fee, 8)

    inputs = json.dumps([{"txid": txid_in, "vout": vout_in}])
    outputs = json.dumps({to_address: send_amount, from_address: change_amount})
    raw_tx_hex = run_cmd(f"bitcoin-cli -regtest createrawtransaction '{inputs}' '{outputs}'")

    signed_tx_out = run_cmd(f'bitcoin-cli -regtest signrawtransactionwithwallet "{raw_tx_hex}"')
    signed_tx_hex = json.loads(signed_tx_out)['hex']

    final_txid = run_cmd(f'bitcoin-cli -regtest sendrawtransaction "{signed_tx_hex}"')
    return final_txid

print("--- Starting Part 2: SegWit P2SH-P2WPKH Transactions ---")

# Generate SegWit addresses
address_A = get_segwit_address()
address_B = get_segwit_address()
address_C = get_segwit_address()

print(f"Address A' (SegWit): {address_A}")
print(f"Address B' (SegWit): {address_B}")
print(f"Address C' (SegWit): {address_C}")

# Send bitcoins Address A'
print("\nFunding Address A' (mining 101 blocks)...")
mine_blocks(101, address_A)
time.sleep(2) # Allow node to process

# Transaction A' -> B' (Send 2 BTC)
print("\nCreating Transaction A' -> B'...")
txid_AB = create_and_send_raw_tx(address_A, address_B, 2.0)
print(f"Broadcasted A' -> B'. TXID: {txid_AB}")
mine_blocks(1, address_A)
time.sleep(2)

# Transaction B' -> C' (Send 1 BTC)
print("\nCreating Transaction B' -> C'...")
txid_BC = create_and_send_raw_tx(address_B, address_C, 1.0)
print(f"Broadcasted B' -> C'. TXID: {txid_BC}")
mine_blocks(1, address_A)

print("\n--- Part 2 Script Complete! ---")
print("Save these TXIDs for your report:")
print(f"A' -> B' TXID: {txid_AB}")
print(f"B' -> C' TXID: {txid_BC}")