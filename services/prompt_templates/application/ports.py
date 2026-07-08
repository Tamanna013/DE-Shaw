from typing import Protocol, List
from services.prompt_templates.domain.entities import PromptTemplate

class PromptTemplateRepositoryPort(Protocol):
    def get_template(self, name: str, version: str) -> PromptTemplate:
        ...
        
    def list_templates(self) -> List[PromptTemplate]:
        ...
