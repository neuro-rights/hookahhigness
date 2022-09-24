from brownie import *
import loggingdef main():
    t = accounts[0].deploy(ERC721)
