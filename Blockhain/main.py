from Node import Node
from Client import Client
import random

class Main:
    def __init__(self) -> None:
        self.nodePool:list[Node] = []
        self.clientPool:list[Client] = []
    
    def main(self):
        # Создаем ноды
        node1 = Node()
        node2 = Node()
        node3 = Node()
        # Дружим ноды друг с другом
        node1.nodePool = [node2, node3]
        node2.nodePool = [node1, node3]
        node3.nodePool = [node2, node3]

        # Создаем клиентов - майнеров
        miner1 = Client("miner1", node1) # Говорим каждому майнеру, к какой ноде он относится
        miner2 = Client("miner2", node2)
        miner3 = Client("miner3", node3)

        # Создаем клиента
        client1 = Client("client1", node1)

        # Говорим каждой ноде, какой у неё майнер
        node1.miner = miner1
        node2.miner = miner2
        node3.miner = miner3


        self.nodePool = [node1, node2, node3] # Все наши узлы
        self.clientPool = [miner1, miner2, miner3, client1]
        print("0:", node1)
        print("1:",node2)
        print("2:",node3)

        # Create genesis block
        i = random.randint(0, len(self.nodePool)) # Выбор узла
        print("Выбран узел №%d" % i)
        self.nodePool[i].createGenesisBlock()

        self.MainMenu()
        
    
    

    def MainMenu(self):
        while True:
            print("Главное меню:\n\
                    1. Nodes\n\
                    2. Clients\n\
                    3. Start new block\n\
                    4. Exit")
            choose = int(input())
            if choose == 1:
                self.NodeMenu()
                continue
            elif choose == 2:
                self.ClientMenu()
                continue
            elif choose == 3:
                self.startNewBlock()
                continue
            elif choose == 4:
                return
            
            print("Вы ввели некорректное значение")
    
    
    def NodeMenu(self):
        i = 0
        print("Выбери узел:")
        for node in self.nodePool:
            print("[%d]: %s\n" % (i, node))
            i += 1
            
        while True:
            print("3. Вернуться назад")
            choose = int(input())
            if choose >= 0 and choose <= 2:
                self.nodePool[i].windowNodeMain()
                continue
            elif choose == 3:
                return
            
            print("Вы ввели некорректное значение")
    
    def ClientMenu(self):
        i = 0
        print("Выбери клиента:")
        for client in self.clientPool:
            print("[%d]: %s\n" % (i, client))
            i += 1
            
        while True:
            print("4. Вернуться назад")
            choose = int(input())
            if choose >= 0 and choose <= 3:
                self.clientPool[i].windowClientMain()
                continue
            elif choose == 4:
                return
            
            print("Вы ввели некорректное значение")
    
    def startNewBlock(self):
        i = random.randint(0, len(self.nodePool)) # Выбор узла
        print("Выбран узел №%d" % i)
        self.nodePool[i].finalyzeBlock()