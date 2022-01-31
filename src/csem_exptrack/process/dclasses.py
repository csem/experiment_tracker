from datetime import datetime
from dataclasses import dataclass

@dataclass
class ExperimentMetadata():
    Path:
    run: int
    time: datetime
 