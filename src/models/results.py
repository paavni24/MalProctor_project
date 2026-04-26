from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DetectionResult:
    filename: str
    is_malware: bool
    probability: float

@dataclass
class EvaluationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float

@dataclass
class DetectionResults:
    results: List[DetectionResult]
    metrics: EvaluationMetrics

    def to_dict(self) -> Dict:
        return {
            "results": [result.__dict__ for result in self.results],
            "metrics": self.metrics.__dict__
        }