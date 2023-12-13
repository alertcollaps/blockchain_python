from array import array
from Block import *
from Crypting import merkle_root
from Client import Client
class Node:
    def __init__(self, miner : Client, nodePool:list, lastBlocks:list[Block] = [], UTXO:list[UTXO]=[UTXO(b'Coinbase', Block().body.coinbase)]) -> None:
        self.nodePool:list[Node] = nodePool
        self.lastBlocks = lastBlocks
        self.currentBlock = Block()
        self.UTXO = UTXO
        self.miner = miner
        self.difficalty = 2 ** 2
        self.hashDifficalt = int.to_bytes((2 ** 256) // self.difficalty, 32, byteorder='big') # 2^256 / diff

    def checkBlock(self, block : Block) -> bool:
        hashMerkle = block.getMerkleRoot() # 1. Расчет дерева Меркла
        if (hashMerkle != block.root):     # и проверка
            return False
        
        if (self.hashDifficalt >= block.hash): # 2. Если hash больше
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

    
        for tx in block.body.tx: # 8. Проверка транзакций
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
                raise RuntimeError("Failed find input UTXO in checkBlock")
        
        return True
        
    def getCoinbaseBalance(self)-> int:
        return self.currentBlock.body.coinbase
        
    def getFinalBlock(self, block : Block):
        if not self.checkBlock(block):
            raise RuntimeError("Error check block. Exit.")
        
        
    
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
        
        pass
    
    def createGenesisBlock(self):
        
        genBlock = Block()
        coinbaseBalance = self.getCoinbaseBalance()
        inputUTXO:list[UTXO] = [UTXO(b'Coinbase', coinbaseBalance)]
        outputUTXO:list[UTXO] = [UTXO(self.addr, 5), UTXO(b'Coinbase', coinbaseBalance-5)]
        
        tx0:Transaction = self.miner.getTransaction() # Та самая нулевая транзакция
        if (tx0.inputUTXO != inputUTXO or tx0.outputUTXO != outputUTXO): # Проверка, что транзакция соответствует 5 рускоинам
            raise RuntimeError("Miner first transaction failed")
        
        if not tx0.checkSignature(): # Проверка подписи самой транзакции
            raise RuntimeError("Failed check first transaction")
        
        genBlock.addTransaction(tx0)
    
        nonce = self.miner.mine(genBlock, self.difficalty) # Майнер решает задачу
        
        genBlock.nonce = nonce
        
        hashGenBlock = genBlock.hashBlock()
        if (self.hashDifficalt >= hashGenBlock): # Если майнер нас обманул - кидаем ошибку
            raise RuntimeError("Failed mine! Exit.")
        
        genBlock.setTime() # Устанавливаем время
        genBlock.hash = hashGenBlock
        self.lastBlocks.append(genBlock)
        
        # Подготовка нового блока
        self.currentBlock.height = genBlock.height + 1
        self.currentBlock.prev = genBlock.hash
        self.currentBlock.body.coinbase = genBlock.body.coinbase - 5
        
        