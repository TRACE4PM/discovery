from pydantic import BaseModel


class QualityResult(BaseModel):
    Fitness: dict
    Precision: float
    Generalization: float
    Simplicity: float
