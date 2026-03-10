# CS 216: Bitcoin Transaction Lab Assignment

## Team Information
| Name | Roll No. |
| :--- | :--- |
| Srigiri Sairaj | 240001070 |
| Donthula Manish | 240001029 |
| Gunala Kushal Goud | 240001033 |
| Sarath Chandra Jandhyala | 240041020 |

## Project Objective
The primary aim of this project is to explore the mechanics of creating, signing, and validating Bitcoin transactions across two different address formats: Legacy (P2PKH) and SegWit (P2SH-P2WPKH). Using a local `bitcoind` node in `regtest` mode and automating the transaction workflow, this project analyzes the challenge and response scripts using the `btcdeb` debugger to verify execution, and mathematically demonstrates how the Segregated Witness soft fork reduces transaction fees and resolves third-party malleability.

## Prerequisites
- **Bitcoin Core (`bitcoind` & `bitcoin-cli`)**: Required to run a full node implementation of Bitcoin.
  - **Note**: The Bitcoin Qt application is unnecessary and if ran, downloads the entire blockchain. It is not required for this project.

- **Python 3.x**: For scripting and interacting with the `bitcoind` RPC interface.

- **Python `requests` Library**: Used for executing JSON-RPC calls to the local node.

- **Bitcoin Debugger (`btcdeb`)**: Necessary for debugging, validating, and decoding the challenge and response scripts.

## Configuration & Execution

### 1. Node Setup
Before executing `bitcoind` in `regtest` mode, configure your `bitcoin.conf` file with the following fee settings:

```ini
paytxfee = 0.0001
fallbackfee = 0.0002
mintxfee = 0.00001
txconfirmtarget = 6

```

Start the daemon in `regtest` mode. The scripts expect the node to be running on `127.0.0.1:18443`. Make sure to update the RPC credentials (`RPC_USER` and `RPC_PASS`) in `part1.py` to match your configuration.
#### For `Linux`
```bash
bitcoind -regtest -daemon
```

#### For `Windows`
```bash
bitcoind.exe -regtest
```
#### **Note**
If running `bitcoind --version` on the command prompt does not display the version, and you have installed the bitcoin core, make sure to add it inside the **path in environment variables**. The default path is `C:\Program Files\Bitcoin\daemon`. Once this has been added, restart your application and test again.


### 2. Running the Scripts

#### **Part 1 (Legacy P2PKH):**
```bash
python3 part1.py
```
This handles the creation, signing, and broadcasting of Legacy (P2PKH) Bitcoin transactions.

#### **Part 2 (SegWit P2SH-P2WPKH):**
```bash
python3 part2.py
```
This handles the creation, signing, and broadcasting of P2SH-wrapped SegWit transactions.

## Implementation Details

### Part 1: Legacy Address Transactions (P2PKH)

- **Workflow**: Creates a local Bitcoin node in `regtest` mode and generates three Legacy addresses (A, B, and C). Bitcoins are sent to Address A by mining blocks directly to it.


- **Transactions**: A transaction is created to send bitcoins from Address A to Address B, which is signed and broadcasted. The newly created UTXO at Address B is then used to send bitcoins to Address C.


- **Script Execution**: In a Legacy P2PKH transaction, the response script (`scriptSig`) provides the user's cryptographic `<Signature>` and `<Public Key>`. The challenge script (`scriptPubKey`) validates this by running `OP_DUP` to duplicate the public key, and `OP_HASH160` to hash it , followed by `OP_EQUALVERIFY` and `OP_CHECKSIG`.



### Part 2: SegWit P2SH-P2WPKH Transactions

- **Workflow**: Generates three new addresses (A', B', and C'), explicitly specifying the `p2sh-segwit` format. Bitcoins are sent Address A' by mining new blocks to it to avoid mixing with legacy UTXOs.


- **Transactions**: Similar to Part 1, bitcoins are sequentially transferred from Address A' to B', and then from B' to C'.


- **Script Execution**: The heavy cryptographic signatures are removed from the main script. The response script (`scriptSig`) only contains a lightweight `<Witness Program>`. The actual `<Signature>` and `<Public Key>` are stored in the separated `txinwitness` structure.

### Script Debugging with btcdeb (Explained in detail in the report)

## Comparative Analysis

### Size Metrics Comparison
| Metric | Legacy P2PKH (Part 1 Avg) | SegWit P2SH-P2WPKH (Part 2 Avg) | Difference |
| :--- | :--- | :--- | :--- |
| **Size (Raw Bytes)** | 225 bytes | 247 bytes | + 22 bytes (Larger) |
| **Weight Units (WU)** | 900 WU | 661 WU | - 239 WU (Lighter) |
| **Virtual Size (vbytes)** | 225 vbytes | 166 vbytes | - 59 vbytes (Smaller) |

### Key Findings
- **Witness Discount & Fee Reduction**: Although the SegWit transaction is physically larger (247 bytes vs 225 bytes) due to the P2SH wrapper, its virtual size is much smaller (166 vbytes vs 225 vbytes). This is because SegWit applies a 75% discount to the signature data stored in the `txinwitness` array. This mathematical reduction results in ~26% decrease on transaction fees for the user.

- **Resolving Transaction Malleability**: In Legacy transactions, signatures are part of the `scriptSig` and are hashed to generate the TXID, making them susceptible to third-party malleability. SegWit resolves this by separating the signatures into the `txinwitness` array, removing them from the TXID hash calculation. This allows Layer 2 scaling solutions like the Lightning Network to function safely.
