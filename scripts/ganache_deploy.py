from brownie import *
import logging

def main():
    acct = accounts.load('development')
    print(acct)
    #ERC721.deploy("My Real Token", "RLT", 18, 1e28, {'from': acct})
    t = acct.deploy(ERC721)
