from array import array
from Crypting import Hash
from Crypting import KeyPair, verify
class UTXO:
    def __init__(self, address : bytes = None, amount : int = 0) -> None:
        self.address = address
        self.amount = amount

        

class Transaction:
    
    
    def __init__(self, inputUTXO:list[UTXO], outputUTXO:list[UTXO], sign:int, pk:KeyPair) -> None:
        self.inputUTXO = inputUTXO
        self.outputUTXO = outputUTXO
        self.sign = sign
        self.pk = pk
    
    def checkTransaction(self) -> bool:
        addr = Hash(self.pk)
        buffer = b''
        inputAmount = 0
        outputAmount = 0
        for input in self.inputUTXO:
            if (input.address != addr): # Если отправитель в инпуте написал другого участника - блокируем
                return False
            buffer += input.address + input.amount.to_bytes()
            inputAmount += input.amount
        
        for output in self.outputUTXO:
            buffer += output.address + output.amount.to_bytes()
            outputAmount += output.amount
            
        if inputAmount != outputAmount: # Если значения входов и выходов не совпали - блокируем
            return False
        
        if verify(buffer, self.sign, self.pk): # Если подпись не подошла - блокируем
            return False
        
        return True

class BlockBody:
    def __init__(self, coinbase=1000000, tx:list[Transaction] = []) -> None:
        self.coinbase = coinbase
        self.tx = tx
        
    
        

class Block:
    def __init__(self, height=0, prev=b'', body=BlockBody()) -> None:
        self.height = height
        self.time = 0
        self.root = b''
        self.prev = prev
        self.nonce = 0
        self.hash = b''
        self.body = body
    
    def addTransaction(self, tx : Transaction):
        self.body.tx.append(tx)
        
    