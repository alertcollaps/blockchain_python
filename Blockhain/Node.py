from array import array
from Block import *
import Client
class Node:
    def __init__(self, miner : Client) -> None:
        self.lastBlocks = array(Block, [])
        self.currentBlock = Block()
        self.UTXO = array(UTXO, [])
        self.miner = miner

        
    def addTransaction(self, tx : Transaction):
        self.currentBlock.addTransaction(tx)