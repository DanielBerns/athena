from typing import Protocol

class Stage(Protocol):
    def write(self, message: Dict[str, str]) -> None:
        ...
        
    def execute(self) -> None:
        ...
    
    @property
    def next_stage(self) -> Stage:
        ...
        
      
class Pipeline:
       
    
    
        
