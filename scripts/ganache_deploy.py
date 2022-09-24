from brownie import *
import logging

def main():
    t = accounts[0].deploy(ERC721)
