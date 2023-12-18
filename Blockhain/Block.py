from array import array
from Crypting import Hash
from Crypting import KeyPair, verify, merkle_root
from datetime import datetime
class UTXO:
    def __init__(self, address : bytes = None, amount : int = 0) -> None:
        self.address = address
        self.amount = amount
    
    def __eq__(self, __value: object) -> bool:
        try:
            return self.address == __value.address and self.amount == __value.amount
        except:
            return False
        
    def __str__(self) -> str:
        return "--------------\n[address]: %s\n[amount]: %d\n--------------" % (self.address.hex(), self.amount)

    def hash(self) -> bytes:
        from hashlib import sha256
        return sha256(self.to_bytes()).digest()
        
        
    def to_bytes(self) -> bytes:
        return self.address + self.amount.to_bytes(self.amount.bit_length()//8 + 1)

        

class Transaction:
    
    
    def __init__(self, inputUTXO:list[UTXO], outputUTXO:list[UTXO], sign:int, pk:KeyPair) -> None:
        self.inputUTXO = inputUTXO
        self.outputUTXO = outputUTXO
        self.sign = sign
        self.pk = pk
    
    def hashTransaction(self):
        data:bytes = b''
        for input in self.inputUTXO:
            data += input.hash()
        for output in self.outputUTXO:
            data += output.hash()
        
        data += self.sign.to_bytes(self.sign.bit_length()//8+1) +\
                self.pk.n.to_bytes(self.pk.n.bit_length()//8+1) + self.pk.e.to_bytes(self.pk.e.bit_length()//8+1)
        
        return Hash(data)

    
    def checkSignature(self) -> bool:
        inputAmount = 0
        outputAmount = 0
        buffer = b''
        for input in self.inputUTXO:
            buffer += input.hash()
            inputAmount += input.amount
            
        for output in self.outputUTXO:
            buffer += output.hash()
            outputAmount += output.amount
            
        if inputAmount != outputAmount: # Если значения входов и выходов не совпали - блокируем
            return False
        
        return verify(buffer, self.sign, self.pk) # Если подпись не подошла - блокируем
        
        
    def checkTransaction(self) -> bool:
        addr = Hash(self.pk.to_bytes())
        buffer = b''
        inputAmount = 0
        outputAmount = 0
        for input in self.inputUTXO:
            if (input.address != addr): # Если отправитель в инпуте написал другого участника - блокируем
                return False
        
        for output in self.outputUTXO:
            buffer += output.address + output.amount.to_bytes()
            outputAmount += output.amount
            
        if inputAmount != outputAmount: # Если значения входов и выходов не совпали - блокируем
            return False
        
        return verify(buffer, self.sign, self.pk) # Если подпись не подошла - блокируем
       

class BlockBody:
    def __init__(self, coinbase=1000000, tx:list[Transaction] = []) -> None:
        self.coinbase = coinbase
        self.tx = tx
        
    
        

class Block:
    def __init__(self, height=0, prev=b'', body=BlockBody()) -> None:
        self.height = height
        self.time = int(datetime.now().timestamp())
        self.root = b''
        self.prev = prev
        self.nonce = 0
        self.hash = b''
        self.body = body
        
    
    def addTransaction(self, tx : Transaction):
        self.body.tx.append(tx)
    
    def setTime(self):
        self.time = int(datetime.now().timestamp())
    
    
    def getMerkleRoot(self): # Рассчитать корень дерева Меркла. Удобно
        listHashes:list[bytes] = []
        for tx in self.body.tx:
            listHashes.append(tx.hashTransaction())
        return merkle_root(listHashes)
    
    def hashBlock(self)-> bytes:
        self.root = self.getMerkleRoot()
        
        data =  self.height.to_bytes(self.height.bit_length()//8+1) + \
                self.time.to_bytes(self.time.bit_length()//8+1) + \
                self.root + \
                self.prev + \
                self.nonce.to_bytes(self.nonce.bit_length()//8+1)
                    
        #self.hash = Hash(data)            # Лучше вручную устанавливать новый хеш
        return Hash(data)  
        
    
    def __str__(self) -> str:
        return "--------------\n[height]: %d\n[time]: %d\n[root]: %s\n[prev]: %s\n[nonce]: %d\n[hash]: %s\n--------------" % \
            (self.height, self.time, self.root.hex(), self.prev.hex(), self.nonce, self.hash.hex())
            
    