from dataclasses import dataclass, field
from typing import Optional

from jawa.constants import MethodReference

from porth.porth import Contract


@dataclass
class Procedure:
    name: str
    local_memory: int
    method_ref: MethodReference
    contract: Contract
