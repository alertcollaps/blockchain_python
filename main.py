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
        return "--------------\n[address]: %s\n[amount]: %d\n--------------" % (self.address, self.amount)

    
    def hash(self) -> bytes:
        from hashlib import sha256
        return sha256(self.to_bytes()).digest()
        
        
    def to_bytes(self) -> bytes:
        return self.address + self.amount.to_bytes()
    
    
    
        
utxo1 = UTXO()
utxo2 = UTXO()

lst1 = [UTXO(None), utxo2]
lst2 = [utxo1, utxo2]

print(lst1 == lst2)