from Node import Node
from Client import Client
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

# Говорим каждой ноде, какой у неё майнер
node1.miner = miner1
node2.miner = miner2
node3.miner = miner3


