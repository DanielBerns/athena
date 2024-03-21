class Actor(Protocol):
    @property
    def frequency(self) -> int:
        ...

    def update(self, index: int) -> "Actor":
        ...

    
class Node:
    def __init__(self, factory: Callable[[], Actor]) -> None:
        self._actor: Actor = factory()
    
    @property
    def actor(self) -> Actor:
        return self._actor

    @actor.setter    
    def actor(self, value: Actor) -> None:
        self._actor = value

    def update(self, index: int) -> "Node":
        self.actor = self.actor.update(index)        
        return self
            
class FirstNode:
    def __init__(self) -> None:
        pass
    
    def execute(self, index: int) -> "Node":
        





class Actor(Protocol):
    def update(self, node: 'Node', text: str) -> None:
        ...

        
class FirstActor:
    def __init__(self) -> None:
        pass
    
    def get_next_actor(self) -> Actor:
        return NextActor()
    
    def update(self, node: Node, text: str) -> None:
        node.table = defaultdict(Node)
        actor = self.get_next_actor()
        actor.update(node, text)
        node.actor = actor
    
        
class Node:
    
    def __init__(self, first_actor: Actor):
        self._frequency: int = 0
        self._table: Optional[DefaultDict[int, 'Node']] = None
        self._actor: Actor = first_actor
    
    @property
    def actor(self) -> Actor:
        return self._actor
    
    @actor.setter
    def actor(self, value: Actor) -> None:
        self._actor = value
        
    def update(self, text: str) -> None:
        self.actor.update(self, text)
