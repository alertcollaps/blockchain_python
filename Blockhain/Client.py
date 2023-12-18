from Block import Block, UTXO, Transaction
from Crypting import KeyPair, generateRSAKeyPair, sign, Hash
from random import randint

class Client:
    def __init__(self, name:str) -> None:
        self.name:str = name
        
        
        key = generateRSAKeyPair()
         
        self.__sk:KeyPair = KeyPair(key.n, 0, key.d) #private
        self.pk:KeyPair = KeyPair(key.n, key.e, 0)
        self.addr:bytes = self.pk.hash()
        self.UTXO:list[UTXO] = []
        self.balance:int = 0
     
    def setNode(self, node):
        self.node = node
        
    def mine(self, block:Block, difficalty:int)-> int:
        data =  block.height.to_bytes(block.height.bit_length()//8+1) + \
                block.time.to_bytes(block.time.bit_length()//8+1) + \
                block.root + \
                block.prev
        
        hashDifficalt = int.to_bytes((2 ** (255)//difficalty), 32, byteorder='big') # 2^256 / diff
                 
        while True:
            nonce:int = randint(0, 2 ** 32)
            hashVal = Hash(data + nonce.to_bytes(nonce.bit_length()//8+1))
            if hashVal < hashDifficalt:
                return nonce
    
    def getTransaction(self) -> Transaction:
        coinbaseBalance = self.node.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        sg = sign(inputUTXO[0].hash() + outputUTXO[0].hash() + outputUTXO[1].hash(), self.__sk)
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
            height += 1
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

        self.UTXO = utxo
        
        return balance
    
    def __str__(self) -> str:
        return "--------------\n[name]: %s\n[addr]: %s\n--------------" % (self.name, self.addr.hex())
    
    def printUTXO(self):
        i = 0
        for utxo in self.UTXO:
            print("%d." % (i), utxo)
            i += 1
    
    def enterTransaction(self):
        self.printUTXO()
        bufferUTXO:list[UTXO] = []
    
        chooseUTXO:str = input("Select transactions{1, 2, 3 ..etc.}: ")
        indexes = chooseUTXO.split(' ')
        amountChoose = 0
        dataSign = b''
        for index in indexes:
            bufferUTXO.append(self.UTXO[int(index)])
            amountChoose += self.UTXO[int(index)].amount
            dataSign += self.UTXO[int(index)].hash()
            
        addressDST = input("Enter address dest: ")
        
        addr = bytes.fromhex(addressDST)
        
        amount = int(input("Enter amount: "))
        if (amount > amountChoose):
            print("Warning! Вы ввели слишком большую сумму. Возврат...")
            return
        
        outputUTXO:list[UTXO] = [UTXO(addr, amount)]
        dataSign += outputUTXO[0].hash()
        if (amount < amountChoose):
            outputUTXO.append(UTXO(self.addr, amountChoose - amount))
            dataSign += outputUTXO[1].hash()
        
        signTX = sign(dataSign, self.__sk)
        tx = Transaction(bufferUTXO, outputUTXO, signTX, self.pk)
        print("Result sending transaction:", self.node.addTransaction(tx))
        
    
    def windowsClientTransaction(self):
        while True:
            print(self, "Меню транзакций\n\
            1. Выполнить транзакцию\n\
            2. Вывести имеющиеся UTXO\n\
            3. Вернуться назад\n")
            choose = int(input())
            if choose == 1:
                self.enterTransaction()
                continue
            elif choose == 2:
                self.printUTXO()
                continue
            elif choose == 3:
                return
            
            print("Вы ввели некорректное значение")
            
            
        
        
    
    def windowClientMain(self):
        while (True):
            
            print(self, "Меню клиента:\n\
                1. Проверить баланс\n\
                2. Операции с транзакциями\n\
                3. Выход\n")
            
            choose = int(input())
            if choose == 1:
                print("Balance: %d" % (self.calcBalance()))
                continue
            elif choose == 2:
                self.windowsClientTransaction()
                continue
            elif choose == 3:
                return
        
        #TODO Сделать окна для клинта и ноды со свич кейзами
    