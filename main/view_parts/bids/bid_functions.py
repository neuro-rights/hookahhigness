# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...utils.nft import NFTUtils
from ...utils.contract import ContractUtils

#
from ..utils.pagination import *

#
from ...forms import PurchaseForm, BidForm
from ...models import User, Bid, Purchase, Nft

from web3 import Web3
import requests
import json

def mint_nft(request, nft_uuid):
    """ """
    
    nft = Nft.objects.get(uuid=nft_uuid)

    INFURA_KEY = request.user.infura_ethereum_secret_key
    RINK_API_URL = f"https://rinkeby.infura.io/v3/{INFURA_KEY}"
    print(RINK_API_URL)
    w3 = Web3(Web3.HTTPProvider(RINK_API_URL))
    #w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))  # web3 must be called locally
    assert True is w3.isConnected()
    print('Network connected')

    # should be in auction model
    contract_address = "0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87"
    # To get ABI vyper -f abi contracts/ERC721.vy
    """
    ABI_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getabi&apiKey=CN1JPCAH2J5FZ189F18ATZXJ8NE7JTPCZ2&address="
    response = requests.get('%s%s'%(ABI_ENDPOINT, contract_address))
    response_json = response.json()
    print(response_json)
    abi_json = json.loads(response_json['result'])
    """
    abi_json = '[{"name": "Transfer", "inputs": [{"name": "sender", "type": "address", "indexed": true}, {"name": "receiver", "type": "address", "indexed": true}, {"name": "tokenId", "type": "uint256", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "Approval", "inputs": [{"name": "owner", "type": "address", "indexed": true}, {"name": "approved", "type": "address", "indexed": true}, {"name": "tokenId", "type": "uint256", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "ApprovalForAll", "inputs": [{"name": "owner", "type": "address", "indexed": true}, {"name": "operator", "type": "address", "indexed": true}, {"name": "approved", "type": "bool", "indexed": false}], "anonymous": false, "type": "event"}, {"stateMutability": "nonpayable", "type": "constructor", "inputs": [], "outputs": []}, {"stateMutability": "pure", "type": "function", "name": "supportsInterface", "inputs": [{"name": "interface_id", "type": "bytes4"}], "outputs": [{"name": "", "type": "bool"}]}, {"stateMutability": "view", "type": "function", "name": "balanceOf", "inputs": [{"name": "_owner", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}]}, {"stateMutability": "view", "type": "function", "name": "ownerOf", "inputs": [{"name": "_tokenId", "type": "uint256"}], "outputs": [{"name": "", "type": "address"}]}, {"stateMutability": "view", "type": "function", "name": "getApproved", "inputs": [{"name": "_tokenId", "type": "uint256"}], "outputs": [{"name": "", "type": "address"}]}, {"stateMutability": "view", "type": "function", "name": "isApprovedForAll", "inputs": [{"name": "_owner", "type": "address"}, {"name": "_operator", "type": "address"}], "outputs": [{"name": "", "type": "bool"}]}, {"stateMutability": "payable", "type": "function", "name": "transferFrom", "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_tokenId", "type": "uint256"}], "outputs": []}, {"stateMutability": "payable", "type": "function", "name": "safeTransferFrom", "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_tokenId", "type": "uint256"}], "outputs": []}, {"stateMutability": "payable", "type": "function", "name": "safeTransferFrom", "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_tokenId", "type": "uint256"}, {"name": "_data", "type": "bytes"}], "outputs": []}, {"stateMutability": "payable", "type": "function", "name": "approve", "inputs": [{"name": "_approved", "type": "address"}, {"name": "_tokenId", "type": "uint256"}], "outputs": []}, {"stateMutability": "nonpayable", "type": "function", "name": "setApprovalForAll", "inputs": [{"name": "_operator", "type": "address"}, {"name": "_approved", "type": "bool"}], "outputs": []}, {"stateMutability": "nonpayable", "type": "function", "name": "mint", "inputs": [{"name": "_to", "type": "address"}, {"name": "_tokenId", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}]}, {"stateMutability": "nonpayable", "type": "function", "name": "burn", "inputs": [{"name": "_tokenId", "type": "uint256"}], "outputs": []}, {"stateMutability": "view", "type": "function", "name": "tokenURI", "inputs": [{"name": "tokenId", "type": "uint256"}], "outputs": [{"name": "", "type": "string"}]}]'

    contract_instance = w3.eth.contract(address=contract_address, abi=abi_json)

    print('Contract Instantiated')
    print(nft.token_id)

    buyer = request.user.ethereum_wallet_address
    seller = nft.creator.ethereum_wallet_address
    # Both raise error
    #seller_balance = contract_instance.functions.balanceOf(seller).call()
    print(seller) 
    #buyer_balance = contract_instance.functions.balanceOf(buyer).call()
    print(buyer) 
    # Change tokenId to avoid error
    result = contract_instance.functions.mint(seller, 1).call()

    time.sleep(60)
    #new_seller_balance = contract_instance.functions.balanceOf(seller)
    #assert new_human_0_balance == human_0_balance + 1


@login_required
def bid_accept(request, bid_uuid):
    """ """

    bid = Bid.objects.get(uuid=bid_uuid)
    bid_form = BidForm()
    #
    try:
        #
        contract_address = bid.auction.contract_address
        contract_abi = bid.auction.contract_abi 
        #
        user_wallet = request.user.ethereum_wallet_address 
        #
        """
        nftutils = ContractUtils()
        config={
                'seller_ethereum_wallet_address':bid.auction.seller.ethereum_wallet_address,
                'seller_ethereum_wallet_private_key':bid.auction.seller.ethereum_wallet_private_key,
                'network':bid.auction.network, 
                'auction_contract_address':bid.auction.contract_address, 
                'auction_contract_abi':bid.auction.contract_abi
            }
        print(config)
        bc_setup = nftutils.set_up_blockchain(config)
        print(bid.uuid)
        tx_hash, tx_token = nftutils.web3_mint(
            userAddress=user_wallet,
            tokenURI=nft_metadata_uri,
            eth_json=bc_setup,
        )
        #
        """
        for asset in bid.auction.assets.all():
            print(asset)
            for nft in asset.nfts.all():
                print(nft)
                mint_nft(request=request, nft_uuid=nft.uuid)
                new_purchase = Purchase(commit=False)
                #new_purchase.bid_id = bid_id
                #new_purchase.tx_hash = tx_hash
                #new_purchase.tx_token = tx_token
                new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
    #
    return render(
        request, "auctions/detail.html", {"auction": bid.auction, "bid_form": bid_form}
    )


@login_required
def bid_reject(request, bid_id):
    #
    bid = Bid.objects.get(id=bid_id)
    bid_nft_id = bid.nft.id
    try:
        #
        bid.delete()
        #
    except Exception as err:
        #
        print("Failed to delete Bid: {}".format(err))
    #
    return redirect("nft_detail", nft_id=bid_nft_id)


@login_required
def dafuq(request, bid_id):
    #
    bid = Bid.objects.get(id=bid_id)
    form = PurchaseForm(request.POST)
    #
    if form.is_valid():
        new_purchase = form.save(commit=False)
        new_purchase.bid_id = bid_id
        new_purchase.save()
        return redirect("auction_detail", auction_id=bid.auction_id)
    #
    context = {"bid": bid_id, "form": form}
    return render(request, "main/purchase_form.html", context)
