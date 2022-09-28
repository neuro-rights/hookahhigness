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
from ...forms import PurchaseForm
from ...models import User, Bid, Purchase


def mint_nft(request, nft_uuid):
    """ """
    
    nft = Nft.objects.get(uuid=nft_uuid)

    w3 = Web3(HTTPProvider('http://localhost:8545'))  # web3 must be called locally
    assert True is w3.isConnected()
    print('Network connected')

    # should be in auction model
    contract_address = "0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87"
    
    # To get ABI vyper -f abi contracts/ERC721.vy
    ABI_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getabi&address="
    response = requests.get('%s%s'%(ABI_ENDPOINT, contract_address))
    response_json = response.json()
    abi_json = json.loads(response_json['result'])
    contract_instance = w3.eth.contract(address=address, abi=abi_json)

    buyer = request.user.ethereum_wallet_address
    seller = nft.creator.ethereum_wallet_address
    # Both raise error
    seller_balance = contract_instance.functions.balanceOf(seller).call({'from': buyer})
    buyer_balance = contract_instance.functions.balanceOf(buyer).call({'from': seller})
    
    # Change tokenId to avoid error
    result = contract_instance.functions.mint(seller, nft.token_id).transact({'from': seller})

    time.sleep(60)
    new_seller_balance = contract_instance.functions.balanceOf(seller).call({'from': buyer})
    assert new_human_0_balance == human_0_balance + 1


@login_required
def bid_accept(request, bid_uuid):
    #
    try:
        #
        contract_address = auction.contract_address
        contract_abi = auction.contract_abi 
        #
        bid = Bid.objects.get(uuid=bid_uuid)
        auction_assets = bid.auction.get_assets()
        auction_assets_nfts = [a.nfts.all() for a in auction_assets]
        user_wallet = request.user.ethereum_wallet_address 
        #
        nftutils = NFTUtils()
        bc_setup = nftutils.set_up_blockchain({
            'seller_ethereum_wallet_address':bid.auction.seller.ethereum_wallet_address,
            'seller_ethereum_wallet_private_key':bid.auction.seller.ethereum_wallet_private_key,
            'network':bid.auction.network, 
            'auction_contract_address':bid.auction.contract_address, 
            'auction_contract_abi':bid.auction.contract_abi
        })
        tx_hash, tx_token = nftutils.web3_mint(
            userAddress=user_wallet,
            tokenURI=nft_metadata_uri,
            eth_json=bc_setup,
        )
        #
        new_purchase = Purchase(commit=False)
        new_purchase.bid_id = bid_id
        new_purchase.tx_hash = tx_hash
        new_purchase.tx_token = tx_token
        new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
        return redirect("nft_detail", nft_id=bid.nft_id)
    #
    return redirect("nft_detail", nft_id=bid.nft_id)


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
