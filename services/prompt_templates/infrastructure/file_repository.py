import os
import importlib.util
from typing import List
from services.prompt_templates.domain.entities import PromptTemplate
from services.prompt_templates.domain.exceptions import TemplateNotFoundError
from services.prompt_templates.application.ports import PromptTemplateRepositoryPort

class FileBasedPromptTemplateRepository(PromptTemplateRepositoryPort):
    def __init__(self, templates_dir: str = None):
        if not templates_dir:
            # Default to the infrastructure/templates dir relative to this file
            self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        else:
            self.templates_dir = templates_dir
            
        self._cache = {}

    def _load_schema_class(self, schema_path: str, template_name: str, version: str):
        # Dynamically load the Pydantic schema class from the co-located file
        spec = importlib.util.spec_from_file_location("dynamic_schema", schema_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # We expect a class named e.g. FailureRootCauseV1Schema
        # Convert snake_case to PascalCase
        parts = template_name.split("_") + [version, "schema"]
        expected_class_name = "".join(p.capitalize() for p in parts)
        
        # For simplicity in finding it if name mapping isn't perfect, just find the first BaseModel subclass
        from pydantic import BaseModel
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseModel) and attr is not BaseModel:
                return attr
                
        raise ImportError(f"Could not find a Pydantic BaseModel in {schema_path}")

    def get_template(self, name: str, version: str) -> PromptTemplate:
        cache_key = f"{name}_{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        jinja_path = os.path.join(self.templates_dir, f"{name}_{version}.jinja2")
        schema_path = os.path.join(self.templates_dir, f"{name}_{version}.schema.py")
        
        if not os.path.exists(jinja_path):
            raise TemplateNotFoundError(f"Template {name} {version} not found at {jinja_path}")
            
        if not os.path.exists(schema_path):
            raise TemplateNotFoundError(f"Schema for {name} {version} not found at {schema_path}")
            
        with open(jinja_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        schema_class = self._load_schema_class(schema_path, name, version)
        
        template = PromptTemplate(
            name=name,
            version=version,
            template_content=content,
            input_schema=schema_class
        )
        
        self._cache[cache_key] = template
        return template

    def list_templates(self) -> List[PromptTemplate]:
        templates = []
        for file in os.listdir(self.templates_dir):
            if file.endswith(".jinja2"):
                # Parse name_v1.jinja2
                basename = file[:-7]
                parts = basename.rsplit("_", 1)
                if len(parts) == 2:
                    name, version = parts
                    try:
                        templates.append(self.get_template(name, version))
                    except Exception:
                        pass
        return templates
