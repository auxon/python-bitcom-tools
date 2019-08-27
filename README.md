# python-bitcom-tools

Tools and scripts to experiment with Bitcoin style OP_RETURN protocols as described here:

https://bitcom.bitdb.network

Also see related Metanet OP_RETURN experiments:

https://github.com/bitcartel/python-metanet-tools

## Installation

Requirements:
- BitcoinSV node (v0.2.1 or later)
  - If a local BitcoinSV node is not available, transaction data can be retrieved from an online blockchain explorer.
- Python 3

Dependencies to install:

```
pip3 install python-bitcoinrpc
```

## Usage

### peek.py

The purpose of `peek.py` is to help developers decode Bitcom style OP_RETURN protocols.

Currently supported protocols include:
- B://
- D://
- Author identity
- MAP

The pipeline operator '|' is also supported so protocols made up of subprotocols can be decoded, such as the TonicPOW protocol: `B | MAP`.

To run `peek.py` without using a local Bitcoin node, pass the option `-w main` to retrieve mainnet transaction data from the online explorer whatsonchain.com.

```
$ python3 peek.py -w main a610a733223f2ab9e0a67b22b519ce4adbd439e1ceb26a5d41873dd64fa5b1b7

Tx output index: 0
Number of elements: 24
----------------------------------------
Protocol: B://
Prefix: 19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut
Data: 10813 bytes
Media type: image/png
Encoding: binary
Filename: satchmo_was_here.png
----------------------------------------
| (pipe)
----------------------------------------
Protocol: Magic Attribute
Prefix: 1PuQa7K62MiKCtssSLKy1kh56WWU7MtUR5
Action: SET
app: tonicpow
type: campaign_request
site_pub_key: 1PuQa7K62MiKCtssSLKy1kh56WWU7MtUR5
ad_unit_id: ad-unit-id
affiliate_pub_key: 00
num_blocks: 1
ad_type: display
cta_url: https://faucet.allaboard.cash
```

When running a local Bitcoin node, use command line options `user`, `password`, `mainnet` to override default configuration settings in the script.

```
usage: peek.py [-h] [-w {main,test,stn}] [-u USER] [-p PASSWORD] [-m] txid

Show OP_RETURN data for Bitcom style protocols: AIP, B, D, MAP, |

positional arguments:
  txid                  txid of transaction

optional arguments:
  -h, --help            show this help message and exit
  -w {main,test,stn}, --whatsonchain {main,test,stn}
                        Get transaction data from whatsonchain.com
  -u USER, --user USER  rpcuser
  -p PASSWORD, --password PASSWORD
                        rpcpassword
  -m, --mainnet         use mainnet (default is testnet)
```
