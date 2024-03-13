
from pydantic import BaseModel

class MiningResult(BaseModel):
    Fitness: dict
    Precision: float
    Generalization: float
    Simplicity: float