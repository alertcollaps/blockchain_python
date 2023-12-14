from Block import Block, UTXO, Transaction
from Node import Node
from Crypting import KeyPair, generateRSAKeyPair, sign, Hash
from random import randint
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
        
    def mine(self, block:Block, difficalty:int)-> int:
        data =  block.height.to_bytes() + \
                block.time.to_bytes() + \
                block.root + \
                block.prev
        
        hashDifficalt = int.to_bytes((2 ** 256) // difficalty, 32, byteorder='big') # 2^256 / diff
                 
        while True:
            nonce:int = randint(0, 2 ** 32)
            hashVal = Hash(data + nonce)
            if hashVal < hashDifficalt:
                return nonce
    
    def getTransaction(self) -> Transaction:
        coinbaseBalance = self.node.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        sg = sign(inputUTXO[0].hash() + outputUTXO[0].hash() + outputUTXO[1].hash())
        self.transaction:Transaction = Transaction(inputUTXO, outputUTXO, sg, self.pk)
        return Transaction(inputUTXO, outputUTXO, sg, self.pk)
    
    def getBlock(self, height:int)-> Block:
        return self.node.getHeightBlock(height)
    
    def calcBalance(self) -> int:
        height = 0
        balance:int = 0
        utxo:list[UTXO] = []
        while True:
            block:Block = self.getBlock(height)
            if block == None:
                break
            for tx in block.body.tx:
                for input in tx.inputUTXO: # Если находим input - то удаляем
                    if input.address == self.addr:
                        utxo.remove(input)
                for output in tx.outputUTXO:
                    if output.address == self.addr: # Если находим output - то прибавляем
                        utxo.append(output)
        
        for utx in utxo:
            balance += utx.amount

        return balance
    
    def __str__(self) -> str:
        return "--------------\n[name]: %s\n[addr]: %s\n--------------" % (self.name, self.addr.hex())
    
    def windowClient(self):
        pass
        #TODO Сделать окна для клинта и ноды со свич кейзами