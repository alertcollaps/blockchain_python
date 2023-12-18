from array import array
from Block import *
from Crypting import merkle_root, generateRSAKeyPair, sign, Hash

from Client import Client
class Node:
    def __init__(self) -> None:
        self.nodePool:list[Node] = []
        self.lastBlocks = []
        self.currentBlock = Block()
        self.UTXO = [UTXO(b'Coinbase', Block().body.coinbase)]
        
        self.difficalty = 2 ** 2
        self.hashDifficalt = int.to_bytes((2 ** (255)//self.difficalty), 32, byteorder='big') # 2^256 / diff

    
    def setMiner(self, miner: Client):
        self.miner:Client = miner
    def checkBlock(self, block : Block) -> bool:
        hashMerkle = block.getMerkleRoot() # 1. Расчет дерева Меркла
        if (hashMerkle != block.root):     # и проверка
            return False
        
        if (self.hashDifficalt < block.hash): # 2. Если hash больше
            return False
        if (block.hash != block.hashBlock()): # 2. Если хеш не совпадает
            return False
        
        numberBlock = -1 # Если это генезис блок, то как бы предыдущий был под индексом -1
        if len(self.lastBlocks) != 0: # Если блок уже есть
            if (block.prev != self.lastBlocks[len(self.lastBlocks)-1].hash): # 4. Проверка на предыдущий блок
                return False
            if (block.time > self.lastBlocks[len(self.lastBlocks)-1].time): # 5. Проверка времени
                return False
            if (block.body.coinbase == self.lastBlocks[len(self.lastBlocks)-1].body.coinbase - 5): # 5. Проверка времени
                return False
            
            bufferUTXO:list[UTXO] = [] # В конечном итоге должен равен UTXO ноды
            for txs in self.lastBlocks[len(self.lastBlocks)-1].body.tx: # Текущий UTXO в каждой ноде должен равен 
                for input in txs.input:
                    bufferUTXO.append(input)
                
            
            numberBlock = self.lastBlocks[len(self.lastBlocks)-1].height #Получаем номер последнего блока
        else:
            if (block.prev != b''): # 4. Проверка на нулевой предыдущий блок
                return False

        if block.height != (numberBlock+1): # 3. Если порядок следования не совпадает
            return False

        i = 0
        for tx in block.body.tx: # 8. Проверка транзакций
            if i == 0: # Пропускаем 0-ую транзакцию, она была проверена ранее
                i = 1
                continue
            if not tx.checkTransaction():
                return False
        
        self.UTXO = [] # 10. and 11. Добавляем output и удаляем инпуты
        for tx in block.body.tx: # Add
            for output in tx.outputUTXO:
                self.UTXO.append(output)
                
        for tx in block.body.tx: # Remove
            for input in tx.inputUTXO:
                for selfUTXO in self.UTXO:
                    if (input == selfUTXO):
                        self.UTXO.remove(selfUTXO)
                        break
                #raise RuntimeError("Failed find input UTXO in checkBlock")
        
        return True
        
    def getCoinbaseBalance(self)-> int:
        return self.currentBlock.body.coinbase
        
    def getFinalBlock(self, block : Block):
        if not self.checkBlock(block):
            raise RuntimeError("Error check block. Exit.")
        self.lastBlocks.append(block)
        
        self.currentBlock = Block()
        self.currentBlock.height = block.height + 1
        self.currentBlock.prev = block.hash
        self.currentBlock.body.coinbase = block.body.coinbase - 5
        
        
    
    def getTransactionFromNode(self, tx : Transaction) -> str: # Для узлов
        if (not tx.checkTransaction()):
            return "Transacion sign failed"
        removeUTXO:list[UTXO] = [] # Массив UTXO, которые мы удалим
        for inputUTXO in tx.inputUTXO:
            for utxo in self.UTXO:
                if (utxo == inputUTXO):
                    removeUTXO.append(utxo)
                    break
            return "Can't find all UTXO"

        for removeUtxo in removeUTXO: # Если все заявленные отправителем inputUtxo найдены, то удаляем из из пула
            self.UTXO.remove(removeUtxo)
        
        for outputUtxo in tx.outputUTXO: # Добавляем в пул заявленные отправителем outputUTXO
            self.UTXO.append(outputUtxo)
                
        self.currentBlock.addTransaction(tx) # Добавляем транзакцию в текущий блок
        return "Ok"
        
    def addTransaction(self, tx : Transaction) -> str: # Для клиентов
        error = self.getTransactionFromNode(tx) # Проверяем и сохраняем
        if error != "Ok": # Если ошибка, то не пересылаем
            return error
        self.resendTransaction(tx) # Пересылаем всем
        return "Ok"
    
    def resendTransaction(self, tx : Transaction):
        for node in self.nodePool:
            node.getTransactionFromNode(tx)
        
    def resendBlock(self, block : Block):
        for node in self.nodePool:
            node.getFinalBlock(block)
        
    def finalyzeBlock(self): # этот метод мы будем трогать HAND
        coinbaseBalance = self.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        
        tx0:Transaction = self.miner.getTransaction() # Та самая нулевая транзакция
        if (tx0.inputUTXO != inputUTXO or tx0.outputUTXO != outputUTXO): # Проверка, что транзакция соответствует 5 рускоинам
            raise RuntimeError("Miner first transaction failed")
        
        if not tx0.checkSignature(): # Проверка подписи самой транзакции
            raise RuntimeError("Failed check first transaction")
        bufferUTXO:list[UTXO] = []
        for txs in  self.currentBlock.body.tx:
            for output in txs.outputUTXO:
                bufferUTXO.append(output)
            for input in txs.inputUTXO:
                for selfUTXO in bufferUTXO:
                    if selfUTXO == input:
                        bufferUTXO.remove(input)
                        break
        self.currentBlock.body.tx.insert(tx0) # Первая транзакция - это выплата майнеру, поэтому инсерт
        
        genBlock = self.currentBlock
        genBlock.root = genBlock.getMerkleRoot()
        genBlock.setTime() # Устанавливаем время
        nonce = self.miner.mine(genBlock, self.difficalty) # Майнер решает задачу
        self.UTXO = bufferUTXO
        genBlock.nonce = nonce
        
        hashGenBlock = genBlock.hashBlock()
        if (self.hashDifficalt >= hashGenBlock): # Если майнер нас обманул - кидаем ошибку
            raise RuntimeError("Failed mine! Exit.")
        
        
        genBlock.hash = hashGenBlock
        self.lastBlocks.append(genBlock)
        
        self.resendBlock(genBlock)
        # Подготовка нового блока
        self.currentBlock = Block()
        self.currentBlock.height = genBlock.height + 1
        self.currentBlock.prev = genBlock.hash
        self.currentBlock.body.coinbase = genBlock.body.coinbase - 5
        
        
    
    def createGenesisBlock(self):
        
        genBlock = Block()
        coinbaseBalance = self.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.miner.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        
        tx0:Transaction = self.miner.getTransaction() # Та самая нулевая транзакция
        if (tx0.inputUTXO != inputUTXO or tx0.outputUTXO != outputUTXO): # Проверка, что транзакция соответствует 5 рускоинам
            raise RuntimeError("Miner first transaction failed")
        
        if not tx0.checkSignature(): # Проверка подписи самой транзакции
            raise RuntimeError("Failed check first transaction")
        
        genBlock.addTransaction(tx0)
        genBlock.root = genBlock.getMerkleRoot()
        genBlock.setTime() # Устанавливаем время
        nonce = self.miner.mine(genBlock, self.difficalty) # Майнер решает задачу
        
        genBlock.nonce = nonce
        
        hashGenBlock = genBlock.hashBlock()
        if (self.hashDifficalt <= hashGenBlock): # Если майнер нас обманул - кидаем ошибку
            raise RuntimeError("Failed mine! Exit.")
        
        
        genBlock.hash = hashGenBlock
        self.lastBlocks.append(genBlock)
        
        self.resendBlock(genBlock)
        self.UTXO = outputUTXO
        # Подготовка нового блока
        self.currentBlock = Block()
        self.currentBlock.height = genBlock.height + 1
        self.currentBlock.prev = genBlock.hash
        self.currentBlock.body.coinbase = genBlock.body.coinbase - 5
        
    def getHeightBlock(self, height:int)-> Block:
        if height >= 0 and height < len(self.lastBlocks):
            return self.lastBlocks[height]
        return None
        
    def printLastBlocks(self):
        for blocks in self.lastBlocks:
            print(blocks)
    
    def printCurrentUTXO(self):
        for utxo in self.UTXO:
            print(utxo)
        
    def windowNodeMain(self):
        while True:
            print(self, "Меню транзакций\n\
            1. Последние блоки\n\
            2. Вывести имеющиеся UTXO\n\
            3. Вернуться назад\n")
            choose = int(input())
            if choose == 1:
                self.printLastBlocks()
                continue
            elif choose == 2:
                self.printCurrentUTXO()
                continue
            elif choose == 3:
                return
            
            print("Вы ввели некорректное значение")