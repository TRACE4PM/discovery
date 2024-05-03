from pydantic import BaseModel


class QualityResult(BaseModel):
    Fitness: dict
    Precision: float
    Generalization: float
    Simplicity: float


class HeuristicParameters(BaseModel):
    none = ""
    Dependency = "Dependency Threshold"
    And = "And Threshold"
    LoopTwo = "Loop Two Threshold"
