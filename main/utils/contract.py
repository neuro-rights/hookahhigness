import json
import os
from typing import Dict, Any
from web3 import Web3
from pathlib import Path
import requests
import vyper
import os, json

from dotenv import load_dotenv

load_dotenv()


def compile_contract(contract_file):
    """
    You need a Vyper file, the name that you want to give to your smart contract, and the output JSON file.
    The following code will do this task:
    """
    filename = contract_file
    contract_name = Path(contract_file).stem
    contract_json_file = open('compiled.json'.format(contract_name), 'w')

    # Use the following lines of code to get the content of the Vyper file:
    with open(filename, 'r') as f:
        content = f.read()

    # Then you create a dictionary object where the key is a path to your Vyper
    # file and the value is the content of the Vyper file, as follows:
    current_directory = os.curdir
    smart_contract = {}
    smart_contract[current_directory] = content

    # To compile the Vyper code, all you need to do is use the compile_codes method from the vyper module, as follows:
    format = ['abi', 'bytecode']
    compiled_code = vyper.compile_codes(smart_contract, format, 'dict')

    smart_contract_json = {
        'contractName': contract_name,
        'abi': compiled_code[current_directory]['abi'],
        'bytecode': compiled_code[current_directory]['bytecode']
    }

    # The last code is used to write the result to an output JSON file:
    json.dump(smart_contract_json, contract_json_file)
    contract_json_file.close()


def deploy_contract():
    """ """

    # 1. Import the ABI and bytecode
    from .compiled import abi, bytecode

    # 2. Add the Web3 provider logic here:
    web3 = Web3(Web3.HTTPProvider(RPC_API_URL))
    # {...}

    # 3. Create address variable
    account_from = {
        'private_key': request.user.ethereum_wallet_private_key,
        'address': request.user.ethereum_wallet_address,
    }

    print(f'Attempting to deploy from account: { account_from["address"] }')

    # 4. Create contract instance
    Incrementer = web3.eth.contract(abi=abi, bytecode=bytecode)

    # 5. Build constructor tx
    construct_txn = Incrementer.constructor(5).buildTransaction(
        {
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )

    # 6. Sign tx with PK
    tx_create = web3.eth.account.sign_transaction(construct_txn, account_from['private_key'])

    # 7. Send tx and wait for receipt
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Contract deployed at address: { tx_receipt.contractAddress }')
    return tx_receipt.contractAddress


def deploy_contract_2():
    """ """

    w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/YOUR_PROJECT_ID"))

    contract_ = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin'])

    acct = w3.eth.account.privateKeyToAccount(privateKey)

    construct_txn = contract_.constructor().buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    signed = acct.signTransaction(construct_txn)

    w3.eth.sendRawTransaction(signed.rawTransaction)



class ContractUtils:
    """

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self):
        """Class init"""

    def load_json(self, contract_address):
        """
        Purpose:
            Load json files
        Args:
            path_to_json (String): Path to  json file
        Returns:
            Conf: JSON file if loaded, else None
        """

        try:
            ABI_ENDPOINT = "https://api-goerli.etherscan.io/api?module=contract&action=getabi&address=0x923604edF1463a5a87eE9158b09bb86c05f41dc0&apiKey=CC5D165SJ3ITQ5NXF1ZBZ8MY5NGN61YZ63"

            import urllib3
            import json

            http = urllib3.PoolManager()
            r = http.request('GET', ABI_ENDPOINT)
            conf = json.loads(r.data.decode('utf-8'))['result']
            print(conf)
            return conf

        except Exception as error:
            print(error)
            raise TypeError("Invalid JSON file")

    def set_up_blockchain(self, config):
        """
        Purpose:
        Setup all blockchain items
        Args:
            config
        Returns:
            Conf: JSON file if loaded, else None
        """
        #
        ############ Ethereum Setup ############
        PUBLIC_KEY = config["seller_ethereum_wallet_address"]
        PRIVATE_KEY = Web3.toBytes(hexstr=config["seller_ethereum_wallet_private_key"])
        INFURA_KEY = config["seller_infura_ethereum_project_id"]
        #
        contract = config["auction_contract_address"]
        network = config["network"]
        ABI = None
        CODE_NFT = None
        CHAIN_ID = None
        w3 = None
        open_sea_url = ""
        scan_url = ""
        eth_json = {}
        #
        print(config)
        if network == "rinkeby":

            RINK_API_URL = f"https://rinkeby.infura.io/v3/{INFURA_KEY}"
            w3 = Web3(Web3.HTTPProvider(RINK_API_URL))
            ABI = self.load_json(config["auction_contract_address"])["abi"]  # get the ABI
            CODE_NFT = w3.eth.contract(address=contract, abi=ABI)  # The contract
            CHAIN_ID = 4
            open_sea_url = f"https://testnets.opensea.io/assets/{contract}/"
            scan_url = "https://rinkeby.etherscan.io/tx/"
        #
        elif network == "goerli":

            GOERLI_API_URL = f"https://goerli.infura.io/v3/{INFURA_KEY}"
            w3 = Web3(Web3.HTTPProvider(GOERLI_API_URL))
            ABI = self.load_json(config["auction_contract_address"])  # get the ABI
            CODE_NFT = w3.eth.contract(address=contract, abi=ABI)  # The contract
            CHAIN_ID = 5 
            open_sea_url = f"https://testnets.opensea.io/assets/{contract}/"
            scan_url = "https://rinkeby.etherscan.io/tx/"
        #
        elif network == "mumbai":
            MUMBAI_API_URL = f"https://polygon-mumbai.infura.io/v3/{INFURA_KEY}"
            w3 = Web3(Web3.HTTPProvider(MUMBAI_API_URL))
            ABI = self.load_json(config["auction_contract_address"])["abi"]  # get the ABI
            CODE_NFT = w3.eth.contract(address=contract, abi=ABI)  # The contract
            CHAIN_ID = 80001
            open_sea_url = f"https://testnets.opensea.io/assets/{contract}/"
            scan_url = "https://explorer-mumbai.maticvigil.com/tx/"
        #
        elif network == "matic_main":
            POLYGON_API_URL = f"https://polygon-mainnet.infura.io/v3/{INFURA_KEY}"
            w3 = Web3(Web3.HTTPProvider(POLYGON_API_URL))
            ABI = self.load_json(config["auction_contract_address"])["abi"]  # get the ABI
            CODE_NFT = w3.eth.contract(address=contract, abi=ABI)  # The contract
            CHAIN_ID = 137
            open_sea_url = f"https://opensea.io/assets/matic/{contract}/"
            scan_url = "https://polygonscan.com/tx/"
        #
        else:
            print("Invalid network")
            raise ValueError(f"Invalid {network}")
        #
        print(f"checking if connected to infura...{w3.isConnected()}")
        #
        eth_json["w3"] = w3
        eth_json["contract"] = CODE_NFT
        eth_json["chain_id"] = CHAIN_ID
        eth_json["open_sea_url"] = open_sea_url
        eth_json["scan_url"] = scan_url
        eth_json["public_key"] = PUBLIC_KEY
        eth_json["private_key"] = PRIVATE_KEY
        #
        return eth_json

    def web3_mint(self, userAddress, tokenURI, eth_json):
        """
        Purpose:
            mint a token for user on blockchain
        Args:
            userAddress - the user to mint for
            tokenURI - metadat info for NFT
            eth_json - blockchain info
        Returns:
            hash - txn of mint
            tokenid - token minted
        """

        PUBLIC_KEY = eth_json["public_key"]
        CHAIN_ID = eth_json["chain_id"]
        w3 = eth_json["w3"]
        CODE_NFT = eth_json["contract"]
        PRIVATE_KEY = eth_json["private_key"]
        #
        nonce = w3.eth.get_transaction_count(PUBLIC_KEY)
        # Create the contracrt
        mint_txn = CODE_NFT.functions.mint(userAddress, tokenURI).buildTransaction(
            {
                "chainId": CHAIN_ID,
                "gas": 10000000,
                "gasPrice": w3.toWei("1", "gwei"),
                "nonce": nonce,
            }
        )
        #
        signed_txn = w3.eth.account.sign_transaction(mint_txn, private_key=PRIVATE_KEY)
        w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        hash = w3.toHex(w3.keccak(signed_txn.rawTransaction))
        #
        print(f"mint txn hash: {hash} ")
        receipt = w3.eth.wait_for_transaction_receipt(hash)  # hmmm have to wait...
        print(receipt)
        hex_tokenid = receipt["logs"][0]["topics"][3].hex()  # this is token id in hex
        # convert from hex to decmial
        tokenid = int(hex_tokenid, 16)
        print(f"Got tokenid: {tokenid}")
        #
        return hash, tokenid
