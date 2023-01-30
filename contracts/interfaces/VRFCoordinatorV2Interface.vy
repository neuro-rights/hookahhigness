# SPDX-License-Identifier: MIT
# @version ^0.3.7

@external
@view
def getRequestConfig() -> (uint16, uint32, Bytes[1000]):
    return (0, 0, b"\x00")

@external
def requestRandomWords(keyHash: bytes32, subId: uint64,minimumRequestConfirmations: uint16,callbackGasLimit: uint32,numWords: uint32) -> uint256:
    return 0

@external
def createSubscription() -> uint64:
    return 0