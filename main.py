from Blockhain.Crypting import *

keyPair = generateRSAKeyPair()
sg = sign(b'123', keyPair)
print(verify(b'123', sg, keyPair))
