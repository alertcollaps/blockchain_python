from hashlib import sha256
from Crypto.PublicKey import RSA

class KeyPair:
        def __init__(self, n = 0, e = 0, d = 0) -> None:
                self.n = n
                self.e = e
                self.d = d

def generateRSAKeyPair()-> KeyPair:
        keyPair = RSA.generate(bits=1024)
        return KeyPair(keyPair.n, keyPair.e, keyPair.d)

def Hash(data):
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