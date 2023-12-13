from Block import Block, UTXO, Transaction
from Node import Node
from Crypting import KeyPair, generateRSAKeyPair, sign
class Client:
    def __init__(self, name:str, node : Node) -> None:
        self.name:str = name
        self.node:Node = node
        key = generateRSAKeyPair()
         
        self.__sk:KeyPair = KeyPair(key.n, 0, key.d) #private
        self.pk:KeyPair = KeyPair(key.n, key.e, 0)
        self.addr:bytes = self.pk.hash()
        self.UTXO:list[UTXO] = []
        self.balance:int = 0
        coinbaseBalance = self.node.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        sg = sign(inputUTXO[0].hash() + outputUTXO[0].hash() + outputUTXO[1].hash())
        self.transaction:Transaction = Transaction(inputUTXO, outputUTXO, sg, self.pk)
        
    def mine(self, block:Block)-> int:
        
        pass
    
    def getTransaction(self) -> Transaction:
        coinbaseBalance = self.node.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        sg = sign(inputUTXO[0].hash() + outputUTXO[0].hash() + outputUTXO[1].hash())
        self.transaction:Transaction = Transaction(inputUTXO, outputUTXO, sg, self.pk)
        return Transaction(inputUTXO, outputUTXO, sg, self.pk)
    pass