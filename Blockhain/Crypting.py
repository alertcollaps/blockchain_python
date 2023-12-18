from hashlib import sha256
from Crypto.PublicKey import RSA

class KeyPair:
        def __init__(self, n = 0, e = 0, d = 0) -> None:
                self.n = n
                self.e = e
                self.d = d
                
        def hash(self) -> bytes:
                return Hash(self.to_bytes())
                
        def to_bytes(self) -> bytes:
                return self.n.to_bytes(self.n.bit_length()//8) + self.e.to_bytes(self.e.bit_length()//8+1) + self.d.to_bytes(self.d.bit_length()//8)

def generateRSAKeyPair()-> KeyPair:
        keyPair = RSA.generate(bits=1024)
        return KeyPair(keyPair.n, keyPair.e, keyPair.d)

def Hash(data:bytes):
        hash = sha256()
        hash.update(data)
        return hash.digest()

def sign(data : bytes, keyPair : KeyPair) -> int:
        hash = int.from_bytes(sha256(data).digest(), byteorder='big')
        signature = pow(hash, keyPair.d, keyPair.n)
        return signature

def verify(data : bytes, sign : int, keyPair : KeyPair):
        hash = int.from_bytes(sha256(data).digest(), byteorder='big')
        hashFromSignature = pow(sign, keyPair.e, keyPair.n)
        return hash == hashFromSignature

def merkle_root(lst):
    sha256d = lambda x: sha256(sha256(x).digest()).digest()
    hash_pair = lambda x, y: sha256d(x[::-1] + y[::-1])[::-1]

    if len(lst) == 1: return lst[0]
    
    if len(lst) % 2 == 1:
        lst.append(lst[-1])
    return merkle_root([ hash_pair(x, y) 
        for x, y in zip(*[iter(lst)] * 2) ])