#!/usr/bin/env python3
import argparse
import json, urllib.request
from bitcoinrpc.authproxy import AuthServiceProxy

# Show OP_RETURN data for Bitcom style protocols.
#
# Author Identity protocol:
#   https://github.com/BitcoinFiles/AUTHOR_IDENTITY_PROTOCOL
#   d4738845dc0d045a35c72fcacaa2d4dee19a3be1cbfcb0d333ce2aec6f0de311
# B:// protocol:
#   https://github.com/unwriter/B
#   e29ea668ac505e971cdd383778284aa6b120f34f509270bd39065a20eb68f151
# D:// protocol:
#   https://github.com/bitcoineler/D
#   329eacb2d1ab8770ac01d2daa13a852d72282379ea26caca1729817315fb12b0
# Magic Attribute protocol:
#   https://github.com/rohenaz/MAP
#   a610a733223f2ab9e0a67b22b519ce4adbd439e1ceb26a5d41873dd64fa5b1b7
# | pipeline:
#   https://github.com/unwriter/Bitcom/issues/2
#   d4738845dc0d045a35c72fcacaa2d4dee19a3be1cbfcb0d333ce2aec6f0de311

# Globals to override from command-line
RPCUSER='user'
RPCPASSWORD='password'
RPCPORT=18332 # Testnet 18332, Mainnet 8332
WHATSONCHAINNETWORK=None

def main(txid):
    tx = {}
    if WHATSONCHAINNETWORK is not None:
        url = "https://api.whatsonchain.com/v1/bsv/{}/tx/hash/{}".format(WHATSONCHAINNETWORK, txid)
        try:
            response = urllib.request.urlopen(url).read()
            tx = json.loads(response.decode('utf-8'))
        except Exception as e:
            print('Error:', e)
            return
    else:
        bitcoin = AuthServiceProxy("http://{}:{}@127.0.0.1:{}".format(RPCUSER, RPCPASSWORD, RPCPORT))
        tx = bitcoin.getrawtransaction(txid, 1)

    script = b''
    vout_n = 0
    for vout in tx["vout"]:
        vout_n = vout['n']
        script = bytes.fromhex(vout["scriptPubKey"]["hex"])
        # Check for OP_RETURN
        if script[0] == 0x6a:
            break
        script = None

    # Retrieve OP_RETURN data elements
    # TODO:
    elements = []
    if script:
        pos = 1
        while pos < len(script):
            c = script[pos]
            pos = pos + 1
            if c <= 0x4b:
                elements.append(script[pos:pos+c])
                pos = pos + c
            elif c == 0x4c:
                size = script[pos]
                elements.append(script[pos+1:pos+1+size])
                pos = pos + 1 + size
            elif c == 0x4d:
                size = int.from_bytes(script[pos:pos+2], byteorder='little')
                elements.append(script[pos+2:pos+2+size])
                pos = pos + 2 + size
            elif c == 0x4e:
                size = int.from_bytes(script[pos:pos+4], byteorder='little')
                elements.append(script[pos+4:pos+4+size])
                pos = pos + 4 + size
            else:
                print("Unsupported opcode:", c)
                break
    else:
        print("Transaction does not contain any OP_RETURN data")
        return

    print("Tx output index:", vout_n)
    print("Number of elements:", len(elements))
    i=0
    while i < len(elements):
        print('-'*40)
        prefix = elements[i].decode('utf-8')
        if prefix == "19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut":
            print("Protocol: B://")
            print("Prefix:", prefix)
            print("Data:", len(elements[i+1]), "bytes")
            print("Media type:", elements[i+2].decode('utf-8'))
            # Option fields
            if len(elements) > i + 3:
                print("Encoding:", elements[i+3].decode('utf-8'))
            if len(elements) > i + 4:
                print("Filename:", elements[i+4].decode('utf-8'))
            i = i + 5
        elif prefix == "15PciHG22SNLQJXMoSUaWVi7WSqc7hCfva":
            print("Protocol: Author Identity")
            print("Prefix:", prefix)
            print("Signing Algorithm:", elements[i+1].decode('utf-8'))
            print("Signing Address:", elements[i+2].decode('utf-8'))
            print("Signature:", elements[i+3].hex())
            i = i + 4
            # Optional field indexes
            while i < len(elements):
                data = elements[i]
                if data == b'|':
                    break
                print("Field Index: 0x{} ({})".format(data.hex(), int.from_bytes(data, byteorder='little')))
                # AIP does not specify width of index value or endianness, use OP_RETURN conventions
                i = i + 1            
        elif prefix == "1PuQa7K62MiKCtssSLKy1kh56WWU7MtUR5":
            print("Protocol: Magic Attribute")
            print("Prefix:", prefix)
            print("Action:", elements[i+1].decode('utf-8'))
            i = i + 2
            while i < len(elements):
                key = elements[i]
                if key == b'|' or i+1 > len(elements): # malformed key-value pair if > len
                    break
                value = elements[i+1]
                print("{}: {}".format(key.decode('utf-8'), value.decode('utf-8')))
                i = i + 2
        elif prefix == "19iG3WTYSsbyos3uJ733yK4zEioi1FesNU":
            print("Protocol: D://")
            print("Prefix:", prefix)
            print("Key:", elements[i+1].decode('utf-8'))
            print("Value:", elements[i+2].decode('utf-8'))
            print("Type:", elements[i+3].decode('utf-8'))
            print("Sequence:", elements[i+4].decode('utf-8'))
            i = i + 5
        elif prefix == '|':
            print("| (pipe)")
            i = i + 1
        else:
            print("Protocol: Unknown")
            print("Prefix:", prefix)
            i = i + 1
            while i < len(elements):
                data = elements[i]
                if data == b'|':
                    break
                print("Unknown field:", data)
                i = i + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show OP_RETURN data for Bitcom style protocols: AIP, B, D, MAP, |")
    parser.add_argument("txid", help="txid of transaction")
    parser.add_argument("-w", "--whatsonchain", choices=['main','test','stn'], help="Get transaction data from whatsonchain.com")
    parser.add_argument_group()
    parser.add_argument("-u", "--user", help="rpcuser")
    parser.add_argument("-p", "--password", help="rpcpassword")
    parser.add_argument("-m", "--mainnet", help="use mainnet (default is testnet)", action="store_true", default=False)
    args = parser.parse_args()
    if args.user:
        RPCUSER = args.user
    if args.password:
        RPCPASSWORD = args.password
    if args.mainnet:
        RPCPORT = 8332
    if args.whatsonchain:
        WHATSONCHAINNETWORK = args.whatsonchain
    main(args.txid)
