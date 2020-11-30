from utils.models import *

nodes = Person.nodes.all()
print(nodes)

m=City.nodes.get(name='Moscow')
af = m.ways_to('London')[0][0]