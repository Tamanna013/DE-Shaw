from dataclasses import dataclass
from typing import Type
from pydantic import BaseModel

@dataclass
class PromptTemplate:
    name: str
    version: str
    template_content: str
    input_schema: Type[BaseModel]
