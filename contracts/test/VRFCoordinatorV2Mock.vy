# SPDX-License-Identifier: MIT
# @version ^0.3.7

MAX_ARRAY_SIZE: constant(uint256) = 10
BASE_FEE: immutable(uint96)
GAS_PRICE_LINK: immutable(uint96)

dummy_address: address
nextRequestId: uint256
numWords: uint32

event RandomWordsFulfilled:
    requestId: indexed(uint256)
    outputSeed: uint256
    payment: uint96
    success: bool

event RandomWordsRequested:
    keyHash: indexed(bytes32)
    requestId: uint256
    preSeed: uint256
    subId: indexed(uint64)
    minimumRequestConfirmations: uint16
    callbackGasLimit: uint32
    numWords: uint32
    sender: indexed(address)

event SubscriptionCreated:
    subId: indexed(uint64)
    owner: address

@external
def __init__(base_fee: uint96, gas_price_link: uint96):
    BASE_FEE = base_fee
    GAS_PRICE_LINK = gas_price_link
    self.dummy_address = msg.sender
    self.nextRequestId = 1

@external
def fulfillRandomWords(requestId: uint256, consumer: address):
    """Returns an array of random numbers. In this mock contract, we ignore the requestId and consumer. 
    Args:
        requestId (uint256): The request Id number
        consumer (address): The consumer address to 
    """
    assert requestId >= self.nextRequestId, "nonexistent request"  
    
    # Default to 77 as a mocking example
    words: DynArray[uint256, MAX_ARRAY_SIZE] = []
    for i in range(MAX_ARRAY_SIZE):
        if convert(i, uint32) >= self.numWords:
            break
        words.append(77)
    self.fulfillRandomWordsWithOverride(requestId, consumer, words)

@external
def fulfillRandomWordsWithGivenWords(requestId: uint256, consumer: address, words: DynArray[uint256, MAX_ARRAY_SIZE]):
    self.fulfillRandomWordsWithOverride(requestId, consumer, words)

@internal
def fulfillRandomWordsWithOverride(requestId: uint256, consumer: address, words: DynArray[uint256, MAX_ARRAY_SIZE]):
    """Returns an array of random numbers. In this mock contract, we ignore the requestId and consumer. 
    Args:
        requestId (uint256): The request Id number
        consumer (address): The consumer address to 
        words (uint256[1]): The array of random numbers, we are defaulting to 1 for vyper
    """    
    call_data: Bytes[3236] = _abi_encode(requestId, words, method_id=method_id("rawFulfillRandomWords(uint256,uint256[])"))
    response: Bytes[32] = raw_call(consumer, call_data, max_outsize=32)
    log RandomWordsFulfilled(requestId, requestId, 0, True)

@external
def requestRandomWords(key_hash: bytes32, sub_id: uint64, minimum_request_confirmations: uint16, callback_gas_limit: uint32, num_words: uint32) -> uint256:
    self.nextRequestId += 1
    self.numWords = num_words
    log RandomWordsRequested(key_hash, self.nextRequestId, 0, sub_id, minimum_request_confirmations, callback_gas_limit, num_words, msg.sender)
    return self.nextRequestId

@external
def fundSubscription(subId: uint64, amount: uint96):
    """Funds a subscription. Keeping blank for the mock.
    Args:
        subId (uint64): The subscription Id number
        amount (uint96): The amount to fund the subscription
    """    
    pass

@external
def addConsumer(subId: uint64, consumer: address):
    """Adds consumer to subscription. Keeping blank for mock. 
    Args:
        subId (uint64): The subId
        consumer (address): Consumer / contract address that will be getting random numbers
    """     
    pass

@external
def createSubscription():
    """
    Create a subscription. Keeping blank for mock. 
    """     
    log SubscriptionCreated(0, msg.sender)


@external 
@view 
def getSubscription(subId: uint64) -> (uint96, uint64, address, address[1]):
    """
    Get a subscription. Keeping blank for mock. 
    """  
    blank_addresses: address[1] = [self.dummy_address]
    # Balance, reqCount, owner, consumers   
    return (10000000000000000000, 0, self.dummy_address, blank_addresses)