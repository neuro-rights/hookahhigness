import json
import web3
from web3 import Web3, HTTPProvider
#from solc import compile_source
from web3.contract import ConciseContract

import os
from typing import Dict, Any
from pathlib import Path
import requests
import vyper
import os, json

from dotenv import load_dotenv

load_dotenv()


class ContractUtils:
    """

    Attributes
    ----------
    """
    """
    Methods
    -------
    """

    def __init__(self):
        """
        Class init
        """
        
        self.INFURA_KEY = None #config["infura_ethereum_project_id"]
        #
        self.contract_address = None #config["auction_contract_address"]
        self.network = None #config["network"]
        self.ABI = None
        self.BYTECODE = None
        self.CODE_NFT = None
        self.CHAIN_ID = None
        self.w3 = None
        self.open_sea_url = ""
        self.scan_url = ""

    def load_json_etherscan(self, contract_address):
        """
        Purpose:
            Load json files
        Args:
            path_to_json (String): Path to  json file
        Returns:
            Conf: JSON file if loaded, else None
        """

        try:
            import urllib3
            import urllib.parse
            import json

            ETHERSCAN_ENDPOINT = "https://api-goerli.etherscan.io/api"

            params = {
                'module': 'contract',
                'action': 'getabi',
                'address': contract_address,
                'apiKey': 'CC5D165SJ3ITQ5NXF1ZBZ8MY5NGN61YZ63'
            }

            #print(ETHERSCAN_ENDPOINT)
            http = urllib3.PoolManager()
            r = http.request('GET', ETHERSCAN_ENDPOINT, fields=params)
            conf = json.loads(r.data.decode('utf-8'))['result']
            print(conf)
            return conf

        except Exception as error:
            print(error)
            raise TypeError("Invalid JSON file")


    def fetch_abi(self, address):
        """
        """
        ABI_ENDPOINT = 'https://api-goerli.etherscan.io/api?module=contract&action=getabi&address='
        response = requests.get('%s%s'%(ABI_ENDPOINT, address))
        response_json = response.json()
        abi_json = json.loads(response_json['result'])
        result = json.dumps(abi_json)
        print("result: "+result)
        return result

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
        #
        self.INFURA_KEY = config["infura_ethereum_project_id"]
        self.contract_address = config["contract_address"]
        self.network = config["network"]
        self.PUBLIC_KEY = config["seller_ethereum_wallet_address"]
        self.PRIVATE_KEY = config["buyer_ethereum_wallet_private_key"]

        if self.network == "goerli":

            GOERLI_API_URL = f"https://goerli.infura.io/v3/{self.INFURA_KEY}"
            self.w3 = Web3(Web3.HTTPProvider(GOERLI_API_URL))
            self.CHAIN_ID = 5 
            self.open_sea_url = f"https://testnets.opensea.io/collections/{self.contract_address}/"
            self.scan_url = "https://goerli.etherscan.io/tx/"
        #
        elif self.network == "mumbai":
            MUMBAI_API_URL = f"https://polygon-mumbai.infura.io/v3/{self.INFURA_KEY}"
            self.w3 = Web3(Web3.HTTPProvider(MUMBAI_API_URL))
            self.CHAIN_ID = 80001
            self.open_sea_url = f"https://testnets.opensea.io/collections/{self.contract_address}/"
            self.scan_url = "https://explorer-mumbai.maticvigil.com/tx/"
        #
        elif self.network == "matic_main":
            POLYGON_API_URL = f"https://polygon-mainnet.infura.io/v3/{self.INFURA_KEY}"
            self.w3 = Web3(Web3.HTTPProvider(POLYGON_API_URL))
            self.CHAIN_ID = 137
            self.open_sea_url = f"https://opensea.io/collections/matic/{self.contract_address}/"
            self.scan_url = "https://polygonscan.com/tx/"
        #
        else:
            print("Invalid network")
            raise ValueError(f"Invalid {network}")
        #
        print(f"checking if connected to infura...{self.w3.isConnected()}")
        


    def transfer(self, sender_public_key, sender_private_key, recipient_public_key, amount_to_transfer):
        """ """
        #
        #get the nonce.  Prevents one from sending the transaction twice
        nonce = self.w3.eth.getTransactionCount(sender_public_key)
        acct = self.w3.eth.account.privateKeyToAccount(self.PRIVATE_KEY)
        #build a transaction in a dictionary
        tx = {
            'nonce': nonce,
            'from': acct.address,
            'to': recipient_public_key,
            'value': self.w3.toWei(amount_to_transfer, 'ether'),
            "gas": 10000000,
            #'gas': 2000000,
            'gasPrice': self.w3.toWei('1', 'gwei')
        }

        #sign the transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, sender_private_key)
        #send transaction
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        #get transaction hash
        print(self.w3.toHex(tx_hash))
        hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        #
        print(f"transfer txn hash: {hash} ")
        transfer_receipt = self.w3.eth.wait_for_transaction_receipt(hash)  # hmmm have to wait...
        print(transfer_receipt)
        #hex_tokenid = receipt["logs"][0]["topics"][3].hex()  # this is token id in hex
        # convert from hex to decmial
        #tokenid = int(hex_tokenid, 16)
        tx_id = 1 #transfer_receipt["transactionIndex"]
        #
        return hash, tx_id


    def web3_mint(self, contract_address, contract_owner_address, contract_owner_private_key, buyer_address, buyer_private_key, amount_to_transfer, token_id):
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
        
        self.ABI = self.load_json_etherscan(contract_address)
        print(self.ABI)
        self.CODE_NFT = self.w3.eth.contract(address=contract_address, abi=self.ABI)
        acct = self.w3.eth.account.privateKeyToAccount(buyer_private_key)
        print(acct.address)
        # get the nonce
        nonce = self.w3.eth.getTransactionCount(acct.address)
        print("Nonce:", nonce)

        #tokenUri = "https://gateway.pinata.cloud/ipfs/QmYueiuRNmL4MiA2GwtVMm6ZagknXnSpQnB3z2gWbz36hP"
        # Build the transaction
        # 'gas' is the gas fee you pay in Wei (in this case, 1,000,000 Wei = 0.000000000001 ETH)
        # 'value' is the amount you pay to mint the token (in this case, 10 Finney = 0.01 ETH)
        tx = self.CODE_NFT.functions.mint(acct.address, token_id).buildTransaction({
            'gas': 1000000,
            'gasPrice': self.w3.toWei('1', 'gwei'),
            'from': contract_owner_address,
            'nonce': nonce,
            'value': self.w3.toWei(amount_to_transfer, 'ether'),
        })

        # Sign the transaction
        print("Signing transaction")
        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=contract_owner_private_key)
        # Process the transaction
        print("Sending transaction")
        txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # Print the confirmed transaction hash
        print("Transaction Successful!\nTransaction Hash:")
        print(self.w3.toHex(txn_hash))
        return self.w3.toHex(txn_hash)


    def compile_contract(self, contract_file):
        """
        You need a Vyper file, the name that you want to give to your smart contract, and the output JSON file.
        The following code will do this task:
        """
        filename = contract_file
        contract_name = Path(contract_file).stem

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
        self.ABI = smart_contract_json['abi']
        self.BYTECODE = smart_contract_json['bytecode']


    def deploy_contract(self):
        """ """
        acct = self.w3.eth.account.privateKeyToAccount(self.PRIVATE_KEY)
        print(acct.address)
        self.CODE_NFT = self.w3.eth.contract(abi=self.ABI, bytecode=self.BYTECODE)
        construct_txn = self.CODE_NFT.constructor().buildTransaction({
            'from': acct.address,
            'nonce': self.w3.eth.getTransactionCount(acct.address),
            'gas': 1728712,
            'gasPrice': self.w3.toWei('21', 'gwei')})

        signed = acct.signTransaction(construct_txn)
        tx_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        # Wait for the transaction to be mined, and get the transaction receipt
        print("Waiting for transaction to finish...")
        transaction_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")
        return transaction_receipt.contractAddress


    def deploy_lottery(self):
        """ """
        acct = self.w3.eth.account.privateKeyToAccount(self.PRIVATE_KEY)
        print(acct.address)
        
            
        smart_contract_json = self.compile_contract("contracts/interfaces/AggregatorV3Interface.vy")
        aggregator_contract_address = self.deploy_contract()

        smart_contract_json = self.compile_contract("contracts/interfaces/VRFCoordinatorV2Interface.vy")
        vrf_coordinator_contract_address = self.deploy_contract()

        smart_contract_json = self.compile_contract("contracts/Lottery.vy")

        self.CODE_NFT = self.w3.eth.contract(abi=self.ABI, bytecode=self.BYTECODE)
        construct_txn = self.CODE_NFT.constructor(aggregator_contract_address, vrf_coordinator_contract_address).buildTransaction({
            'from': acct.address,
            'nonce': self.w3.eth.getTransactionCount(acct.address),
            'gas': 1728712,
            'gasPrice': self.w3.toWei('21', 'gwei')})

        signed = acct.signTransaction(construct_txn)
        tx_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        # Wait for the transaction to be mined, and get the transaction receipt
        print("Waiting for transaction to finish...")
        transaction_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")

        self.CODE_NFT = self.w3.eth.contract(address=transaction_receipt.contractAddress, abi=self.ABI)
        self.CODE_NFT.functions.startLottery().call({"from": acct.address})
        return transaction_receipt.contractAddress

    def verify_contract(self):
        """ """
        networks = {
            "main": "https://api.etherscan.io/",
            "goerli": "https://api-goerli.etherscan.io/",
            "kovan": "https://api-kovan.etherscan.io/",
            "ropsten": "https://api-ropsten.etherscan.io/",
            "sepolia": "https://api-sepolia.etherscan.io/"
        }

        req = {
            "apikey": "",
            "module": "contract",
            "action": "verifysourcecode",
            "contractaddress": "",
            "sourceCode": "",
            "codeformat": "",
            "contractname": "",
            "compilerversion": "",
            "optimizationUsed": "",
            "runs": 200,
            "constructorArguements": "",
            "evmversion": "",
            "licenseType": ""
        }

        network_endpoint = networks["goerli"]
        x = requests.post(network_endpoint, data=req)
